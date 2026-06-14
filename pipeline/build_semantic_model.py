#!/usr/bin/env python3
"""
Deploy the Direct Lake semantic model from model/model.bim — Fabric Items API, no GUI.

model/model.bim is the committed source of truth (fact + dim_drug + dim_reaction + relationship
+ measures, plus the mart_drug_safety_kpis table the report binds to). This script pushes it to
the "openFDA Drug Safety" model (id c11d0c74) via updateDefinition. Direct Lake = reads the
Lakehouse SQL endpoint live, no import.

Auth: api.fabric.microsoft.com token (Items API). Run: python pipeline/build_semantic_model.py
"""
import base64
import json
import subprocess
import urllib.request
from pathlib import Path

WS = "577de43f-21b4-479e-99b6-ea78f32e5216"          # HealthcareAnalytics workspace
MODEL_ID = "c11d0c74-1fa3-4d45-b7cc-2ea8a1243df0"
SQL_ENDPOINT_ITEM = "7ad5c267-d044-418b-b24c-c9925be5394d"
BIM = Path(__file__).resolve().parents[1] / "model" / "model.bim"


def tok(resource: str) -> str:
    return subprocess.run(["az", "account", "get-access-token", "--resource", resource,
                           "--query", "accessToken", "-o", "tsv"],
                          capture_output=True, text=True, check=True).stdout.strip()


def sql_endpoint(fab: str) -> str:
    url = f"https://api.fabric.microsoft.com/v1/workspaces/{WS}/sqlEndpoints/{SQL_ENDPOINT_ITEM}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {fab}"})
    return json.load(urllib.request.urlopen(req)).get("properties", {}).get("connectionString", "")


def deploy() -> int:
    fab = tok("https://api.fabric.microsoft.com/")
    bim = json.loads(BIM.read_text())
    server = sql_endpoint(fab) or "ndcddt2bpc6elclhiudkopyo5m-h7sh2v5uegpepgnw5j4pglsscy.datawarehouse.fabric.microsoft.com"
    bim["model"]["expressions"][0]["expression"] = (
        f'let database = Sql.Database("{server}", "HealthcareAnalytics") in database')
    b64 = lambda s: base64.b64encode(s.encode()).decode()
    parts = [{"path": "model.bim", "payload": b64(json.dumps(bim)), "payloadType": "InlineBase64"},
             {"path": "definition.pbism", "payload": b64('{"version":"4.0","settings":{}}'), "payloadType": "InlineBase64"}]
    body = json.dumps({"definition": {"parts": parts}}).encode()
    req = urllib.request.Request(
        f"https://api.fabric.microsoft.com/v1/workspaces/{WS}/semanticModels/{MODEL_ID}/updateDefinition",
        data=body, method="POST", headers={"Authorization": f"Bearer {fab}", "Content-Type": "application/json"})
    return urllib.request.urlopen(req).status   # 202 = accepted (async)


if __name__ == "__main__":
    print("updateDefinition →", deploy())
