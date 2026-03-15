# Healthcare DA Platform - Quick Start

## ✅ Move Fast (CLI Only)

### 1. Start API
```bash
./scripts/start_api.sh
# → 55K patient records at http://localhost:8000/docs
```

### 2. Check Fabric Ready
```bash
./scripts/fabric_doctor.sh
# Validates: Azure CLI auth → Power BI token → Workspace access → Warehouse
```

### 3. Run dbt Transforms
```bash
cd dbt-project
dbt run --profiles-dir .
dbt test --profiles-dir .
```

### 4. Train ML Model
```bash
cd ml-pipeline/src
source ../../.venv/bin/activate
python train.py
mlflow ui  # → http://localhost:5000
```

### 5. Deploy TMDL Model
```bash
# TMDL files in ../powerbi-model/ ready to deploy to Fabric
# No GUI needed — all CLI
```

---

## ⏳ Auth Issues? Run Doctor

If `dbt run` fails with Azure auth errors:

```bash
./scripts/fabric_doctor.sh
```

This will tell you:
- ✅ or ❌ Azure CLI authenticated
- ✅ or ❌ Power BI scope token available
- ✅ or ❌ Workspace visible
- ✅ or ❌ Warehouse exists

**Fix:** If warehouse missing, create one:
1. https://app.fabric.microsoft.com/groups/577de43f-21b4-479e-99b6-ea78f32e5216
2. Click "New" → "Warehouse"
3. Name: `HealthcareWarehouse`
4. Assign Trial capacity
5. Re-run: `dbt run --profiles-dir .`

---

## 📊 What's Running

- **API:** 55K patient records, searchable
- **dbt:** Star schema (patients, encounters, readmissions)
- **ML:** XGBoost readmission risk model
- **Power BI:** TMDL semantic model ready for deployment

---

## 🎯 For Demos

```bash
# Get patient stats
curl http://localhost:8000/api/stats

# Search by condition
curl "http://localhost:8000/api/encounters?condition=Diabetes&limit=5"

# View ML results
open http://localhost:5000  # MLflow
```

---

See [README.md](README.md) for architecture + full docs.
cd dbt-project
export FABRIC_SERVER="your-warehouse.datawarehouse.pbidedicated.windows.net"
export $(cat /Users/anixlynch/.config/secrets/fabric.env | xargs)
dbt run
dbt test
```

### Decision checkpoint
- If doctor passes and dbt runs, continue Fabric path.
- If doctor keeps failing after one focused session, treat this as a documented fail case and continue with API-first analytics path.

## 📚 Documentation
- `docs/BUILD_COMPLETE.md` - Full summary
- `docs/FABRIC_SETUP_FIX.md` - Capacity fix guide
- `docs/CURRENT_STATUS.md` - Detailed status

## 🎯 Status
- **Code:** 100% complete
- **Tested:** ML ✅, API ✅, dbt ⏳ (waiting on Fabric)
- **Deployed:** 50% (API + ML working, dbt + TMDL waiting on capacity)
