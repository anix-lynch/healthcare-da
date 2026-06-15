#!/usr/bin/env python3
"""Vertex / Cloud Run consumer preflight — the SAME contract gate, reused on the AI-serving side.

Any GCP/Vertex-side consumer (a grounded agent, a Cloud Run serving job, an LLM/RAG pipeline)
imports this and calls preflight() BEFORE reading the marts. It (1) reuses enforce() from the gate
library to validate the data it is about to serve, and (2) checks the last committed gate status.
If the contract is not satisfied, the consumer refuses to serve — so bad data never reaches the
LLM/RAG layer, on the Vertex side too, not just the Fabric build side.

One contract definition, enforced on both the build (Fabric) and serve (Vertex) sides — no drift.

Run:  python3 pipeline/vertex_preflight.py
"""
import json
import sys
import pathlib

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from run_contract_gate import enforce, load_jsonl, CONTRACT, SILVER, QUALITY_REPORT


def preflight(rows=None):
    """Return a serve-decision a Vertex/LLM consumer checks before reading data."""
    contract = yaml.safe_load(open(CONTRACT))
    rows = rows if rows is not None else load_jsonl(SILVER)
    results, quarantine = enforce(contract, rows)
    fails = [r for r in results if r["status"] == "FAIL"]
    last = json.load(open(QUALITY_REPORT)) if QUALITY_REPORT.exists() else {}
    serve_allowed = not fails and last.get("overall_status") in ("PASS", "WARN")
    return {
        "serve_allowed": serve_allowed,
        "live_fail_fields": [r["field"] for r in fails],
        "last_committed_status": last.get("overall_status"),
        "quarantine_would_hold": len(quarantine),
    }


def main():
    r = preflight()
    print(f"vertex preflight: serve_allowed={r['serve_allowed']} "
          f"last_status={r['last_committed_status']} live_fails={r['live_fail_fields']}")
    if not r["serve_allowed"]:
        print("PREFLIGHT BLOCKED — Vertex/LLM consumer must not serve on contract-failing data.",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
