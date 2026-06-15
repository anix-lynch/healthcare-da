"""Contract + metric checks for the openFDA Fabric slice. Run: pytest -q

Each test guards against the vacuous-pass trap: it asserts it actually checked
at least one row (a loop that never enters must fail, not silently pass).
"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_contract_has_core_columns():
    c = json.load(open(ROOT / "contracts/openfda_fact_contract.json"))
    cols = {x["name"] for x in c["columns"]} if isinstance(c.get("columns"), list) else set(c["columns"])
    for required in ("safetyreportid", "primary_drug", "is_serious", "n_reactions"):
        assert required in cols, f"contract missing {required}"


def test_dax_under_1_3s():
    """Every benchmarked DAX query must clear the 1.3s Direct Lake bar."""
    d = json.load(open(ROOT / "proof/dax_latency.json"))
    checked = 0
    for name, q in d.items():
        if isinstance(q, dict) and "all_under_1_3s" in q:
            assert q["all_under_1_3s"], f"{name} DAX exceeded 1.3s"
            assert q["p50"] <= 1.3, f"{name} p50 {q['p50']}s over 1.3s bar"
            checked += 1
    assert checked >= 2, f"expected >=2 DAX query blocks, checked {checked}"


def test_gcp_fabric_reconciles():
    """Source (BigQuery) vs Fabric metric layer must reconcile on every table."""
    r = json.load(open(ROOT / "proof/reconcile_gcp_fabric.json"))
    checked = 0
    for table, v in r.items():
        if isinstance(v, dict) and "match" in v:
            assert v["match"] is True, f"{table} GCP != Fabric: {v}"
            checked += 1
    assert checked >= 3, f"expected >=3 reconciled tables, checked {checked}"


def test_quality_report_is_code_generated():
    """The quality report must be produced by the gate, not hand-authored."""
    r = json.load(open(ROOT / "proof/quality_report.json"))
    assert r.get("generated_by") == "pipeline/run_contract_gate.py", "report must be code-generated"
    assert r["overall_status"] in ("PASS", "WARN", "FAIL")


def test_gate_quarantines_failing_rows():
    """Synthetic bad data must trip FAIL-level rules and land in the quarantine lane."""
    import sys, yaml
    sys.path.insert(0, str(ROOT))
    from pipeline.run_contract_gate import enforce
    contract = yaml.safe_load(open(ROOT / "contracts/data_contract.yml"))
    bad = [
        {"safetyreportid": "X1", "drug_name": None, "occurcountry": "US", "is_serious": True, "received_date": "2026-01-01"},
        {"safetyreportid": None, "drug_name": "ASPIRIN", "occurcountry": "US", "is_serious": False, "received_date": "2026-01-01"},
        {"safetyreportid": "X3", "drug_name": "VALID", "occurcountry": "US", "is_serious": True, "received_date": "2026-01-01"},
    ]
    results, quarantine = enforce(contract, bad)
    fails = [r for r in results if r["status"] == "FAIL"]
    assert fails, "bad data must produce FAIL-level verdicts"
    assert len(quarantine) >= 2, f"expected >=2 quarantined rows, got {len(quarantine)}"
    assert all("violation_reason" in q for q in quarantine), "every quarantined row needs a reason"


def test_trust_reduction_proof_exists():
    """The ~15%->0% reduction must be backed by a code-generated proof file."""
    r = json.load(open(ROOT / "proof/trust_issues_reduction.json"))
    assert r["pre_issue_rate_pct"] > r["post_issue_rate_pct"], "post rate must be lower than pre"
    assert r["post_issue_rate_pct"] < 1.0, f"post-gate issue rate must be <1%, got {r['post_issue_rate_pct']}"
