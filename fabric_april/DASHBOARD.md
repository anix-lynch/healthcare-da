# DASHBOARD — Fabric April track

**👈 we are here:** F2 Data Factory pipeline (bronze→silver→gold) — F1 bronze file upload **done** via `scripts/upload_bronze_to_onelake.py`.

## Phase summary

| Phase | Status | Who |
|-------|--------|-----|
| F0 Auth + capacity | ⬜ | b-turn → AI |
| F1 Lakehouse + bronze CSV | ✅ | AI | 
| F2 Data Factory pipeline (medallion) | ⬜ | b-turn |
| F3 Warehouse / SQL proof | ⬜ | b-turn |
| F4 Power BI Direct Lake + report | ⬜ | b-turn |

## Flow

```
[data/raw CSV] → Fabric Lakehouse (bronze) → Pipeline (silver/gold) → Warehouse SQL → Power BI Direct Lake → screenshots + export
```

## SLA STATUS

| Phase | Done when (see SLA.md) | Met |
|-------|-------------------------|-----|
| F1 | `outputs/01_screenshots/lakehouse_files_explorer.png` + `outputs/03_proof/bronze_onelake_upload.txt` | ⏳ (file uploaded; screenshot optional) |
| F2 | `outputs/01_screenshots/data_factory_pipeline_run.png` **or** `outputs/02_exports/fabric_pipeline_definition.json` | ⬜ |
| F3 | `outputs/01_screenshots/warehouse_sql_results.png` | ⬜ |
| F4 | `outputs/01_screenshots/powerbi_directlake_report.png` | ⬜ |

**SHIPPED:** false
