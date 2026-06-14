#!/usr/bin/env python3
"""
BigQuery marts (N=3,000) → OneLake Delta — refreshes the tables the Direct Lake model reads.

Overwrites the four openFDA Delta tables in the HealthcareAnalytics Lakehouse with the
3,000-report marts. The deployed Direct Lake semantic model (openFDA Drug Safety, c11d0c74)
re-points automatically — no model rebuild, no import. Same column shapes, more rows.

Auth: user/SP token (storage.azure.com for OneLake, GOOGLE creds for BigQuery read).
Run:  ./.venv/bin/python pipeline/push_to_onelake.py   (needs deltalake + google-cloud-bigquery)
"""
import subprocess
import urllib.request

from deltalake import write_deltalake
from google.cloud import bigquery

PROJECT = "bchan-genai-lab"
DATASET = "healthcare_analytics"
LAKEHOUSE = "HealthcareAnalytics"
TABLES = ["fact_adverse_events", "dim_drug", "dim_reaction", "mart_drug_safety_kpis"]


def storage_token() -> str:
    return subprocess.run(
        ["az", "account", "get-access-token", "--resource", "https://storage.azure.com/",
         "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True, check=True).stdout.strip()


import time


def _path_count(table: str, tok: str) -> int:
    """How many files/dirs remain under the table path (0 = truly clean)."""
    url = (f"https://onelake.dfs.fabric.microsoft.com/{LAKEHOUSE}/"
           f"{LAKEHOUSE}.Lakehouse/Tables/{table}?resource=filesystem&recursive=true")
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}"}))
        import json as _j
        return len(_j.loads(r.read()).get("paths", []))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return 0
        raise


def _delete(path: str, tok: str):
    url = f"https://onelake.dfs.fabric.microsoft.com/{LAKEHOUSE}/{LAKEHOUSE}.Lakehouse/{path}?recursive=true"
    try:
        urllib.request.urlopen(urllib.request.Request(url, method="DELETE",
                               headers={"Authorization": f"Bearer {tok}"}))
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise


def delete_existing(table: str, tok: str):
    """Fully remove the Fabric Delta dir (table + _delta_log) and confirm 0 files remain."""
    _delete(f"Tables/{table}/_delta_log", tok)
    _delete(f"Tables/{table}", tok)
    for _ in range(25):
        if _path_count(table, tok) == 0:
            return
        time.sleep(1)


def main():
    bq = bigquery.Client(project=PROJECT)
    tok = storage_token()
    opts = {"bearer_token": tok, "use_fabric_endpoint": "true"}
    for t in TABLES:
        arrow = bq.query(f"SELECT * FROM `{PROJECT}.{DATASET}.{t}`").to_arrow()
        delete_existing(t, tok)
        uri = (f"abfss://{LAKEHOUSE}@onelake.dfs.fabric.microsoft.com/"
               f"{LAKEHOUSE}.Lakehouse/Tables/{t}")
        write_deltalake(uri, arrow, storage_options=opts)   # clean path → create fresh
        print(f"  OneLake ← {t}: {arrow.num_rows} rows")


if __name__ == "__main__":
    main()
