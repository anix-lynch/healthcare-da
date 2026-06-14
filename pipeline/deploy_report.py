#!/usr/bin/env python3
"""
Deploy a Power BI report (PBIR) with visuals over the semantic model — Fabric Items API, no GUI.

Creates "openFDA Drug Safety Report" (id ef468dc5): 2 KPI cards + 1 bar chart bound to the
openFDA Direct Lake model. byConnection + $schema => the report materializes (byPath fails).
The deployed definition lives in ../model/report/ (report.json + definition.pbir).

Auth: api.fabric.microsoft.com token (Items API). Run: python pipeline/deploy_report.py
"""
import base64
import json
import subprocess
import urllib.request

WS = "577de43f-21b4-479e-99b6-ea78f32e5216"
WS_NAME = "HealthcareAnalytics"
MODEL = "c11d0c74-1fa3-4d45-b7cc-2ea8a1243df0"
MODEL_NAME = "openFDA Drug Safety"
E = "mart_drug_safety_kpis"


def tok(resource: str) -> str:
    return subprocess.run(["az", "account", "get-access-token", "--resource", resource,
                           "--query", "accessToken", "-o", "tsv"],
                          capture_output=True, text=True, check=True).stdout.strip()


def create_powerbi_report() -> int:
    fab = tok("https://api.fabric.microsoft.com/")
    b64 = lambda s: base64.b64encode(s.encode()).decode()
    col = lambda p: {"Column": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": p}, "Name": f"{E}.{p}"}
    meas = lambda p: {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": p}, "Name": f"{E}.{p}"}

    def vc(name, vtype, proj, sel, x, y, w, h):
        cfg = {"name": name, "singleVisual": {"visualType": vtype, "projections": proj,
               "prototypeQuery": {"Version": 2, "From": [{"Name": "m", "Entity": E, "Type": 0}], "Select": sel}}}
        return {"x": x, "y": y, "z": 0, "width": w, "height": h, "config": json.dumps(cfg)}

    visuals = [
        vc("vTotalReports", "card", {"Values": [{"queryRef": f"{E}.Total Reports"}]}, [meas("Total Reports")], 40, 30, 300, 160),
        vc("vAvgSeriousRate", "card", {"Values": [{"queryRef": f"{E}.Avg Serious Rate"}]}, [meas("Avg Serious Rate")], 360, 30, 300, 160),
        vc("vDrugLeaderboard", "barChart",
           {"Category": [{"queryRef": f"{E}.primary_drug"}], "Y": [{"queryRef": f"{E}.Total Reports"}]},
           [col("primary_drug"), meas("Total Reports")], 40, 210, 640, 470)]
    report = {"version": "5.43", "themeCollection": {"baseTheme": {"name": "CY24SU10"}}, "layoutOptimization": 0,
              "sections": [{"name": "openfdapage", "displayName": "openFDA Drug Safety", "displayOption": 1,
                            "width": 1280, "height": 720, "visualContainers": visuals}]}
    pbir = {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
            "version": "4.0", "datasetReference": {"byConnection": {"connectionString":
                f'Data Source=powerbi://api.powerbi.com/v1.0/myorg/{WS_NAME};initial catalog="{MODEL_NAME}";'
                f'integrated security=ClaimsToken;semanticmodelid={MODEL}'}}}
    platform = json.dumps({"metadata": {"type": "Report", "displayName": "openFDA Drug Safety Report"},
                           "config": {"version": "2.0", "logicalId": "00000000-0000-0000-0000-000000000001"}})
    parts = [{"path": "report.json", "payload": b64(json.dumps(report)), "payloadType": "InlineBase64"},
             {"path": "definition.pbir", "payload": b64(json.dumps(pbir)), "payloadType": "InlineBase64"},
             {"path": ".platform", "payload": b64(platform), "payloadType": "InlineBase64"}]
    body = json.dumps({"displayName": "openFDA Drug Safety Report", "definition": {"parts": parts}}).encode()
    req = urllib.request.Request(f"https://api.fabric.microsoft.com/v1/workspaces/{WS}/reports",
                                 data=body, headers={"Authorization": f"Bearer {fab}",
                                                     "Content-Type": "application/json"}, method="POST")
    return urllib.request.urlopen(req).status  # 202 = created


if __name__ == "__main__":
    create_powerbi_report()
    print("openFDA Drug Safety Report deployed (definition saved in model/report/)")
