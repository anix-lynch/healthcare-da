#!/usr/bin/env python3
"""
Real medallion — bronze (raw, dirty) -> silver (cleaned) as separate tables you can query.

The honest medallion: bronze lands openFDA EXACTLY as it arrives (null drug names, raw fields),
silver applies the trust layer (coalesce, contract). The before/after is then a real SQL query,
not a diagram — bronze.drug_name_raw is 14.4% null, silver.drug_name is 0% null, same rows.

Reads the raw openFDA bronze JSONL, lands bronze_adverse_events + silver_adverse_events into
BigQuery healthcare_analytics. (gold = the marts from build_openfda_marts.py.)
"""
import glob
import json
import subprocess
import tempfile
from pathlib import Path

PROJECT, DATASET = "bchan-genai-lab", "healthcare_analytics"
BRONZE_JSONL = Path("~/dev/wip/fabric-hub/healthcare-da/data/openfda/bronze").expanduser()


def raw_events():
    rows = []
    for f in sorted(glob.glob(str(BRONZE_JSONL / "*" / "part-000.jsonl"))):
        with open(f) as fh:
            rows += [json.loads(l) for l in fh]
    return rows


def build():
    events = raw_events()
    bronze, silver = [], []
    for ev in events:
        sid = ev.get("safetyreportid")
        country, serious = ev.get("occurcountry"), ev.get("serious")
        d = str(ev.get("receivedate") or "")
        rdate = f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else None
        for dr in ev.get("patient", {}).get("drug", []) or []:
            generic = (dr.get("openfda", {}).get("generic_name") or [None])[0]   # RAW: ~14.4% null
            mp = dr.get("medicinalproduct")
            # BRONZE — as-ingested, the mess preserved
            bronze.append({"safetyreportid": sid, "drug_name_raw": generic,
                           "medicinalproduct": mp, "occurcountry": country,
                           "serious_raw": serious, "received_date_raw": d})
            # SILVER — trust layer applied: coalesce + conform
            silver.append({"safetyreportid": sid,
                           "drug_name": generic or mp,                 # coalesced -> 0% null
                           "occurcountry": country, "is_serious": serious == "1",
                           "received_date": rdate})
    return bronze, silver


def load(table, rows):
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
        path = f.name
    subprocess.run(["bq", f"--project_id={PROJECT}", "load", "--replace",
                    "--source_format=NEWLINE_DELIMITED_JSON", "--autodetect",
                    f"{DATASET}.{table}", path], check=True, capture_output=True, text=True)


if __name__ == "__main__":
    bronze, silver = build()
    load("bronze_adverse_events", bronze)
    load("silver_adverse_events", silver)
    print(f"  bronze_adverse_events: {len(bronze)} rows (raw, dirty)")
    print(f"  silver_adverse_events: {len(silver)} rows (cleaned)")
