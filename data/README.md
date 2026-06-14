# Data — see the records yourself

Real openFDA FAERS adverse-event reports (US FDA public API, `api.fda.gov/drug/event.json` —
20.3M real reports total; this is a 3,000-report sample). **Not synthetic.** Verify any
`safetyreportid` on the FDA FAERS public dashboard.

| file | what it is |
|---|---|
| `sample_openfda_raw.jsonl` | 50 raw openFDA records exactly as the API returns them — nested 6 levels deep, the real mess |
| `bronze_adverse_events.jsonl` | 11,523 drug rows, raw — **`drug_name_raw` is 14.4% null** (the dirty ingest) |
| `silver_adverse_events.jsonl` | same 11,523 rows after the trust layer — **`drug_name` 0% null** (coalesce generic_name→medicinalproduct) |

Before/after in one line:
```bash
grep -c '"drug_name_raw": null' bronze_adverse_events.jsonl   # 1654  (14.4%)
grep -c '"drug_name": null'     silver_adverse_events.jsonl   # 0
```
Full 3,000-report dataset lives in BigQuery `healthcare_analytics` + OneLake; regenerate with `pipeline/build_openfda_marts.py`.
