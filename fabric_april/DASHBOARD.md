# DASHBOARD — Fabric April track

**👈 we are here:** F3 Warehouse SQL — F1 ✅ · F2 pipeline **succeeded in Fabric** (save real PNG to `outputs/01_screenshots/data_factory_pipeline_run.png` if disk still shows 0 bytes) · see `outputs/03_proof/f2_pipeline_run.txt`.

## Phase summary

| Phase | Status | Who |
|-------|--------|-----|
| F0 Auth + capacity | ⬜ | b-turn → AI |
| F1 Lakehouse + bronze CSV | ✅ | AI | 
| F2 Data Factory pipeline (medallion) | ✅ (run succeeded; confirm PNG on disk) | AI |
| F3 Warehouse / SQL proof | ⬜ | b-turn |
| F4 Power BI Direct Lake + report | ⬜ | b-turn |

## Flow

```
[data/raw CSV] → Fabric Lakehouse (bronze) → Pipeline (silver/gold) → Warehouse SQL → Power BI Direct Lake → screenshots + export
```

## SLA STATUS

| Phase | Done when (see SLA.md) | Met |
|-------|-------------------------|-----|
| F1 | `outputs/01_screenshots/lakehouse_files_explorer.png` + `outputs/03_proof/bronze_onelake_upload.txt` | ✅ |
| F2 | `outputs/01_screenshots/data_factory_pipeline_run.png` **or** `outputs/02_exports/fabric_pipeline_definition.json` | ⏳ (run done; **replace 0-byte PNG** with real capture — see `outputs/03_proof/f2_pipeline_run.txt`) |
| F3 | `outputs/01_screenshots/warehouse_sql_results.png` | ⬜ |
| F4 | `outputs/01_screenshots/powerbi_directlake_report.png` | ⬜ |

**SHIPPED:** false
