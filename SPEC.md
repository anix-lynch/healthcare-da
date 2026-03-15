# SPEC: Healthcare Analytics Progress Tracker

**👤 25% you · 🤖 75% agent** — Bchan: az login once (unlocks P4), P6 approve. Rest = AI.

Last updated: 2026-03-15

## Goal

Ship an interview-ready, evidence-backed healthcare analytics stack (API → dbt → semantic model → ML) with a single execution tracker; every claim traceable to code per **sla** (locked bullets + claim-to-code map).

## Where we are · Next step

| Step | Done | Next |
| ---- | ---- | ---- |
| P0 Context + keys | ✅ | |
| P1 Scaffold repair | ✅ | |
| P2 API proof | ✅ | |
| P3 dbt proof | ✅ | |
| P4 Semantic model proof | ✅ | |
| P5 ML proof | ✅ | |
| P6 Final interview lock | ✅ | |

## Inputs


| Input                   | Where it lives                                                       | Status | Who | Notes                                             |
| ----------------------- | -------------------------------------------------------------------- | ------ | --- | ------------------------------------------------- |
| API export snapshot     | inputs/01_api_export/encounters_export_2026-03-11.json               | ✅      | AI  | Current sample export captured.                   |
| Fabric profile snapshot | inputs/02_fabric_profile/fabric_workspace_connection_2026-03-11.json | ✅      | AI  | Workspace metadata present.                       |
| Semantic model source   | inputs/03_semantic_model/healthcare_semantic_model_v1.tmdl           | ✅      | AI  | TMDL source available for validation.             |
| ML training snapshot    | inputs/04_ml_training_snapshot/                                      | ✅      | AI  | Snapshot folder exists for model reproducibility. |
| AZURE_TENANT_ID         | ~/.config/secrets/global.env                                         | ✅      | AI  | Verified present. Unlocks: Fabric/Power BI auth.  |
| AZURE_SUBSCRIPTION_ID   | ~/.config/secrets/global.env                                         | ✅      | AI  | Verified present.                                 |
| AZURE_CLIENT_ID         | ~/.config/secrets/global.env                                         | ✅      | AI  | Verified present (Fabric-PowerBI app).            |
| AZURE_CLIENT_SECRET     | ~/.config/secrets/global.env                                         | ✅      | AI  | Verified present.                                 |
| FABRIC_WORKSPACE_ID     | ~/.config/secrets/fabric.env                                         | ✅      | AI  | Present in fabric.env.                            |
| FABRIC_REGION           | ~/.config/secrets/global.env                                         | ⬜      | —   | Optional. Not used by scripts. |
| FABRIC_CAPACITY_SKU     | ~/.config/secrets/global.env                                         | ⬜      | —   | Optional. Not used by scripts. |
| az login (session)      | —                                                                     | ✅      | b-turn | Unlocks: AI runs P4 script (check_p4_semantic_model.sh). |


## Outputs


| Output                      | Where it lives                                                  | Status | Who    | Notes                                   |
| --------------------------- | --------------------------------------------------------------- | ------ | ------ | --------------------------------------- |
| API proof stats             | outputs/01_api_proof/api_stats_response_2026-03-11.json         | ✅      | AI     | Baseline evidence captured.             |
| dbt run proof               | outputs/02_dbt_proof/dbt_run_results_2026-03-11.json            | ✅      | AI     | dbt proof artifact captured.            |
| Semantic model validation   | outputs/03_bi_proof/semantic_model_validation_2026-03-11.md     | ✅      | AI     | P4 script passed: 1 dataset (Healthcare Semantic Model) in workspace. |
| MLflow run summary          | outputs/04_ml_proof/mlflow_run_summary_2026-03-11.md            | ✅      | AI     | Training evidence captured.             |
| Resume claim traceability   | outputs/05_resume_proof/resume_claim_traceability_2026-03-11.md | ✅      | AI     | Claim-to-proof lock present.            |
| Warehouse/BI schema summary | outputs/02_schema/healthcare_analytics_schema_2026-03-11.md     | ✅      | AI     | Consolidated from legacy docs.          |
| Repository mapping summary  | outputs/02_mapping/repo_mapping_2026-03-11.md                   | ✅      | AI     | Consolidated from legacy docs.          |


## Phase Gates


| Phase                   | Gate                                                                                       | Status | Who    |
| ----------------------- | ------------------------------------------------------------------------------------------ | ------ | ------ |
| P0 Context + keys       | Read AGENT.md, TOOL_STACK_AUDIT.md; verify global.env and fabric.env for Fabric/Azure keys | ✅      | AI     |
| P1 Scaffold repair      | Backup legacy scaffold markdown and create canonical SPEC.md                               | ✅      | AI     |
| P2 API proof            | Verify API stats endpoint evidence is present                                              | ✅      | AI     |
| P3 dbt proof            | Verify dbt run evidence is present                                                         | ✅      | AI     |
| P4 Semantic model proof | AI runs `./scripts/check_p4_semantic_model.sh`. Unlocks: Bchan runs `az login` once. | ✅      | AI     |
| P5 ML proof             | Verify MLflow summary evidence is present                                                  | ✅      | AI     |
| P6 Final interview lock | Approve end-to-end go/no-go (human decision only)                                         | ✅      | b-turn |


## File Map

- **sla** — Locked resume bullets + claim-to-code traceability (source of truth for interview claims).
- SPEC.md (single source of truth for progress)
- DASHBOARD.md (phase summary + flow with current pointer)
- inputs/01_api_export, inputs/02_fabric_profile, inputs/03_semantic_model, inputs/04_ml_training_snapshot
- outputs/01_api_proof, outputs/02_dbt_proof, outputs/02_schema, outputs/02_mapping, outputs/03_bi_proof, outputs/04_ml_proof, outputs/05_resume_proof
- api/, dbt-project/, powerbi-model/, ml-pipeline/, scripts/

## B-turns Pending

( none )

## Session Start (Agents)

1. Read ~/.config/ai-context/AGENT.md.
2. Read ~/.config/ai-context/TOOL_STACK_AUDIT.md.
3. Use SPEC.md as the single source of truth for project status. Never a single read/done row; break docs into actionable items.

