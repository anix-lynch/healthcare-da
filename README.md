# Healthcare Analytics on Microsoft Fabric

> 🟥 **L1 Truth** — part of the [L1→L3 healthcare AI platform](https://gozeroshot.dev): trusted data → features → signals → agent actions → human adoption. This repo = a Microsoft Fabric medallion warehouse + dbt + semantic model that feeds BI and downstream AI.

**Microsoft Fabric medallion warehouse + dbt + TMDL semantic model + Power BI + REST API**, over 55,500 synthetic patient records.

[![Portfolio](https://img.shields.io/badge/Portfolio-gozeroshot.dev-blue)](https://gozeroshot.dev/projects/healthcare-analytics-fabric/)

## What it is
A trusted data backbone for hospital operations: raw clinical data → cleaned/conformed marts → a governed semantic model that Power BI and AI agents both consume. The point is **trust** — every metric traces to a dbt test, not a claim.

```
bronze → silver → gold        (dbt medallion in Fabric lakehouse/warehouse)
        → TMDL semantic model (certified measures, version-controlled like code)
        → Power BI             (executive dashboards)
        → REST API             (machine-readable marts for downstream AI)
```

## Highlights
- **dbt star schema** — staging → intermediate → fact + conformed dims, with domain SQL tests gating every build.
- **TMDL semantic model in Git** — measures + relationships reviewed like application code.
- **Microsoft Fabric** — lakehouse + warehouse + SQL endpoint + bronze-silver-gold pipeline (API-verified).
- **MLflow lineage** — training runs logged with metrics (honest AUC on synthetic data).
- **FastAPI** — OpenAPI-documented endpoints serving the gold marts.

## Repo Map

What lives where, at a glance:

```
healthcare-da/
├── dbt-project/     ✅ medallion SQL models (raw → clean → gold) + data tests
├── api/             ✅ FastAPI service serving the gold marts + OpenAPI snapshot
├── powerbi-model/   ✅ TMDL semantic model — measures + relationships, versioned like code
├── ml-pipeline/     ✅ readmission model — train + score, MLflow-logged
├── data/raw/        ✅ synthetic source data (clearly labeled, no real PHI)
├── inputs/          ✅ reproducible fixtures (API export · Fabric profile · semantic model)
├── outputs/         🖼️  proof artifacts per stage (api · dbt · BI · ML run results)
├── scripts/         ✅ ingestion + build + Fabric helpers
├── screenshots/     🖼️  live Power BI / Fabric captures (proof it's real)
└── openapi_snapshot.json  ✅ frozen public API surface
```

<details open>
<summary><b>Full file tree</b> (every file, plain-language — click to collapse)</summary>

```
healthcare-da/
├── dbt-project/                      the Fabric medallion warehouse
│   ├── models/staging/               ✅ stg_healthcare + sources — raw landing
│   ├── models/intermediate/          ✅ enriched encounters + readmission logic
│   ├── models/marts/core/            ✅ 8 dims + fact_patient_encounters (the gold star schema)
│   ├── tests/                        ✅ 3 SQL data tests (no negative LOS, discharge>admit…)
│   ├── dbt_project.yml · profiles    ✅ dbt config
│   └── README.md                     📖 how the marts are built
├── api/
│   ├── app/main.py                   ✅ FastAPI — serves the gold marts as endpoints
│   ├── test_api.py                   ✅ API smoke tests
│   ├── requirements.txt              ✅ API deps
│   └── README.md                     📖 how the API layer works
├── powerbi-model/                    the governed semantic layer (TMDL = code)
│   ├── model.tmdl · relationships    ✅ certified measures + star-schema relationships
│   └── tables/*.tmdl                 ✅ Date · Doctor · Hospital · Patient · Encounters
├── ml-pipeline/src/                  ✅ train.py + score.py — readmission model (MLflow)
├── data/raw/                         ✅ synthetic healthcare dataset + signals (no PHI)
├── inputs/                           reproducible fixtures (each stage + a context note)
│   ├── 01_api_export/                ✅ encounters pulled from the API
│   ├── 02_fabric_profile/            ✅ Fabric workspace connection used
│   ├── 03_semantic_model/            ✅ the TMDL semantic model snapshot
│   └── 04_ml_training_snapshot/      ✅ frozen training dataset
├── outputs/                          🖼️  proof captured per pipeline stage
│   ├── 01_api_proof/                 🖼️  live API stats response
│   ├── 02_dbt_proof/                 🖼️  dbt run results (tests passing)
│   ├── 02_schema · 02_mapping/       📖 schema + repo mapping notes
│   ├── 03_bi_proof/                  🖼️  Fabric lakehouse + semantic-model validation
│   └── 04_ml_proof/                  🖼️  MLflow run summary (honest AUC)
├── scripts/                          ingestion + Fabric + build helpers
│   ├── upload_bronze_to_onelake.py   ✅ loads bronze data into Fabric OneLake
│   ├── get_fabric_info.py            ✅ reads the live Fabric workspace state
│   ├── render_proof_screenshots.py   ✅ regenerates the screenshot proofs
│   ├── add_visuals_to_report.py      ✅ builds the BI report visuals
│   ├── *.sh                          ✅ Fabric API / Power BI / start-api helpers
│   └── README_POWERBI_CLI.md         📖 how to drive Power BI from the CLI
├── screenshots/                      🖼️  live Power BI + Fabric model-view captures
├── openapi_snapshot.json             ✅ frozen public API surface
├── .vscode/settings.json             ✅ editor config
└── README.md · LICENSE               📖 the story + MIT license
```
</details>

## Data note
All data is **synthetic** (clearly labeled) — no real PHI. Suitable for a public portfolio.

## Live Fabric proof

Captured from the live Microsoft Fabric workspace (synthetic data). The semantic-model
relationships were defined as code (TMDL) and pushed via the Fabric REST API, then rendered
in Model view — code-first, not click-built.

| | |
|---|---|
| ![Ingest](screenshots/fabric_files_ingest.png) | ![Medallion](screenshots/fabric_medallion_bronze.png) |
| Lakehouse Files — data ingested via Dataflow Gen2 | Medallion bronze layer |
| ![Star schema](screenshots/fabric_model_view_starschema.png) | ![DAX](screenshots/fabric_dax_query.png) |
| Semantic model — fact→dim star schema (1—∞, FK/PK) | DAX query over the modeled relationships |
| ![Lineage](screenshots/fabric_lineage_pipeline.png) | ![Table](screenshots/fabric_table_preview.png) |
| End-to-end lineage: CSV → Dataflow → Lakehouse → semantic model → report | Warehouse table preview |

---
*Part of Anix Lynch's L1→L3 healthcare AI platform — see [gozeroshot.dev](https://gozeroshot.dev). MIT licensed.*
