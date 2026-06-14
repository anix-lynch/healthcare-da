#!/usr/bin/env python3
"""
Benchmark DAX through the Power BI engine — the real "Power BI query", no GUI.

Runs DAX against the deployed openFDA Direct Lake model via the executeQueries REST API and
records latency to ../proof/dax_latency.json. executeQueries needs a DELEGATED (user)
token — app-only service-principal tokens get 401 (see /azure-auth-hell skill). N=3,000.

Auth: analysis.windows.net/powerbi/api token (delegated). Run: python pipeline/benchmark_dax.py
"""
import json
import subprocess
import time
import urllib.request
from pathlib import Path

WS = "577de43f-21b4-479e-99b6-ea78f32e5216"
MODEL = "c11d0c74-1fa3-4d45-b7cc-2ea8a1243df0"
OUT = Path(__file__).resolve().parents[1] / "proof" / "dax_latency.json"
QUERIES = {
    "kpi_card": 'EVALUATE ROW("total", COUNTROWS(mart_drug_safety_kpis), '
                '"serious", AVERAGE(mart_drug_safety_kpis[serious_rate]))',
    "drug_leaderboard": 'EVALUATE TOPN(10, mart_drug_safety_kpis, '
                        'mart_drug_safety_kpis[total_reports], DESC)',
}


def tok() -> str:
    return subprocess.run(["az", "account", "get-access-token", "--resource",
                           "https://analysis.windows.net/powerbi/api", "--query", "accessToken", "-o", "tsv"],
                          capture_output=True, text=True, check=True).stdout.strip()


def bench(label: str, dax: str, pbi: str, runs: int = 5) -> dict:
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WS}/datasets/{MODEL}/executeQueries"
    lat = []
    for _ in range(runs):
        body = json.dumps({"queries": [{"query": dax}]}).encode()
        req = urllib.request.Request(url, data=body, method="POST",
                                     headers={"Authorization": f"Bearer {pbi}", "Content-Type": "application/json"})
        t0 = time.time(); urllib.request.urlopen(req).read(); lat.append(round(time.time() - t0, 2))
    s = sorted(lat)
    return {"runs": lat, "p50": s[len(s) // 2], "max": max(lat), "all_under_1_3s": max(lat[1:]) < 1.3}


def main():
    pbi = tok()
    out = {"_doc": "DAX latency via executeQueries on the openFDA Direct Lake model @ N=3,000 reports "
                   "(562-drug mart). Cold first run = Direct Lake warmup.", "n_reports": 3000}
    for label, dax in QUERIES.items():
        out[label] = bench(label, dax, pbi)
        print(f"  {label}: p50 {out[label]['p50']}s")
    OUT.write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
