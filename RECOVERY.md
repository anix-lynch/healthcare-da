# Recovery & Backup — what survives the Fabric trial expiry

The Microsoft Fabric trial capacity expires ~15 days after activation. Here's what is
permanent, what dies, and how to rebuild — so nothing real is ever lost.

## What is permanent (backed up already)
| where | holds | survives Fabric expiry? |
|---|---|---|
| **GitHub** (this repo) | `model/model.bim` (semantic model def) · `model/report.pbir` (report def) · all `pipeline/*.py` · `data/*` samples · `proof/*` · `contracts/*` | ✅ yes |
| **GCP BigQuery** `healthcare_analytics` | every table: bronze/silver/fact/dims/bridge/mart (full 3,000-report data) | ✅ yes (GCP ≠ Fabric) |

## What dies with the trial
- The **live Fabric workspace** (running Direct Lake model `c11d0c74`, report `ef468dc5`, OneLake Delta tables).
- These are **reproducible** — they were all deployed *from code*, not hand-built.

## The only non-reproducible asset → capture before expiry
- **Screenshots** of the Fabric Model view / Lineage / Lakehouse / DAX — there is no headless export.
  Capture them now into `images/`.

## How to rebuild on a fresh Fabric capacity (disaster recovery)
```bash
az login --use-device-code                  # delegated user token (executeQueries needs a user)
python pipeline/build_openfda_marts.py      # openFDA → BigQuery (or skip — BigQuery already has it)
python pipeline/build_medallion.py          # bronze (dirty) + silver (clean) → BigQuery
python pipeline/ingest_to_onelake.py        # BigQuery → OneLake Delta  (point at the new lakehouse)
python pipeline/build_semantic_model.py     # deploy model.bim → new model (fact + dims + bridge + relationships)
python pipeline/deploy_report.py            # deploy report.pbir
python pipeline/benchmark_dax.py            # re-bench DAX
```
Everything regenerates from code + the committed `model.bim`. The data is already safe in BigQuery.

## To download the raw Fabric data right now (optional belt-and-suspenders)
OneLake Delta tables are also in BigQuery; or pull any table to a file:
```bash
bq extract --destination_format=NEWLINE_DELIMITED_JSON \
  healthcare_analytics.silver_adverse_events gs://<bucket>/silver.jsonl
```
