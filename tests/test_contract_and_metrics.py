"""Contract + metric checks for the openFDA Fabric slice. Run: pytest -q"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

def test_contract_has_core_columns():
    c = json.load(open(ROOT / "contracts/openfda_fact_contract_v1.0.0.json"))
    cols = {x["name"] for x in c["columns"]} if isinstance(c.get("columns"), list) else set(c["columns"])
    for required in ("safetyreportid", "primary_drug", "is_serious", "n_reactions"):
        assert required in cols, f"contract missing {required}"

def test_dax_under_5s():
    d = json.load(open(ROOT / "proof/powerbi_dax_latency.json"))
    for name, q in d.items():
        if isinstance(q, dict) and "all_under_5s" in q:
            assert q["all_under_5s"], f"{name} DAX exceeded 5s"

def test_gcp_fabric_reconciles():
    r = json.load(open(ROOT / "proof/reconciliation_gcp_vs_fabric.json"))
    for table, v in r.items():
        if isinstance(v, dict) and "gcp" in v and "fabric" in v:
            assert v["gcp"] == v["fabric"], f"{table} GCP != Fabric"
