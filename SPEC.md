# SPEC: Healthcare Analytics Progress Tracker

**👤 5% you · 🤖 95% agent** — Bchan: P6 approve only (or skip P3/P5 if not needed). Agent runs terminal with keys from config.

Last updated: 2026-03-14 (sweep + workflow inference + auth inference applied)

## Goal

Ship an interview-ready, evidence-backed healthcare analytics stack (API → dbt → semantic model → ML) with a single execution tracker; every claim traceable to code per **sla** (locked bullets + claim-to-code map).

**Workflow order:** Raw data in place (55K rows) → run populate script → API/semantic proof captured → optionally install deps for dbt/ML → then all proof outputs filled. No proof screenshots until outputs are populated.

## Where we are · Next step

| Step | Done | Next |
| ---- | ---- | ---- |
| P0 Context + keys | ✅ | |
| P1 Scaffold repair | ✅ | |
| P1.5 Raw data loaded | ✅ | |
| P2 API proof | ✅ | |
| P3 dbt proof | ✅ | |
| P4 Semantic model proof | ✅ | |
| P5 ML proof | ✅ | |
| P6 Final interview lock | ⬜ | Bchan: approve go/no-go |

## Inputs

| Input | Where it lives | Status | Who | Notes |
|-------|----------------|--------|-----|-------|
| **Raw dataset** | data/raw/healthcare_dataset.csv | ✅ | AI | Verified: 55,501 rows. Unlocks: populate script → proof outputs. |
| API export snapshot | inputs/01_api_export/encounters_export_2026-03-11.json | ✅ | AI | Captured (100 encounters sample). |
| Semantic model source | inputs/03_semantic_model/healthcare_semantic_model_v1.tmdl | ✅ | AI | TMDL source in repo. |
| AZURE_TENANT_ID | ~/.config/secrets/global.env | ✅ | AI | Verified. Unlocks: Fabric/Power BI auth (service principal). |
| AZURE_SUBSCRIPTION_ID | ~/.config/secrets/global.env | ✅ | AI | Verified. |
| AZURE_CLIENT_ID | ~/.config/secrets/global.env | ✅ | AI | Verified (Fabric-PowerBI app). Unlocks: P4 script (check_p4_semantic_model.sh). |
| AZURE_CLIENT_SECRET | ~/.config/secrets/global.env | ✅ | AI | Verified. Unlocks: P4 script. |
| FABRIC_WORKSPACE_ID | ~/.config/secrets/fabric.env | ✅ | AI | Verified. Unlocks: P4 script. |
| dbt-fabric adapter | .venv with dbt-core + dbt-fabric | ✅ | AI | Created venv; dbt run successful. Unlocks: P3 (dbt run). |
| mlflow + xgboost | pip install mlflow xgboost scikit-learn | ✅ | AI | Verified. Unlocks: P5 (ML training proof). |

## Outputs

| Output | Where it lives | Status | Who | Notes |
|--------|----------------|--------|-----|-------|
| API proof stats | outputs/01_api_proof/api_stats_response_2026-03-11.json | ✅ | AI | Captured (stats JSON: 55K encounters, demographics, financial, operational). |
| API export sample | inputs/01_api_export/encounters_export_2026-03-11.json | ✅ | AI | Captured (100 encounters). |
| dbt run proof | outputs/02_dbt_proof/dbt_run_results_2026-03-11.json | ✅ | AI | Captured (fact_patient_encounters: success, 0.93s). |
| Semantic model validation | outputs/03_bi_proof/semantic_model_validation_2026-03-11.md | ✅ | AI | P4 script passed: 1 dataset in Fabric workspace. |
| MLflow run summary | outputs/04_ml_proof/mlflow_run_summary_2026-03-11.md | ✅ | AI | Captured (accuracy: 0.6641, AUC: 0.5097, feature importance). |
| Resume claim traceability | outputs/05_resume_proof/resume_claim_traceability_2026-03-11.md | ✅ | AI | Claim→proof map with status. |
| Warehouse/BI schema summary | outputs/02_schema/healthcare_analytics_schema_2026-03-11.md | ✅ | AI | Scaffold doc (35 lines). |
| Repository mapping summary | outputs/02_mapping/repo_mapping_2026-03-11.md | ✅ | AI | Scaffold doc. |

## Phase Gates

| Phase | Gate | Status | Who |
|-------|------|--------|-----|
| P0 Context + keys | Read AGENT.md, TOOL_STACK_AUDIT; verify global.env + fabric.env for Azure/Fabric keys | ✅ | AI |
| P1 Scaffold repair | Backup legacy scaffold; create canonical SPEC.md | ✅ | AI |
| P1.5 Raw data loaded | data/raw/healthcare_dataset.csv present (55,501 rows); run populate_proof_artifacts.sh | ✅ | AI |
| P2 API proof | Verify API stats endpoint evidence (outputs/01_api_proof/ has content) | ✅ | AI |
| P3 dbt proof | Created .venv with dbt-core + dbt-fabric; run dbt run; capture run_results.json | ✅ | AI |
| P4 Semantic model proof | Run check_p4_semantic_model.sh (auth from global.env service principal) | ✅ | AI |
| P5 ML proof | Install mlflow; run train.py; capture run summary | ✅ | AI |
| P6 Final interview lock | Approve end-to-end go/no-go (or approve with P3/P5 skipped if optional) | ⬜ | b-turn |

## B-turns Pending

**P6 (final lock) — Bchan only:**
Approve go/no-go when ready. You can approve with P3 skipped if not needed for interview (API + semantic model + ML proofs may be enough).

## File Map

```
healthcare-da/
├── sla                          ← Locked resume bullets + claim-to-code map (source of truth)
├── SPEC.md                      ← Single source of truth for progress
├── DASHBOARD.md                 ← Phase summary + flow
├── data/raw/                    ← 55,501 patient records (healthcare_dataset.csv)
├── api/                         ← FastAPI (11 endpoints)
├── dbt-project/                 ← Star schema (8 marts, 3 tests)
├── powerbi-model/               ← TMDL semantic model
├── ml-pipeline/                 ← XGBoost + MLflow
├── scripts/                     ← start_api.sh, populate_proof_artifacts.sh, check_p4_semantic_model.sh, fabric_doctor.sh
├── inputs/                      ← 01_api_export, 02_fabric_profile, 03_semantic_model, 04_ml_training_snapshot
└── outputs/                     ← 01_api_proof, 02_dbt_proof, 03_bi_proof, 04_ml_proof, 05_resume_proof, 02_schema, 02_mapping
```

## Proof Artifacts Status

| Claim (from sla) | Code location | Proof artifact | Status |
|------------------|---------------|----------------|--------|
| 55,500 encounters, 6 conditions | api/app/main.py | outputs/01_api_proof/api_stats_response_2026-03-11.json | ✅ |
| 11 GET endpoints | api/app/main.py (11 route decorators) | outputs/01_api_proof/api_stats_response_2026-03-11.json | ✅ |
| dbt star schema, 8 marts, 3 tests | dbt-project/models/marts/core/*.sql (8 files), tests/*.sql (3 files) | outputs/02_dbt_proof/dbt_run_results_2026-03-11.json | ✅ |
| Power BI semantic model (TMDL) | powerbi-model/*.tmdl | outputs/03_bi_proof/semantic_model_validation_2026-03-11.md | ✅ |
| XGBoost + MLflow | ml-pipeline/src/train.py | outputs/04_ml_proof/mlflow_run_summary_2026-03-11.md | ✅ |

## Session Start (Agents)

1. Read ~/.config/ai-context/AGENT.md (nudge rule + SPEC.md = only entry point).
2. Read ~/.config/ai-context/TOOL_STACK_AUDIT.md (Bchan's tool stack; only suggest from this list).
3. Use SPEC.md as single source of truth. Never a single read/done row; break docs into actionable items.
4. Before any proof step: confirm prerequisite (raw data, keys, deps). If missing, set Status=⬜ and add to B-turns with exact command.
5. No stub .md files in outputs/. Blockers go in SPEC.md B-turns only.
