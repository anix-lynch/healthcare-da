#!/usr/bin/env python3
"""Live contract gate — the trust layer as CODE, not a hand-authored proof.

Reads the medallion bronze + silver JSONL, enforces contracts/data_contract.yml
(PASS/WARN/FAIL), routes FAIL rows to a quarantine table, runs a volume + serious-rate
anomaly check against a rolling baseline, and writes code-generated proof artifacts.

Exits non-zero on any FAIL-level violation so a pipeline/CI step blocks silver/gold/the
semantic model from building on bad data. Dashboards and the AI agent read only the
post-gate (silver/gold) layer — never raw bronze.

Run:  python3 pipeline/run_contract_gate.py
"""
import argparse
import json
import sys
import pathlib
import datetime

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTRACT = ROOT / "contracts/data_contract.yml"
BRONZE = ROOT / "data/bronze_adverse_events.jsonl"
SILVER = ROOT / "data/silver_adverse_events.jsonl"
QUARANTINE = ROOT / "data/quarantine_adverse_events.jsonl"
BASELINE = ROOT / "proof/baseline.json"
QUALITY_REPORT = ROOT / "proof/quality_report.json"
TRUST_REDUCTION = ROOT / "proof/trust_issues_reduction.json"
ANOMALY_REPORT = ROOT / "proof/anomaly_report.json"
GATE_RUN_LOG = ROOT / "proof/gate_run_log.jsonl"

# contract field name -> the actual column materialized in the silver fact.
# reaction_pt is modeled in dim_reaction (not the fact grain), so it is reported, not enforced here.
FIELD_MAP = {
    "safetyreportid": "safetyreportid",
    "receivedate": "received_date",
    "drug_name": "drug_name",
    "occurcountry": "occurcountry",
    "serious": "is_serious",
    "reaction_pt": None,  # not in fact grain -> noted, not enforced
}


def load_jsonl(path):
    if not path.exists():
        return []
    with open(path) as fh:
        return [json.loads(line) for line in fh if line.strip()]


def is_null(v):
    return v is None or (isinstance(v, str) and v.strip() == "")


def valid_date(v):
    if is_null(v):
        return False
    try:
        datetime.date.fromisoformat(str(v))
        return True
    except ValueError:
        return False


def grain_uniqueness(contract, silver):
    """Grain observability: (safetyreportid, drug_name) duplicates = FAERS multi-entry reports
    (a drug listed more than once on one report). Real FAERS characteristic, NOT corruption —
    flagged as WARN and retained (dropping them would change N and break downstream coherence)."""
    keys = contract.get("grain_key")
    if not keys:
        return None
    seen, dups = set(), 0
    for r in silver:
        k = tuple(r.get(c) for c in keys)
        if k in seen:
            dups += 1
        seen.add(k)
    return {"field": "grain_key", "status": "WARN" if dups else "PASS",
            "composite": keys, "duplicate_rows": dups, "severity": "WARN",
            "detail": "FAERS multi-entry (drug listed >1x per report); retained, not corruption"}


def enforce(contract, silver):
    """Return (results, quarantine_rows). results = per-field verdict list."""
    n = len(silver)
    results, quarantine = [], []
    fail_row_ids = set()

    gk = grain_uniqueness(contract, silver)
    if gk:
        results.append(gk)

    for fname, rule in contract["fields"].items():
        col = FIELD_MAP.get(fname, fname)
        sev = rule.get("on_violation", "WARN")

        if col is None:  # contract field not materialized in the fact
            results.append({"field": fname, "status": "NOTE",
                            "detail": "modeled in dim_reaction, not enforced on fact grain"})
            continue

        present = sum(1 for r in silver if not is_null(r.get(col)))
        null_pct = round(100 * (n - present) / n, 2) if n else 0.0

        # date validity for the date field
        if rule.get("type") == "date":
            bad = [r for r in silver if not valid_date(r.get(col))]
            null_pct = round(100 * len(bad) / n, 2) if n else 0.0

        max_null = rule.get("max_null_pct", 0.0 if rule.get("required") else 100.0)
        violated = null_pct > max_null

        # uniqueness check (primary key)
        dup_violation = False
        if rule.get("unique"):
            seen, dups = set(), 0
            for r in silver:
                v = r.get(col)
                if v in seen:
                    dups += 1
                seen.add(v)
            dup_violation = dups > 0

        status = "PASS"
        if violated or dup_violation:
            status = sev  # FAIL or WARN per contract
            if sev == "FAIL":
                for r in silver:
                    bad_null = is_null(r.get(col)) if rule.get("type") != "date" else not valid_date(r.get(col))
                    if bad_null and r.get("safetyreportid") not in fail_row_ids:
                        fail_row_ids.add(r.get("safetyreportid"))
                        quarantine.append({**r, "violation_field": fname,
                                           "violation_reason": f"{fname} null/invalid (FAIL-level)"})

        results.append({"field": fname, "status": status, "null_pct": null_pct,
                        "max_null_pct": max_null, "unique_violation": dup_violation,
                        "severity": sev})
    return results, quarantine


def issue_reduction(bronze, silver):
    """Aggregate pre-gate vs post-gate issue rate across concrete failure modes."""
    nb = len(bronze) or 1
    ns = len(silver) or 1

    # mode 1: null drug identifier (bronze raw generic_name) -> silver coalesced
    pre_drug_null = sum(1 for r in bronze if is_null(r.get("drug_name_raw")))
    post_drug_null = sum(1 for r in silver if is_null(r.get("drug_name")))
    # mode 2: missing/invalid serious flag
    pre_serious_bad = sum(1 for r in bronze if is_null(r.get("serious_raw")))
    post_serious_bad = sum(1 for r in silver if r.get("is_serious") is None)
    # mode 3: invalid received date
    post_date_bad = sum(1 for r in silver if not valid_date(r.get("received_date")))

    pre_issues = pre_drug_null + pre_serious_bad
    post_issues = post_drug_null + post_serious_bad + post_date_bad
    return {
        "n_records": len(silver),
        "failure_modes": {
            "null_drug_identifier": {"pre": pre_drug_null, "post": post_drug_null},
            "missing_serious_flag": {"pre": pre_serious_bad, "post": post_serious_bad},
            "invalid_received_date": {"pre": "n/a (derived in silver)", "post": post_date_bad},
        },
        "pre_issue_rate_pct": round(100 * pre_issues / nb, 2),
        "post_issue_rate_pct": round(100 * post_issues / ns, 2),
        "note": "Aggregate issue rate across key failure modes, measured before vs after the contract gate.",
    }


def anomaly_check(silver):
    """Volume + serious-rate drift vs rolling baseline. WARN on breach; never silently passes."""
    n = len(silver)
    serious = sum(1 for r in silver if r.get("is_serious") is True)
    serious_rate = round(serious / n, 4) if n else 0.0

    baseline = json.load(open(BASELINE)) if BASELINE.exists() else None
    if baseline is None:
        # seed the baseline on first run
        baseline = {"record_count": n, "serious_rate": serious_rate, "seeded": True}
        json.dump(baseline, open(BASELINE, "w"), indent=2)

    def pct_change(cur, base):
        return round(100 * abs(cur - base) / base, 2) if base else 0.0

    vol_drift = pct_change(n, baseline["record_count"])
    rate_drift = pct_change(serious_rate, baseline["serious_rate"])
    THRESH = 20.0  # >20% swing = WARN
    status = "WARN" if (vol_drift > THRESH or rate_drift > THRESH) else "PASS"
    return {"record_count": n, "serious_rate": serious_rate,
            "baseline_record_count": baseline["record_count"],
            "baseline_serious_rate": baseline["serious_rate"],
            "volume_drift_pct": vol_drift, "serious_rate_drift_pct": rate_drift,
            "threshold_pct": THRESH, "status": status}


def append_run_log(report, anomaly, strict):
    """Append one line per gate run — a simple, queryable monitoring history (no external tooling)."""
    entry = {"run_grain": "contract_gate", "overall": report["overall_status"],
             "rows": report["rows_in"], "quarantined": report["rows_quarantined"],
             "contract_pass_pct": report["contract_pass_pct"], "anomaly": anomaly["status"],
             "strict": strict}
    with open(GATE_RUN_LOG, "a") as fh:
        fh.write(json.dumps(entry) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true",
                        help="treat WARN-level anomaly/grain breaches as blocking (SLA mode)")
    args = parser.parse_args()

    contract = yaml.safe_load(open(CONTRACT))
    bronze = load_jsonl(BRONZE)
    silver = load_jsonl(SILVER)

    results, quarantine = enforce(contract, silver)
    reduction = issue_reduction(bronze, silver)
    anomaly = anomaly_check(silver)

    # write quarantine table (never silent-drop)
    with open(QUARANTINE, "w") as fh:
        for row in quarantine:
            fh.write(json.dumps(row) + "\n")

    fails = [r for r in results if r["status"] == "FAIL"]
    warns = [r for r in results if r["status"] == "WARN"]
    overall = "FAIL" if fails else ("WARN" if warns else "PASS")

    report = {
        "contract_version": contract["contract_version"],
        "source": contract["source"],
        "generated_by": "pipeline/run_contract_gate.py",  # code-generated, not hand-authored
        "rows_in": len(silver),
        "rows_quarantined": len(quarantine),
        "rows_passed": len(silver) - len(quarantine),
        "overall_status": overall,
        "field_results": results,
        "contract_pass_pct": round(100 * (len(silver) - len(quarantine)) / (len(silver) or 1), 2),
    }
    json.dump(report, open(QUALITY_REPORT, "w"), indent=2)
    json.dump(reduction, open(TRUST_REDUCTION, "w"), indent=2)
    json.dump(anomaly, open(ANOMALY_REPORT, "w"), indent=2)
    append_run_log(report, anomaly, args.strict)

    print(f"contract gate: {overall} | rows={len(silver)} quarantined={len(quarantine)} "
          f"pass={report['contract_pass_pct']}%")
    print(f"issue reduction: {reduction['pre_issue_rate_pct']}% -> {reduction['post_issue_rate_pct']}%")
    print(f"anomaly: {anomaly['status']} (vol drift {anomaly['volume_drift_pct']}%, "
          f"serious-rate drift {anomaly['serious_rate_drift_pct']}%)")

    # blocking conditions: FAIL always blocks; in --strict (SLA mode) an anomaly WARN also blocks.
    blocked = overall == "FAIL" or (args.strict and anomaly["status"] == "WARN")
    if blocked:
        why = "contract FAIL" if overall == "FAIL" else "anomaly breach (strict SLA)"
        print(f"GATE BLOCKED ({why}) — silver/gold/semantic-model build halted.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
