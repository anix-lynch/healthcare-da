# 🤝 Handover Card — Healthcare DA Portfolio

**Scenario:** You're closing the full workspace and opening ONLY this folder in a fresh session.

---

## What Is This?

**Healthcare Data Analyst portfolio** — proof of 4-layer analytics stack for LA healthcare DA interviews.

Not ML research. Not generic code. Pure data engineering.

---

## Lane (If You're Bchan's Agent)

**Sprint Lane S1:** AI Data Engineer (warehousing, feature stores, data quality)

**Not these lanes:**
- ❌ S2: GenAI/Agent/LLM (separate project)
- ❌ S3: DevRel/writing (separate project)  
- ❌ S4: n8n automation (separate project)

---

## 5-Minute Orientation

**What's where:**
- `README.md` — 5-min overview
- `sla` — locked resume bullets + claim-to-code map
- `.instructions.md` — This folder's agent context (you're reading it now)
- `REPO_CHECKLIST.md` — Interview demo script (verified)
- `scripts/*.sh` — CLI entry points

**The 4 layers:**
1. **api/** — 55K patient records via FastAPI
2. **dbt-project/** — Star schema warehouse (SQL)
3. **powerbi-model/** — TMDL semantic model (no GUI!)
4. **ml-pipeline/** — XGBoost model with MLflow metric logging

---

## Run Something Now

```bash
# Quickest demo (1 minute)
./scripts/start_api.sh
curl http://localhost:8000/api/stats
```

Result: See 55,500 patient record counts. ✅

---

## Full Interview Demo (5 min)

See `REPO_CHECKLIST.md` for step-by-step script.

**Order:**
1. API → 55K records
2. Warehouse → star schema
3. Semantic → TMDL + DAX
4. ML → model training
5. Verify → resume-proof-verification.sh

---

## Constraints (No GUI Hell)

- ✅ Power BI TMDL files (text-based) — edit freely
- ❌ Power BI Semantic Modeler GUI — NOT ALLOWED
- ✅ dbt CLI — use normally
- ✅ FastAPI docs — browser OK (localhost:8000/docs)
- ✅ MLflow UI — browser OK (localhost:5000)

---

## If Something Breaks

1. **Fabric/Azure auth issue?**
   - Run: `./scripts/fabric_doctor.sh` (shows what's missing)
   - Skip Fabric layer if needed (other 3 layers still work)

2. **dbt models won't compile?**
   - Check: `cd dbt-project && dbt debug`
   - Profiles.yml likely needs credentials (Fabric SQL)

3. **API won't start?**
   - Run: `pip install -r api/requirements.txt`
   - Then: `./scripts/start_api.sh`

4. **ML training fails?**
   - Run: `pip install -r ml-pipeline/requirements.txt`
   - Then: `cd ml-pipeline/src && python train.py`

---

## Resume Claims Verification

```bash
# Run all at once
./scripts/resume-proof-verification.sh
```

Maps every resume claim → code location → demo command.

---

## Context Files (If You Need Deep Context)

**In this folder:**
- `.instructions.md` (you are here)
- `README.md` (overview)
- `REPO_CHECKLIST.md` (interview flow)
- `project-spec.md` (architecture deep-dive)

**Outside this folder (full context):**
- `~/.config/ai-context/AGENT.md` — Who Bchan is, all 4 lanes
- `/Users/anixlynch/dev/06devrel/orbit_karma/set and forget` — Career strategy
- `/Users/anixlynch/.config/secrets/global.env` — API keys (if needed)

---

## Quick Checklist

Before you start work:

- [ ] Can cd into this folder and see 4 layers
- [ ] Can run `./scripts/start_api.sh` (test API)
- [ ] Can run `./scripts/resume-proof-verification.sh` (verify claims)
- [ ] REPO_CHECKLIST.md makes sense (interview flow)

---

## One More Thing

**This is NOT production code** — it's portfolio proof on synthetic data.

Every component exists to answer: **"Can you build & own a healthcare data stack?"**

Answer: Yes. Here's the code. Let me demo it.

---

**Status:** ✅ Ready to open in isolated workspace  
**Confidence:** High (agent will understand context immediately)
