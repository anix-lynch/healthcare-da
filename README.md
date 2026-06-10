# Healthcare Analytics on Microsoft Fabric — openFDA

> **openFDA drug-safety analytics on Microsoft Fabric — built code-first, no GUI.**
> Real openFDA FAERS reports land in OneLake as Delta, a Direct Lake semantic model and a
> Power BI report are deployed through the Fabric REST API, DAX runs sub-1.3s, and counts +
> business metrics reconcile against the GCP BigQuery source. The whole BI lane is agent-drivable.

## Repo Map
```
healthcare-openfda-fabric/
├── pipeline/    openFDA → OneLake (Delta) → Direct Lake semantic model → Power BI report → DAX bench
├── contracts/   the shared openFDA fact contract (same one GCP + AWS use)
├── proofs/      DAX latency receipt + GCP↔Fabric reconciliation receipt
├── visuals/     openFDA chart (from the DAX data) + star schema + executive KPI
├── tests/       contract shape + DAX<5s + reconcile checks (pytest)
├── README.md    you are here
└── LICENSE
```

## What it proves
- **Power BI ships from code** — semantic model + report (`openFDA Drug Safety Report`, id `ef468dc5`) deploy via the Fabric Items API, not manual clicking (`pipeline/openfda_fabric_pipeline.py`).
- **Sub-second answers** — real DAX through the Power BI engine: drug leaderboard p50 1.15s, KPI card p50 0.66s, all < 5s (`proofs/powerbi_dax_latency.json`).
- **Fabric can't quietly change the truth** — fact + dims + mart counts reconcile GCP ↔ Fabric (`proofs/reconciliation_gcp_vs_fabric.json`).

## Run
Fill `WS` / `SQL_ENDPOINT` from your Fabric workspace, then drive `pipeline/openfda_fabric_pipeline.py`
(`ingest_to_onelake → create_directlake_model → create_powerbi_report → benchmark_dax`). Needs an
interactive owner `az login` (three token audiences: storage.azure.com · api.fabric.microsoft.com · powerbi).

## Honest scope
n=300 real openFDA reports. `ExportToFile` (report → PNG via API) is capped on the free FTL trial, so the
rendered screenshot needs a logged-in browser; `visuals/openfda_drug_safety_chart.png` is from the same DAX data.
