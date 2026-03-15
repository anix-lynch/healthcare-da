START HERE — Healthcare DA Portfolio
=====================================

Source of truth for interview claims: `sla`

**You're in:** `/Users/anixlynch/dev/06devrel/orbit_karma/Powerbi/healthcare-da`

**Everything you need is in THIS FOLDER.**

---

## ⚡ Quick Start (Pick One)

### 🎓 New to this? (5 min orientation)
1. Read: `HANDOVER.md` (context)
2. Read: `README.md` (overview)
3. Run: `./scripts/start_api.sh` (see it work)

### 🎬 Interview demo? (5 min execution)
1. Read: `sla` (locked resume bullets + claim-to-code map)
2. Follow: `REPO_CHECKLIST.md` (step-by-step)
2. Done ✅

### 🔍 Find something specific?
→ See: `FILE_MAP.md` (where everything is)

---

## 📂 Everything Here

### Documentation (Read)
- **`.instructions.md`** — Agent context (Copilot will read this)
- **`HANDOVER.md`** — Orientation card (start here if new)
- **`README.md`** — Full overview (5 min read)
- **`REPO_CHECKLIST.md`** — Interview demo script
- **`FILE_MAP.md`** — Navigation reference
- **`QUICKSTART.md`** — Setup guide
- **`project-spec.md`** — Architecture deep-dive

### Code (Run)
- **`api/`** — REST API (55K patient records)
- **`dbt-project/`** — Data warehouse (star schema)
- **`powerbi-model/`** — TMDL semantic model
- **`ml-pipeline/`** — XGBoost + MLflow
- **`scripts/`** — Automation (start_api.sh, fabric_doctor.sh, etc.)
- **`data/`** — Sample datasets

---

## 🚀 I Want To...

### ...understand the project (5 min)
```bash
cat HANDOVER.md
cat README.md
```

### ...see it work (1 min)
```bash
./scripts/start_api.sh
# → visit http://localhost:8000/docs
```

### ...do interview demo (5 min)
```bash
# Follow steps in REPO_CHECKLIST.md
```

### ...verify resume claims (1 min)
```bash
cat sla
./scripts/resume-proof-verification.sh
```

### ...find a specific file
```bash
cat FILE_MAP.md
```

---

## ✅ Verification

All files here:
```bash
ls -la *.md .instructions.md
# Should see: 7 markdown files + .instructions.md
```

Can run immediately:
```bash
./scripts/start_api.sh
./scripts/fabric_doctor.sh
./scripts/resume-proof-verification.sh
```

---

## 🎯 Lane Context

**This is Lane S1: AI Data Engineer**

Not ML research. Not GenAI. Not DevRel. Pure data engineering.

→ See `.instructions.md` for full context

---

**Status:** ✅ READY  
**Everything in folder:** ✅ YES  
**Can run immediately:** ✅ YES  

**Next step:** Pick above and go! 🚀
