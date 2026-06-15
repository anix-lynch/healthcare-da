#!/usr/bin/env python3
"""Measure the semantic layer's value, don't estimate it.

For a set of typical drug-safety questions, compare what a human or an LLM must compose:
  - SEMANTIC path: call a named, governed measure with a slicer  (e.g. [Serious Rate], filter Drug)
  - RAW-SQL path:  hand-write the join + filter + aggregate over the star schema

We measure two honest complexity proxies per question:
  - tokens   (whitespace-token count of the query the model/user must emit)
  - surfaces (distinct tables/joins the author must reason about)

Output proof/semantic_complexity.json with the median reduction ratio — a real, reproducible
number to back the resume bullet, instead of a guessed "2-4x".

Run:  python3 pipeline/semantic_complexity_bench.py
"""
import json
import statistics
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "proof/semantic_complexity.json"

# 10 typical drug-safety questions, each in both forms. SQL is the minimal correct query over the
# committed star schema (fact_adverse_events + dim_drug/reaction/country/date + bridge).
QUESTIONS = [
    {
        "q": "What is the serious rate for a given drug?",
        "semantic": "[Serious Rate (event-weighted)] WHERE Drug = @drug",
        "sql": "SELECT SUM(CASE WHEN f.is_serious THEN 1 ELSE 0 END)*1.0/COUNT(*) FROM fact_adverse_events f JOIN dim_drug d ON f.primary_drug = d.drug_name WHERE d.drug_name = @drug",
        "tables": ["fact_adverse_events", "dim_drug"],
    },
    {
        "q": "How many reports per country?",
        "semantic": "[Reports] BY Country",
        "sql": "SELECT c.country, COUNT(*) FROM fact_adverse_events f JOIN dim_country c ON f.occurcountry = c.country_key GROUP BY c.country",
        "tables": ["fact_adverse_events", "dim_country"],
    },
    {
        "q": "Top reactions for a drug?",
        "semantic": "[Reports] BY Reaction WHERE Drug = @drug ORDER BY [Reports] DESC",
        "sql": "SELECT r.reaction_name, COUNT(*) FROM fact_adverse_events f JOIN dim_drug d ON f.primary_drug = d.drug_name JOIN bridge_report_reaction b ON f.safetyreportid = b.safetyreportid JOIN dim_reaction r ON b.reaction_id = r.reaction_id WHERE d.drug_name = @drug GROUP BY r.reaction_name ORDER BY COUNT(*) DESC",
        "tables": ["fact_adverse_events", "dim_drug", "bridge_report_reaction", "dim_reaction"],
    },
    {
        "q": "Serious rate by quarter?",
        "semantic": "[Serious Rate (event-weighted)] BY Date[year], Date[quarter]",
        "sql": "SELECT dt.year, ((dt.month-1)/3)+1 AS quarter, SUM(CASE WHEN f.is_serious THEN 1 ELSE 0 END)*1.0/COUNT(*) FROM fact_adverse_events f JOIN dim_date dt ON f.received_date = dt.date_key GROUP BY dt.year, ((dt.month-1)/3)+1",
        "tables": ["fact_adverse_events", "dim_date"],
    },
    {
        "q": "Unique drugs reported?",
        "semantic": "[Unique Drugs]",
        "sql": "SELECT COUNT(DISTINCT f.primary_drug) FROM fact_adverse_events f",
        "tables": ["fact_adverse_events"],
    },
    {
        "q": "Reporting countries for a drug?",
        "semantic": "[Reporting Countries] WHERE Drug = @drug",
        "sql": "SELECT COUNT(DISTINCT f.occurcountry) FROM fact_adverse_events f JOIN dim_drug d ON f.primary_drug = d.drug_name WHERE d.drug_name = @drug",
        "tables": ["fact_adverse_events", "dim_drug"],
    },
    {
        "q": "Serious rate by country for a drug?",
        "semantic": "[Serious Rate (event-weighted)] BY Country WHERE Drug = @drug",
        "sql": "SELECT c.country, SUM(CASE WHEN f.is_serious THEN 1 ELSE 0 END)*1.0/COUNT(*) FROM fact_adverse_events f JOIN dim_drug d ON f.primary_drug = d.drug_name JOIN dim_country c ON f.occurcountry = c.country_key WHERE d.drug_name = @drug GROUP BY c.country",
        "tables": ["fact_adverse_events", "dim_drug", "dim_country"],
    },
    {
        "q": "Monthly report trend?",
        "semantic": "[Reports] BY Date[year], Date[month]",
        "sql": "SELECT dt.year, dt.month, COUNT(*) FROM fact_adverse_events f JOIN dim_date dt ON f.received_date = dt.date_key GROUP BY dt.year, dt.month ORDER BY dt.year, dt.month",
        "tables": ["fact_adverse_events", "dim_date"],
    },
    {
        "q": "Total reports overall?",
        "semantic": "[Total Reports]",
        "sql": "SELECT SUM(total_reports) FROM mart_drug_safety_kpis",
        "tables": ["mart_drug_safety_kpis"],
    },
    {
        "q": "Average serious rate across drugs?",
        "semantic": "[Avg Serious Rate]",
        "sql": "SELECT AVG(serious_rate) FROM mart_drug_safety_kpis",
        "tables": ["mart_drug_safety_kpis"],
    },
]


def tokens(s):
    return len(s.replace("(", " ( ").replace(")", " ) ").split())


def main():
    rows, tok_ratios, surf_ratios = [], [], []
    for item in QUESTIONS:
        st, qt = tokens(item["semantic"]), tokens(item["sql"])
        # semantic surfaces = 1 (a named measure hides the joins); raw = # tables the author joins
        ss, qs = 1, len(item["tables"])
        tok_ratios.append(qt / st)
        surf_ratios.append(qs / ss)
        rows.append({"q": item["q"], "semantic_tokens": st, "sql_tokens": qt,
                     "token_reduction_x": round(qt / st, 2),
                     "surfaces_semantic": ss, "surfaces_raw": qs})

    result = {
        "n_questions": len(QUESTIONS),
        "metric": "complexity a user/LLM must emit per question: semantic named-measure vs raw SQL over the star schema",
        "median_token_reduction_x": round(statistics.median(tok_ratios), 2),
        "mean_token_reduction_x": round(statistics.mean(tok_ratios), 2),
        "median_surface_reduction_x": round(statistics.median(surf_ratios), 2),
        "per_question": rows,
        "claimable_range_x": f"{round(min(tok_ratios),1)}-{round(max(tok_ratios),1)}x token reduction; "
                             f"median {round(statistics.median(tok_ratios),1)}x, and the LLM reasons over 1 named "
                             f"measure instead of up to {max(len(i['tables']) for i in QUESTIONS)} joined tables",
        "honesty_note": "Measures prompt/query complexity (tokens + join surfaces), not wall-clock time. "
                        "Runtime speed is separately proven in proof/dax_latency.json (p50 ~0.5s).",
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print(f"semantic complexity: median {result['median_token_reduction_x']}x fewer tokens, "
          f"median {result['median_surface_reduction_x']}x fewer table-surfaces "
          f"(across {result['n_questions']} typical safety questions)")
    print(f"claimable: {result['claimable_range_x']}")


if __name__ == "__main__":
    main()
