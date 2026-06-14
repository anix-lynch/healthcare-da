#!/usr/bin/env python3
"""
Deploy a Direct Lake semantic model over the OneLake gold tables — Fabric Items API, no GUI.

Creates/updates the "openFDA Drug Safety" model (id c11d0c74) whose mart table the Power BI
report binds to. Direct Lake = the model reads the Lakehouse SQL endpoint live, no import.
The deployed definition lives in ../model/ (TMDL) as the committed source of truth.

Auth: api.fabric.microsoft.com token (Items API). Run: python pipeline/build_semantic_model.py
"""
import base64
import json
import subprocess
import urllib.request

WS = "577de43f-21b4-479e-99b6-ea78f32e5216"          # HealthcareAnalytics workspace
LAKEHOUSE = "HealthcareAnalytics"
SQL_ENDPOINT = "<sqlendpoint>.datawarehouse.fabric.microsoft.com"   # Lakehouse SQL analytics endpoint


def tok(resource: str) -> str:
    return subprocess.run(["az", "account", "get-access-token", "--resource", resource,
                           "--query", "accessToken", "-o", "tsv"],
                          capture_output=True, text=True, check=True).stdout.strip()


def create_directlake_model(name: str, table: str, columns: list[tuple], measures: list[tuple]) -> int:
    """Direct Lake model via the Items API (NOT XMLA — Fabric trials cap XMLA)."""
    fab = tok("https://api.fabric.microsoft.com/")
    b64 = lambda s: base64.b64encode(s.encode()).decode()
    bim = {"name": name, "compatibilityLevel": 1604, "model": {
        "culture": "en-US", "defaultPowerBIDataSourceVersion": "powerBI_V3",
        "expressions": [{"name": "DatabaseQuery", "kind": "m",
                         "expression": f'let database = Sql.Database("{SQL_ENDPOINT}", "{LAKEHOUSE}") in database'}],
        "tables": [{"name": table,
                    "columns": [{"name": c, "dataType": t, "sourceColumn": c} for c, t in columns],
                    "measures": [{"name": n, "expression": e} for n, e in measures],
                    "partitions": [{"name": table, "mode": "directLake",
                                    "source": {"type": "entity", "entityName": table,
                                               "expressionSource": "DatabaseQuery", "schemaName": "dbo"}}]}]}}
    parts = [{"path": "model.bim", "payload": b64(json.dumps(bim)), "payloadType": "InlineBase64"},
             {"path": "definition.pbism", "payload": b64('{"version":"4.0","settings":{}}'), "payloadType": "InlineBase64"}]
    body = json.dumps({"displayName": name, "definition": {"parts": parts}}).encode()
    req = urllib.request.Request(f"https://api.fabric.microsoft.com/v1/workspaces/{WS}/semanticModels",
                                 data=body, headers={"Authorization": f"Bearer {fab}",
                                                     "Content-Type": "application/json"}, method="POST")
    return urllib.request.urlopen(req).status   # 202 = created (async)


if __name__ == "__main__":
    # The deployed mart model: measures the report reads.
    create_directlake_model(
        "openFDA Drug Safety", "mart_drug_safety_kpis",
        columns=[("primary_drug", "string"), ("total_reports", "int64"),
                 ("serious_rate", "double"), ("distinct_reactions", "int64")],
        measures=[("Total Reports", "SUM(mart_drug_safety_kpis[total_reports])"),
                  ("Avg Serious Rate", "AVERAGE(mart_drug_safety_kpis[serious_rate])")])
    print("openFDA Drug Safety Direct Lake model deployed (definition saved in model/)")
