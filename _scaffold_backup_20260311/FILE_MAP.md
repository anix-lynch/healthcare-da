# 📑 File Map — Which File Does What

**Use this when opening the folder in isolation.**

---

## 📖 Read First (In Order)

1. **HANDOVER.md** ←  **START HERE** (2 min read)
   - What is this folder?
   - Lane context (S1: Data Engineer)
   - Quick orientation

2. **README.md** (5 min read)
   - Full overview
   - Resume narrative
   - Architecture diagram

3. **REPO_CHECKLIST.md** (3 min read for reference)
   - Interview demo script (5 min to run)
   - Resume claims ↔ code locations
   - What's kept, what's archived

---

## 🏗️ Implementation Files

### Layer 0: REST API
- **Location:** `api/`
- **Key files:** `api/app/main.py` (endpoints), `api/app/database.py` (55K records)
- **Run:** `./scripts/start_api.sh`
- **Test:** `curl http://localhost:8000/api/stats`

### Layer 1: Data Warehouse (dbt)
- **Location:** `dbt-project/`
- **Key files:**
  - `dbt-project/models/staging/stg_healthcare.sql` (raw → clean)
  - `dbt-project/models/intermediate/int_*.sql` (business logic)
  - `dbt-project/models/marts/fact_*.sql` + `dim_*.sql` (star schema)
- **Run:** `cd dbt-project && dbt run --profiles-dir .`

### Layer 2: Semantic Model (TMDL)
- **Location:** `powerbi-model/`
- **Key files:** `powerbi-model/tables/*.tmdl` (DAX measures)
- **Don't use:** Power BI GUI (use TMDL text files only)
- **View:** `cat powerbi-model/tables/Patient\ Encounters.tmdl`

### Layer 3: ML Pipeline (XGBoost)
- **Location:** `ml-pipeline/`
- **Key files:** `ml-pipeline/src/train.py`, `ml-pipeline/src/score.py`
- **Run:** `cd ml-pipeline/src && python train.py`

---

## 🔧 Automation Scripts

| Script | Purpose | Run |
|--------|---------|-----|
| `scripts/start_api.sh` | Launch REST API | `./scripts/start_api.sh` |
| `scripts/fabric_doctor.sh` | Check Azure/Fabric auth | `./scripts/fabric_doctor.sh` |
| `scripts/resume-proof-verification.sh` | Verify all resume claims | `./scripts/resume-proof-verification.sh` |

---

## 📊 Reference Docs

| File | Purpose | Length |
|------|---------|--------|
| `README.md` | Full project overview + narrative | 5 min |
| `QUICKSTART.md` | Setup & installation guide | 5 min |
| `project-spec.md` | Full architecture specification | 10 min |
| `REPO_CHECKLIST.md` | Interview demo checklist (verified) | 3 min read / 5 min run |
| `.instructions.md` | Agent context (for Copilot) | 3 min |
| `HANDOVER.md` | Context-switching card (you are here) | 2 min |

---

## 🎯 I Want To...

### ...understand the project
→ Read `README.md` then `REPO_CHECKLIST.md`

### ...interview demo (5 min)
→ Follow `REPO_CHECKLIST.md` step-by-step

### ...verify a resume claim
→ Run `./scripts/resume-proof-verification.sh`

### ...check if I can run it
→ Run `./scripts/start_api.sh` (quickest test)

### ...fix Fabric auth
→ Run `./scripts/fabric_doctor.sh`

### ...explore dbt models
→ `cd dbt-project && dbt compile` or `dbt docs generate`

### ...understand architecture deeply
→ Read `project-spec.md` (comprehensive)

### ...understand cost/constraints
→ See `.instructions.md` (no GUI, no auth hell)

---

## 📍 Where Are The 4 Resume Claims?

| Claim | Where | How to Verify |
|-------|-------|---------------|
| 55,500+ patient encounters | `api/app/database.py` | `./scripts/start_api.sh` → GET /api/stats |
| Star schema (8 dims + fact) | `dbt-project/models/marts/` | `cd dbt-project && dbt compile --select fact_*` |
| TMDL + DAX semantic model | `powerbi-model/tables/` | `cat powerbi-model/tables/Patient\ Encounters.tmdl` |
| MLflow-logged ML metrics (accuracy + AUC-ROC) | `ml-pipeline/src/train.py` | `python ml-pipeline/src/train.py` → see logged metrics |

---

## ⚡ TL;DR

1. Read `HANDOVER.md` (2 min)
2. Run `./scripts/start_api.sh` (see it works)
3. Follow `REPO_CHECKLIST.md` for interview (5 min)
4. Done! ✅

---

**Last updated:** 2026-03-10
