#!/usr/bin/env python3
"""
openFDA → BigQuery marts (event-grain) — N=3,000, the upstream of the Fabric pipeline.

Pulls real openFDA FAERS drug-event reports (6 closed monthly partitions, 500 each =
3,000 reports) and shapes them into the EXACT contract the deployed Fabric Direct Lake
model + report bind to:
    fact_adverse_events   (grain = safetyreportid)
    dim_drug · dim_reaction
    mart_drug_safety_kpis (grain = primary_drug — what the report visuals read)
then loads them into BigQuery `healthcare_analytics` (--replace). The Fabric pipeline
(openfda_fabric_pipeline.py) takes it from BigQuery → OneLake Delta → model → report.

Auth: GOOGLE_APPLICATION_CREDENTIALS = bchan-genai-deploy SA key.
Run:  python pipeline/build_openfda_marts.py
"""
import hashlib
import json
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

API = "https://api.fda.gov/drug/event.json"
PROJECT = "bchan-genai-lab"
DATASET = "healthcare_analytics"
INGEST_TS = "2026-06-13 00:00:00"          # deterministic stamp
MONTHS = [("20251001", "20251031"), ("20251101", "20251130"), ("20251201", "20251231"),
          ("20260101", "20260131"), ("20260201", "20260228"), ("20260301", "20260331")]


def pull() -> list[dict]:
    rows = []
    for s, e in MONTHS:
        q = urllib.parse.urlencode({"search": f"receivedate:[{s}+TO+{e}]", "limit": 500}, safe="+[]:")
        with urllib.request.urlopen(f"{API}?{q}", timeout=60) as r:
            rows += json.load(r).get("results", [])
        time.sleep(1)
    return rows


def primary_drug(ev: dict) -> str:
    for d in ev.get("patient", {}).get("drug", []) or []:
        name = (d.get("openfda", {}).get("generic_name") or [None])[0] or d.get("medicinalproduct")
        if name:
            return name.strip().upper()
    return "UNKNOWN"


def md5(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()


def transform(events: list[dict]):
    fact, drugs, reactions = [], set(), set()
    for ev in events:
        rxn = [r.get("reactionmeddrapt") for r in ev.get("patient", {}).get("reaction", []) or [] if r.get("reactionmeddrapt")]
        d = str(ev.get("receivedate") or "")
        pd = primary_drug(ev)
        drugs.add(pd)
        reactions.update(rxn)
        fact.append({
            "safetyreportid": ev.get("safetyreportid"),
            "received_date": f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else None,
            "primary_drug": pd,
            "is_serious": ev.get("serious") == "1",
            "n_drugs": len(ev.get("patient", {}).get("drug", []) or []),
            "n_reactions": len(rxn),
            "reactions": ";".join(rxn),
            "occurcountry": ev.get("occurcountry"),
            "ingest_ts": INGEST_TS,
        })
    dim_drug = [{"drug_id": md5(d), "drug_name": d} for d in sorted(drugs)]
    dim_reaction = [{"reaction_id": md5(r), "reaction_name": r} for r in sorted(reactions)]

    # mart_drug_safety_kpis — per primary_drug
    by = defaultdict(list)
    for f in fact:
        by[f["primary_drug"]].append(f)
    mart = []
    for drug, fs in by.items():
        rxset, countries, dates, tot_rxn, serious = set(), set(), [], 0, 0
        for f in fs:
            rxset.update(x for x in f["reactions"].split(";") if x)
            if f["occurcountry"]:
                countries.add(f["occurcountry"])
            if f["received_date"]:
                dates.append(f["received_date"])
            tot_rxn += f["n_reactions"]
            serious += 1 if f["is_serious"] else 0
        n = len(fs)
        window = (date.fromisoformat(max(dates)) - date.fromisoformat(min(dates))).days if dates else 0
        mart.append({
            "primary_drug": drug, "total_reports": n, "serious_reports": serious,
            "serious_rate": round(serious / n, 4), "distinct_reactions": len(rxset),
            "total_reaction_events": tot_rxn, "reactions_per_report": round(tot_rxn / n, 2),
            "countries_reporting": len(countries),
            "first_report_date": min(dates) if dates else None,
            "last_report_date": max(dates) if dates else None,
            "reporting_window_days": window,
        })
    # conformed dims + a reaction bridge (many-to-many done right) — the full star
    dim_date = [{"date_key": d, "date": d, "year": int(d[:4]), "month": int(d[5:7])}
                for d in sorted({f["received_date"] for f in fact if f["received_date"]})]
    dim_country = [{"country_key": c, "country": c}
                   for c in sorted({f["occurcountry"] for f in fact if f["occurcountry"]})]
    bridge = [{"safetyreportid": f["safetyreportid"], "reaction_id": md5(r)}
              for f in fact for r in set(f["reactions"].split(";")) if r]

    return {"fact_adverse_events": fact, "dim_drug": dim_drug, "dim_reaction": dim_reaction,
            "dim_date": dim_date, "dim_country": dim_country,
            "bridge_report_reaction": bridge, "mart_drug_safety_kpis": mart}


def load_bq(table: str, rows: list[dict]):
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
        path = f.name
    subprocess.run([
        "bq", f"--project_id={PROJECT}", "load", "--replace",
        "--source_format=NEWLINE_DELIMITED_JSON", "--autodetect",
        f"{DATASET}.{table}", path,
    ], check=True, capture_output=True, text=True)


def main():
    events = pull()
    marts = transform(events)
    for t, rows in marts.items():
        load_bq(t, rows)
        print(f"  loaded {DATASET}.{t}: {len(rows)} rows")
    print(f"\nN = {len(events)} reports → fact {len(marts['fact_adverse_events'])} · "
          f"drugs {len(marts['dim_drug'])} · reactions {len(marts['dim_reaction'])} · "
          f"mart {len(marts['mart_drug_safety_kpis'])}")


if __name__ == "__main__":
    main()
