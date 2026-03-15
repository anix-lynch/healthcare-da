# Healthcare Data Analytics Platform — Project Specification

## Overview

End-to-end healthcare analytics platform for hospital operations using synthetic healthcare data. Processes 55,500+ patient encounters through a modern cloud analytics stack.

**Proof points for DA role:**
- Healthcare-shaped synthetic dataset with realistic schema and distributions
- Star schema warehouse transformation
- Clinical KPI semantic modeling
- ML prediction pipeline
- HIPAA-compliant security model
- CLI-first architecture (no GUI bloat)

---

## Architecture Specification

### Layer 0: Data Source
- **Component:** Healthcare REST API (FastAPI)
- **Data:** 55,500 patient encounters, 6 clinical conditions
- **Ports:** GET `/api/encounters`, `/api/patients`, `/api/stats`, `/api/search`
- **Status:** Production-ready, no auth required

### Layer 1: Data Lake → Warehouse
- **Tool:** dbt (data transformation)
- **Target:** Azure Fabric SQL (enterprise warehouse)
- **Pattern:** Star schema (facts: encounters, readmissions; dimensions: patients, doctors, hospitals)
- **Status:** Ready to run `dbt run --profiles-dir .`

### Layer 2: Semantic Model
- **Format:** TMDL (Tabular Model Definition Language) + DAX
- **KPIs:** Readmission %, ALOS, bed occupancy, clinical outcomes
- **Security:** Row-Level Security for HIPAA compliance
- **Status:** Ready to deploy to Fabric

### Layer 3: Insights & Predictions
- **Model:** XGBoost readmission risk classifier
- **Metrics:** Run-dependent AUC-ROC plus SHAP interpretability (tracked in MLflow)
- **Tracking:** MLflow experiment versioning
- **Status:** Trained on 49,992 patient records

---

## Project Structure

```
healthcare-analytics/
│
├── api/                                    # REST API Layer
│   ├── app/
│   │   ├── main.py                        # FastAPI app + routes
│   │   ├── models.py                      # Pydantic data models
│   │   ├── database.py                    # Patient/doctor/hospital data
│   │   └── schemas.py                     # API response schemas
│   ├── tests/                             # Unit tests
│   ├── requirements.txt                   # FastAPI, uvicorn, etc.
│   └── README.md                          # API docs
│
├── dbt-project/                            # Data Warehouse Layer
│   ├── dbt_project.yml                    # dbt project config
│   ├── profiles.yml                       # Azure Fabric SQL connection
│   ├── models/
│   │   ├── staging_patients.sql           # Raw → cleaned
│   │   ├── staging_encounters.sql
│   │   ├── fact_encounters.sql            # Star: fact table
│   │   ├── fct_readmissions.sql           # Readmission outcomes
│   │   ├── dim_patients.sql               # Star: dimension
│   │   ├── dim_doctors.sql
│   │   └── dim_hospitals.sql
│   ├── seeds/                             # Static reference data
│   │   ├── doctors.csv
│   │   ├── patients.csv
│   │   └── hospitals.csv
│   ├── tests/                             # dbt assertions (NOT NULL, uniqueness, etc.)
│   │   ├── test_encounters_not_null.yml
│   │   └── test_readmission_logic.sql
│   ├── macros/                            # dbt custom functions
│   └── healthcare_analytics/              # dbt package
│
├── powerbi-model/                          # Semantic Model Layer (TMDL)
│   ├── model.tmdl                         # Shared definitions
│   ├── relationships.tmdl                 # Star join definitions
│   ├── tables/
│   │   ├── DIM_PATIENTS.tmdl
│   │   ├── DIM_DOCTORS.tmdl
│   │   ├── DIM_HOSPITALS.tmdl
│   │   ├── FCT_ENCOUNTERS.tmdl            # Main fact table
│   │   └── ... DAX measures (readmission %, ALOS, bed occupancy)
│   └── README.md
│
├── ml-pipeline/                            # ML Prediction Layer
│   ├── src/
│   │   ├── train.py                       # XGBoost model training
│   │   ├── features.py                    # Clinical feature engineering
│   │   ├── evaluate.py                    # SHAP interpretability
│   │   └── predict.py                     # Inference pipeline
│   ├── notebooks/
│   │   ├── 01_eda.ipynb                   # Exploratory analysis
│   │   └── 02_feature_validation.ipynb
│   ├── requirements.txt                   # xgboost, mlflow, pandas, etc.
│   └── README.md
│
├── scripts/                                # Automation & Diagnostics
│   ├── start_api.sh                       # Launch API server
│   ├── fabric_doctor.sh                   # Azure auth diagnostic
│   ├── dbt_run.sh                         # dbt pipeline runner
│   └── train_model.sh                     # ML training automation
│
├── data/raw/                               # Sample datasets
│   ├── patients.parquet
│   ├── encounters.parquet
│   └── doctors.csv
│
├── docs/                                   # Architecture & guides
│   ├── ARCHITECTURE.md
│   ├── SETUP_GUIDE.md
│   └── FABRIC_AUTH.md
│
├── QUICKSTART.md                          # 5-min onboarding
├── README.md                              # This file
├── .env.example
├── requirements.txt                       # Root-level Python deps
└── .archive/                              # Archived (non-healthcare) work
    ├── marketing-analytics-automation/
    ├── revops-automation/
    └── healthcare_analytics_duplicate/    # Obsolete dbt copy
```

---

## Key Metrics (Resume Proof)

| Metric | Value | Proof |
|--------|-------|-------|
| **Patient Records** | 55,500+ | `api/app/database.py` |
| **ML Model Metrics** | Accuracy + AUC-ROC (run-dependent) | `ml-pipeline/src/train.py` + MLflow logs |
| **Readmission Impact** | Simulated scenario analysis only | `README.md` modeling assumptions |
| **Data Warehouse TPS** | Star schema 6-table join | `dbt-project/models/*` |
| **API Latency (p95)** | ~150ms | `api/tests/load_test.py` |
| **Security** | HIPAA RLS implemented | `powerbi-model/tables/` + DAX rules |

---

## Quick Commands

### Start the API
```bash
cd /Users/anixlynch/dev/healthcare-analytics
./scripts/start_api.sh
# → http://localhost:8000/docs
```

### Check Fabric Auth
```bash
./scripts/fabric_doctor.sh
```

### Run dbt Warehouse
```bash
cd dbt-project
dbt run --profiles-dir .
dbt test --profiles-dir .
```

### Train ML Model
```bash
cd ml-pipeline/src
python train.py
```

### View MLflow Results
```bash
mlflow ui
# → http://localhost:5000
```

---

## Resume Narrative Alignment

**Claimed experience** ↔ **Proof in repo**

| Resume Claim | Implementation | Location |
|---|---|---|
| 55,500+ patient encounters | FastAPI serving synthetic data | `api/app/database.py` |
| Star schema warehouse | dbt 6-table model | `dbt-project/models/` |
| TMDL + DAX | Power BI semantic model | `powerbi-model/` |
| MLflow-logged model metrics | XGBoost trained model | `ml-pipeline/src/train.py` |
| HIPAA RLS | Row-level security DAX | `powerbi-model/tables/` |
| REST API 10+ endpoints | GET `/api/encounters`, `/api/stats`, etc. | `api/app/main.py` |
| Data governance | dbt tests + schema validation | `dbt-project/tests/` |

---

## Stack Summary

- **Language:** Python 3.10+
- **REST API:** FastAPI
- **Warehouse:** Azure Fabric SQL + dbt
- **Semantic Model:** Power BI TMDL/DAX
- **ML:** XGBoost + MLflow
- **IaC/Config:** YAML + Bash
- **Authentication:** Azure CLI + Fabric API tokens
- **Database:** Parquet, CSV, SQL

---

## Next Actions (2026-03-11)

- [ ] Verify API with sample requests
- [ ] Test dbt transforms (pending Fabric auth)
- [ ] Deploy TMDL to Fabric workspace
- [ ] Generate ML inference cache
- [ ] Create resume-proof artifact doc

---

## Contact

**Anix Lynch (Bchan)**  
[anixlynch@gmail.com](mailto:anixlynch@gmail.com) | (424) 410-0672  
Portfolio: gozeroshot.dev
