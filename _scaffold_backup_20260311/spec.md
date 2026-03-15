# SPEC: Healthcare Analytics Progress Tracker

Last updated: 2026-03-11

## Goal
Ship a single execution tracker that proves API, dbt, semantic model, and ML claims with clear phase ownership and explicit b-turn checkpoints.

## Inputs

| Input | Source | Used For | Status |
|---|---|---|---|
| Global environment secrets | ~/.config/secrets/global.env | Azure auth, Fabric checks, optional external API calls | ⬜ Validate loaded in active shell |
| Workspace context and rules | ~/.config/ai-context/AGENT.md, ~/.config/ai-context/VSCODE_SPEC_SCAFFOLD_RULES.md | Session behavior, spec-checklist and scaffold execution policy | ✅ Loaded |
| Project orientation docs | START_HERE.md, HANDOVER.md, QUICKSTART.md, REPO_CHECKLIST.md, project-spec.md | Scope baseline and executable proof flow | ✅ Loaded |

## Outputs

| Output | Path | Owner |
|---|---|---|
| Canonical progress spec | specs/001-project-checklist/spec.md | AI |
| Execution dashboard scaffold | DASHBOARD.md | AI |
| Input placeholders with real expected filenames + context | inputs/ | AI |
| Output placeholders with real expected deliverable names + context | outputs/ | AI |
| Updated phase status report | specs/001-project-checklist/checklists/progress.md | AI |

## Phase Gates

| Phase | Gate | Status | Who |
|---|---|---|---|
| P0 Context Sweep | Confirm source-of-truth docs were ingested: START_HERE, HANDOVER, QUICKSTART, REPO_CHECKLIST, project-spec | ✅ | AI |
| P0 Context Sweep | Confirm tool-stack offload check completed from ~/.config/ai-context/TOOL_STACK_AUDIT.md | ✅ | AI |
| P1 Spec Canonicalization | Rewrite feature spec to canonical Goal, Inputs, Outputs, Phase Gates, File Map, B-turns, Session Start | ✅ | AI |
| P2 API Proof | Start API and capture stats response evidence file | ⬜ | ~~Bchan~~ -> AI with scripts/start_api.sh |
| P2 API Proof | Save 2-3 endpoint examples for interview flow | ⬜ | AI |
| P3 dbt Proof | Run dbt compile/run/test and persist run results artifact | ⬜ | ~~Bchan~~ -> AI with dbt CLI |
| P3 dbt Proof | Validate data-quality checks: LOS non-negative, discharge after admission, readmission logic | ⬜ | AI |
| P4 Semantic Model Proof | Validate TMDL relationship and KPI mapping against warehouse model | ⬜ | AI |
| P4 Semantic Model Proof | Confirm Fabric deployment pass/fail status | ⏸️ | b-turn |
| P5 ML Proof | Run train.py and capture MLflow run summary evidence | ⬜ | AI |
| P6 Final Handover | Update progress tracker + attach evidence links for all 4 layers | ⬜ | AI |
| P6 Final Handover | Approve go/no-go for interview-ready lock | ⏸️ | b-turn |

## File Map

| Purpose | Path |
|---|---|
| Primary progress spec | specs/001-project-checklist/spec.md |
| Rolling checklist state | specs/001-project-checklist/checklists/progress.md |
| Interview demo script | REPO_CHECKLIST.md |
| End-to-end architecture detail | project-spec.md |
| Resume claim lock | sla |
| API layer | api/ |
| dbt warehouse layer | dbt-project/ |
| Semantic model layer | powerbi-model/ |
| ML layer | ml-pipeline/ |

## B-turns Pending

1. Confirm global env secrets are loaded in the active shell.
2. Confirm Fabric workspace/deployment outcome for semantic model phase.
3. Approve final go/no-go lock after evidence artifacts are attached.

## Session Start (Agents)

1. Read ~/.config/ai-context/AGENT.md.
2. If user says spec checklist or full scaffold, read ~/.config/ai-context/VSCODE_SPEC_SCAFFOLD_RULES.md and execute the matching workflow.
3. Run tool-stack offload check via ~/.config/ai-context/TOOL_STACK_AUDIT.md before proposing repetitive manual work.
