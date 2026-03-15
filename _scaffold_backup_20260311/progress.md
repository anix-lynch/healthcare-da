# SPEC: Healthcare Analytics Progress Tracker
> Single source of truth for execution status and intervention points. Last sync: 2026-03-10

**Progress:** Setup is complete. API, dbt, BI, and ML proof capture are next. Use this file as the working tracker, not just a template.

**3 birds, 1 stone:**
- Healthcare DA
- C10 Analytics Engineer
- DINO / classic Data Engineer

---

## Quick Context
- Feature path: specs/001-project-checklist/spec.md
- Branch: 001-project-checklist
- Rule: keep language plain and action-first

---

## Phase 0 - Setup (done)

- [x] Run `specify check` and confirm it passes in this workspace.
- [x] Keep branch naming compliant with Spec Kit (`001-project-checklist`).
- [x] Confirm Spec Kit pathing resolves to this project, not parent repos.
- [ ] (b-turn) Confirm secrets are loaded in your shell before external calls.

## Phase 1 - API proof

- [ ] Write the exact FastAPI start command and health-check method used today.
- [ ] Save 2-3 real API examples (request + response) as proof.
- [ ] (b-turn) Run API checks that require your credentials or explicit approval.

## Phase 2 - dbt and warehouse proof

- [ ] List exact dbt run/test commands and profile setup.
- [ ] Confirm data checks are covered: negative LOS, readmission logic, discharge after admission.
- [ ] (b-turn) Run Fabric-auth steps and record pass/fail outcome.

## Phase 3 - Semantic model proof

- [ ] Validate TMDL relationships against the current warehouse schema.
- [ ] Map KPI definitions (Readmission %, ALOS, occupancy) to concrete proof artifacts.
- [ ] (b-turn) Confirm Power BI/Fabric deployment and manual validation status.

## Phase 4 - ML proof

- [ ] Record training/scoring entry points and expected outputs.
- [ ] Attach target metrics and model evidence (MLflow or registry output).
- [ ] (b-turn) Approve parameters before any cost-impacting retraining.

## Phase 5 - Final handover

- [x] Lock resume bullets in `sla` with claim-to-code traceability.
- [ ] Link final evidence: logs, run outputs, screenshots, and metrics.
- [ ] Update handover with done, blocked, and next actions.
- [ ] (b-turn) Make go/no-go decision and set next intervention priority.

---

## B-turns Pending
1. Secrets loaded check
2. Credentialed API checks
3. Fabric-auth run
4. BI deployment confirmation
5. Retraining approval
6. Go/no-go decision
