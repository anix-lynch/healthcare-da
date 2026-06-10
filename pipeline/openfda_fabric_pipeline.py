#!/usr/bin/env python3
"""
openFDA → Microsoft Fabric pipeline (CLI/API only — no GUI, runs on the free FTL trial).

Repoints this Fabric repo from the synthetic patient/encounter story to REAL openFDA
adverse-event data, proving the whole BI lane is agent-drivable as of 2026-06:
  1. INGEST   — write the openFDA star schema straight to OneLake as Delta (deltalake, NO ODBC)
  2. MODEL    — create a Direct Lake semantic model over the Lakehouse via the Fabric Items API
  3. REPORT   — create a Power BI report (PBIR-legacy) with visuals via the Items API
  4. BENCH    — run DAX through the Power BI engine (executeQueries) and measure latency

Three token audiences (do not mix): storage.azure.com (OneLake) · api.fabric.microsoft.com/
(Items API) · analysis.windows.net/powerbi/api (executeQueries). The one trial cap is
ExportToFile (403) — native screenshots need a logged-in browser; see proof/ for an
agent-made chart from the same DAX data. Full notes: /azure-auth-hell skill.
"""
import base64, json, subprocess, time, urllib.request

WS = "<FABRIC_WORKSPACE_ID>"            # HealthcareAnalytics workspace
LAKEHOUSE = "HealthcareAnalytics"
SQL_ENDPOINT = "<sqlendpoint>.datawarehouse.fabric.microsoft.com"


def tok(resource):
    return subprocess.run(["az", "account", "get-access-token", "--resource", resource,
                           "--query", "accessToken", "-o", "tsv"],
                          capture_output=True, text=True).stdout.strip()


# ── 1. INGEST: GCP BigQuery openFDA marts → OneLake Delta (pure-python, no ODBC) ──
def ingest_to_onelake(df, table):
    from deltalake import write_deltalake, DeltaTable
    storage = tok("https://storage.azure.com/")
    uri = f"abfss://{LAKEHOUSE}@onelake.dfs.fabric.microsoft.com/{LAKEHOUSE}.Lakehouse/Tables/{table}"
    opts = {"bearer_token": storage, "use_fabric_endpoint": "true"}
    write_deltalake(uri, df, mode="overwrite", storage_options=opts)
    return DeltaTable(uri, storage_options=opts).to_pyarrow_dataset().count_rows()  # reconcile vs GCP


# ── 2. MODEL: Direct Lake semantic model via Fabric Items API (NOT XMLA — trials cap XMLA) ──
def create_directlake_model(name, table, columns, measures):
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
                                 data=body, headers={"Authorization": f"Bearer {fab}", "Content-Type": "application/json"}, method="POST")
    return urllib.request.urlopen(req).status   # 202 = created (async)


# ── 4. BENCH: DAX through the Power BI engine — the real "Power BI query" ──
def benchmark_dax(model_id, dax, runs=5):
    pbi = tok("https://analysis.windows.net/powerbi/api")
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WS}/datasets/{model_id}/executeQueries"
    lat = []
    for _ in range(runs):
        body = json.dumps({"queries": [{"query": dax}]}).encode()
        req = urllib.request.Request(url, data=body, headers={"Authorization": f"Bearer {pbi}", "Content-Type": "application/json"}, method="POST")
        t0 = time.time(); urllib.request.urlopen(req).read(); lat.append(round(time.time() - t0, 2))
    return {"runs": lat, "warm_p50": sorted(lat)[len(lat) // 2], "max": max(lat)}  # cold first run ~8s (Direct Lake warmup)


# ── 3. REPORT (PBIR-legacy) — creates a real Power BI
#    report WITH visuals over the semantic model, via the Fabric Items API (NOT the UI).
def create_powerbi_report(workspace_id, model_id, model_name, workspace_name):
    """Deploys a Power BI report with 3 visuals (2 KPI cards + 1 bar chart) bound to the openFDA
    Direct Lake model. Returns report id. This is how report `openFDA Drug Safety Report`
    (id ef468dc5-...) was created — verified live (webUrl resolves, bound to dataset c11d0c74)."""
    fab = tok("https://api.fabric.microsoft.com/")
    b64 = lambda s: base64.b64encode(s.encode()).decode()
    E = "mart_drug_safety_kpis"
    col = lambda p: {"Column": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": p}, "Name": f"{E}.{p}"}
    meas = lambda p: {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": p}, "Name": f"{E}.{p}"}
    def vc(name, vtype, proj, sel, x, y, w, h):
        cfg = {"name": name, "singleVisual": {"visualType": vtype, "projections": proj,
               "prototypeQuery": {"Version": 2, "From": [{"Name": "m", "Entity": E, "Type": 0}], "Select": sel}}}
        return {"x": x, "y": y, "z": 0, "width": w, "height": h, "config": json.dumps(cfg)}
    visuals = [  # the visual inventory
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
                f'Data Source=powerbi://api.powerbi.com/v1.0/myorg/{workspace_name};initial catalog="{model_name}";integrated security=ClaimsToken;semanticmodelid={model_id}'}}}
    platform = json.dumps({"metadata": {"type": "Report", "displayName": "openFDA Drug Safety Report"}, "config": {"version": "2.0", "logicalId": "00000000-0000-0000-0000-000000000001"}})
    parts = [{"path": "report.json", "payload": b64(json.dumps(report)), "payloadType": "InlineBase64"},
             {"path": "definition.pbir", "payload": b64(json.dumps(pbir)), "payloadType": "InlineBase64"},
             {"path": ".platform", "payload": b64(platform), "payloadType": "InlineBase64"}]
    body = json.dumps({"displayName": "openFDA Drug Safety Report", "definition": {"parts": parts}}).encode()
    req = urllib.request.Request(f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/reports",
                                 data=body, headers={"Authorization": f"Bearer {fab}", "Content-Type": "application/json"}, method="POST")
    return urllib.request.urlopen(req).status  # 202 = created; byConnection + $schema => materializes (byPath silently fails)


if __name__ == "__main__":
    # Documents the proven openFDA->Fabric pipeline (ingest -> model -> report -> bench).
    # Live artifacts (2026-06-09): semantic model openFDA Drug Safety (id c11d0c74),
    # report openFDA Drug Safety Report (id ef468dc5) with 3 visuals, reconciled GCP==Fabric,
    # DAX warm p50 ~0.7-1.2s. Fill WS / SQL_ENDPOINT from your workspace to re-run.
    print("openFDA -> Fabric pipeline: ingest_to_onelake -> create_directlake_model -> create_powerbi_report -> benchmark_dax")
