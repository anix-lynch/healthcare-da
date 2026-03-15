# Healthcare DA Repo — Lean Verification Checklist

**Purpose:** Prove 4 resume claims with minimal bloat. No GUI hell. All CLI.

---

## ✅ LAYER 0: REST API (55,500+ patient records)

- [x] FastAPI app running
- [x] 11 GET endpoints (`/`, `/api/encounters`, `/api/stats`, `/api/search`, etc.)
- [x] Sample data loaded (55,500 encounters, 6 conditions)
- [x] Location: `api/app/main.py` + `api/app/database.py`

**Start:** `./scripts/start_api.sh` → http://localhost:8000/docs

---

## ✅ LAYER 1: dbt Data Warehouse (Star Schema)

**Staging →  Intermediate → Marts (Facts + Dims)**

### Staging
- [x] `stg_healthcare.sql` - Raw → cleaned data

### Intermediate (Business Logic)
- [x] `int_encounters_enriched.sql` - Enriched encounters
- [x] `int_readmissions.sql` - Readmission logic

### Star Schema (Analytics)

**Facts:**
- [x] `fact_patient_encounters.sql` - Main fact table

**Dimensions:**
- [x] `dim_patient.sql` - Patient attributes
- [x] `dim_doctor.sql` - Doctor info
- [x] `dim_hospital.sql` - Hospital info
- [x] `dim_date.sql` - Time dimension
- [x] `dim_diagnosis.sql` - Clinical codes
- [x] `dim_medication.sql` - Medication reference
- [x] `dim_insurance.sql` - Insurance providers

**Run dbt:** `cd dbt-project && dbt run --profiles-dir . && dbt test --profiles-dir .`

---

## ✅ LAYER 2: Power BI TMDL Semantic Model

**TMDL files (no GUI):**
- [x] `model.tmdl` - Shared model definitions
- [x] `relationships.tmdl` - Star join definitions
- [x] `tables/Date.tmdl` - Time dimension DAX
- [x] `tables/Patient.tmdl` - Clinical attributes
- [x] `tables/Doctor.tmdl` - Provider info
- [x] `tables/Hospital.tmdl` - Organization info
- [x] `tables/Patient Encounters.tmdl` - Fact table + measures

**DAX Measures (KPIs):**
- [x] Readmission %
- [x] Average Length of Stay (ALOS)
- [x] Bed occupancy rate

**Deploy:** `cd powerbi-model && fabric deploy` (once Fabric auth is fixed)

---

## ✅ LAYER 3: ML Pipeline (XGBoost + MLflow)

- [x] `train.py` - XGBoost model training (49,992 records)
- [x] `score.py` - Model inference
- [x] MLflow experiment tracking
- [x] SHAP interpretability

**Metrics:**
- [x] Accuracy and AUC-ROC are logged to MLflow per run
- [x] Readmission risk prediction workflow is reproducible

**Run:** `cd ml-pipeline/src && python train.py`

---

## ✅ SECURITY & COMPLIANCE

- [x] HIPAA RLS in Power BI TMDL
- [x] CLI-only (no GUI security debt)
- [x] Fabric doctor diagnostic tool
- [x] Environment secrets management

---

## ✅ SCRIPTS (Automation)

- [x] `start_api.sh` - Launch REST API
- [x] `fabric_doctor.sh` - Azure/Fabric auth diagnostic
- [x] `resume-proof-verification.sh` - This checklist (automated)

---

## 📊 Interview Demo Flow

**Duration: 5 minutes**

### 1. API (1 min)
```bash
./scripts/start_api.sh
curl http://localhost:8000/api/stats
```
→ Shows 55K patient records

### 2. Warehouse (1 min)
```bash
cd dbt-project
dbt compile --select fact_patient_encounters
```
→ Shows star schema SQL

### 3. Semantic Model (1 min)
```bash
cat powerbi-model/tables/Patient\ Encounters.tmdl
```
→ Shows DAX measures (readmission %, ALOS)

### 4. ML Model (1 min)
```bash
cd ml-pipeline/src
python train.py | tail -10
```
→ Shows AUC-ROC, feature importance

### 5. Compliance (1 min)
```bash
./scripts/fabric_doctor.sh
```
→ Shows Fabric auth + RLS config

---

## 📁 What's NOT in this repo (intentionally)

- ❌ Marketing analytics (archived in `.archive/`)
- ❌ RevOps automation (archived in `.archive/`)
- ❌ Duplicate folders
- ❌ GUI-based Power BI configuration files (TMDL only)
- ❌ Unused notebooks or exploratory junk

---

## 🎯 Resume Alignment

| Resume Claim | Proof in Repo | Status |
|---|---|---|
| 55,500+ patient encounters | `api/app/database.py` | ✅ |
| Star schema warehouse | `dbt-project/models/marts/` | ✅ |
| TMDL + DAX semantic model | `powerbi-model/tables/` | ✅ |
| XGBoost + MLflow metric logging | `ml-pipeline/src/train.py` | ✅ |
| HIPAA RLS | `powerbi-model/tables/*.tmdl` + DAX | ✅ |
| REST API 10+ endpoints | `api/app/main.py` | ✅ |
| Production-ready | All runnable CLI commands | ✅ |

---

## 🚀 Ready for LA Healthcare DA Interviews

This repo is **production-proof**, **interview-ready**, and **pure data engineering** (no ML buzzword nonsense).

**Talking points:**
- "I built this end-to-end: API → warehouse → BI → ML"
- "55K synthetic patient records, clearly labeled, with governance-style controls"
- "Can run everything from CLI (no Fabric GUI debt)"
- "MLflow logs accuracy/AUC every run; I report the exact run used in resume"

---

**Last Updated:** 2026-03-10  
**Status:** LEAN & READY
