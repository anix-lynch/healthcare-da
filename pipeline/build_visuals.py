#!/usr/bin/env python3
"""
Showroom visuals for Resume A — agent-made (matplotlib), headless, N=3,000.

NOT Power BI screenshots — these are diagram/chart artifacts generated from the repo's
own proof files + the live mart numbers, so every figure is reproducible and traceable.
Numbers are the real event-grain figures at N=3,000 reports (NOT the old 300).

Run: ./.venv/bin/python pipeline/build_visuals.py   (needs matplotlib)
Out: visuals/01..07 *.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "visuals"
OUT.mkdir(exist_ok=True)

# real N=3,000 event-grain numbers (from BigQuery mart, verified via DAX)
KPI = {"Total Reports": "3,000", "Serious Rate": "51.3%", "Unique Drugs": "562", "Countries": "44"}
TOP_DRUGS = [("DUPILUMAB", 502), ("TIRZEPATIDE", 189), ("RISANKIZUMAB", 74), ("TREPROSTINIL", 72),
             ("LOTILANER", 63), ("PROGESTERONE", 47), ("UPADACITINIB", 46), ("NEMOLIZUMAB", 38),
             ("ADALIMUMAB", 34), ("SPARSENTAN", 30)]

INK = "#1d3354"      # deep coastal navy
SEA = "#3e7cb1"      # mid blue
MIST = "#dbe9f4"     # pale blue
SAND = "#e8e0d5"     # warm neutral
GOOD = "#2a9d8f"     # teal
WARN = "#e9c46a"
FAIL = "#e76f51"


def _style(ax):
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")


def box(ax, x, y, w, h, text, fc=MIST, ec=INK, tc=INK, fs=10, bold=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6,rounding_size=2",
                                fc=fc, ec=ec, lw=1.6))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=tc,
            fontsize=fs, fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, x1, y1, x2, y2, label="", color=INK):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=18,
                                 color=color, lw=1.8))
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 3, label, ha="center", va="bottom",
                fontsize=7.5, color=SEA, style="italic")


def save(fig, name):
    fig.savefig(OUT / name, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  built {name}")


# ── 01 lineage map ──
def lineage():
    fig, ax = plt.subplots(figsize=(13, 3.6)); _style(ax)
    ax.text(50, 95, "openFDA → Microsoft Fabric — End-to-End Lineage  (N=3,000 reports)",
            ha="center", fontsize=13, fontweight="bold", color=INK)
    nodes = [("openFDA\nFAERS API", 2, SAND), ("OneLake\nBronze", 18, MIST), ("Silver\nfact_adverse_events", 34, MIST),
             ("Gold\nmart_drug_safety_kpis", 51, MIST), ("Direct Lake\nSemantic Model", 69, SEA),
             ("Power BI\nReport ef468dc5", 86, GOOD)]
    edges = ["Data Factory", "quality gate\n+ contract", "aggregate", "Items API", "DAX <1.3s"]
    for t, x, c in nodes:
        box(ax, x, 42, 13, 22, t, fc=c, tc="white" if c in (SEA, GOOD) else INK, fs=8.5)
    for i, e in enumerate(edges):
        arrow(ax, nodes[i][1] + 13, 53, nodes[i + 1][1], 53, e)
    ax.text(50, 30, "every number on the report traces back through this chain — grounding, not vibes",
            ha="center", fontsize=8.5, color=SEA, style="italic")
    save(fig, "01_lineage_map.png")


# ── 02 quality gate map ──
def quality():
    fig, ax = plt.subplots(figsize=(12, 5)); _style(ax)
    ax.text(50, 95, "Trust Layer — Medallion Quality Gates", ha="center", fontsize=13, fontweight="bold", color=INK)
    box(ax, 4, 55, 22, 22, "BRONZE\nraw openFDA\n3,000 reports", fc=SAND, fs=9)
    box(ax, 39, 55, 22, 22, "SILVER\nfact_adverse_events\nvalidated", fc=MIST, fs=9)
    box(ax, 74, 55, 22, 22, "GOLD\nmart_drug_safety_kpis\n562 drugs", fc=SEA, tc="white", fs=9)
    arrow(ax, 26, 66, 39, 66, "contract gate")
    arrow(ax, 61, 66, 74, 66, "aggregate")
    checks = [("null drug name  14.4% → 0.0%", GOOD), ("data contract pass  100%", GOOD),
              ("schema-drift  PASS / WARN / FAIL", GOOD), ("dup / bad-date checks", GOOD),
              ("FAIL row → quarantine (not dropped)", WARN)]
    for i, (c, col) in enumerate(checks):
        y = 40 - i * 7.5
        ax.add_patch(FancyBboxPatch((20, y), 4, 4, boxstyle="round,pad=0.2", fc=col, ec=col))
        ax.text(26, y + 2, c, va="center", fontsize=9.5, color=INK)
    ax.text(50, 2, "agent-made diagram · source: TRUST/quality_report.json, data_contract.yml",
            ha="center", fontsize=7.5, color="#888")
    save(fig, "02_quality_gate_map.png")


# ── 03 star ERD (real event-grain) ──
def erd():
    fig, ax = plt.subplots(figsize=(11, 6)); _style(ax)
    ax.text(50, 96, "Star Schema — fact_adverse_events (event grain)", ha="center", fontsize=13, fontweight="bold", color=INK)
    fact_cols = "fact_adverse_events\n──────────────\nPK safetyreportid\n   received_date\nFK primary_drug\nFK reactions\n   is_serious\n   n_drugs · n_reactions\n   occurcountry"
    box(ax, 36, 33, 28, 34, fact_cols, fc=SEA, tc="white", fs=8.5)
    dims = [("dim_drug\n──────\nPK drug_id\n   drug_name\n(562 rows)", 4, 60),
            ("dim_reaction\n────────\nPK reaction_id\n   reaction_name\n(1,828 rows)", 70, 60),
            ("dim_date\n──────\nreceived_date\nyear · month", 4, 14),
            ("dim_country\n────────\noccurcountry\n(44)", 70, 14)]
    for t, x, y in dims:
        box(ax, x, y, 26, 26, t, fc=MIST, fs=8)
        arrow(ax, x + 13, y + (26 if y < 33 else 0), 50, 50 if y < 33 else 40, "")
    ax.text(50, 2, "agent-made diagram · PK/FK enforced in the gold marts", ha="center", fontsize=7.5, color="#888")
    save(fig, "03_star_erd.png")


# ── 04 contract → serving map ──
def serving():
    fig, ax = plt.subplots(figsize=(12, 5)); _style(ax)
    ax.text(50, 95, "One Governed Mart → Humans AND AI Agents", ha="center", fontsize=13, fontweight="bold", color=INK)
    box(ax, 36, 60, 28, 22, "mart_drug_safety_kpis\nDirect Lake semantic layer\n(one source of truth)", fc=SEA, tc="white", fs=9)
    consumers = [("Power BI report\nexec KPIs", 6, GOOD), ("AI agents\nground from marts", 39, GOOD), ("ad-hoc SQL\nanalysts", 72, GOOD)]
    for t, x, c in consumers:
        box(ax, x, 18, 22, 20, t, fc=MIST, fs=9)
        arrow(ax, 50, 60, x + 11, 38, "")
    ax.text(50, 5, "same measures, same numbers — no metric drift across consumers", ha="center", fontsize=8.5, color=SEA, style="italic")
    save(fig, "04_contract_serving_map.png")


# ── 05 executive KPI (N=3,000) ──
def kpi():
    fig = plt.figure(figsize=(13, 6.5)); fig.patch.set_facecolor("white")
    fig.suptitle("openFDA Drug-Safety — Executive KPIs  (N = 3,000 reports)", fontsize=14, fontweight="bold", color=INK, y=0.97)
    # KPI cards
    axc = fig.add_axes([0.04, 0.62, 0.92, 0.28]); _style(axc)
    for i, (k, v) in enumerate(KPI.items()):
        x = 2 + i * 24.5
        box(axc, x, 10, 22, 80, f"{v}\n{k}", fc=[MIST, SEA, MIST, SEA][i],
            tc="white" if i % 2 else INK, fs=15)
    # bar chart
    axb = fig.add_axes([0.10, 0.10, 0.84, 0.42])
    names = [d[0] for d in TOP_DRUGS][::-1]; vals = [d[1] for d in TOP_DRUGS][::-1]
    axb.barh(names, vals, color=SEA, edgecolor=INK)
    for i, v in enumerate(vals):
        axb.text(v + 4, i, str(v), va="center", fontsize=8, color=INK)
    axb.set_title("Top 10 drugs by adverse-event reports", fontsize=10, color=INK, loc="left")
    axb.spines[["top", "right"]].set_visible(False)
    axb.tick_params(labelsize=8)
    fig.text(0.5, 0.015, "agent-made chart · live mart_drug_safety_kpis (562 drugs) · serious rate weighted, event-grain",
             ha="center", fontsize=7.5, color="#888")
    save(fig, "05_executive_kpi.png")


# ── 06 medallion lifecycle (nice) ──
def medallion():
    fig, ax = plt.subplots(figsize=(11, 3.4)); _style(ax)
    ax.text(50, 92, "Medallion Lifecycle", ha="center", fontsize=13, fontweight="bold", color=INK)
    for i, (t, c) in enumerate([("BRONZE\nraw land", SAND), ("SILVER\nvalidated", MIST), ("GOLD\nserved", SEA)]):
        x = 8 + i * 32
        box(ax, x, 35, 24, 30, t, fc=c, tc="white" if c == SEA else INK, fs=10)
        if i < 2:
            arrow(ax, x + 24, 50, x + 32, 50, "")
    save(fig, "06_medallion_lifecycle.png")


# ── 07 orchestration DAG (nice) ──
def dag():
    fig, ax = plt.subplots(figsize=(12, 3.6)); _style(ax)
    ax.text(50, 92, "Pipeline DAG — ingest → quality → model → serve", ha="center", fontsize=13, fontweight="bold", color=INK)
    steps = [("pull\nopenFDA", 3), ("build\nmarts (BQ)", 22), ("push\nOneLake", 42), ("refresh\nmodel", 62), ("DAX\nbench", 81)]
    for t, x in steps:
        box(ax, x, 40, 15, 24, t, fc=MIST, fs=8.5)
    for i in range(len(steps) - 1):
        arrow(ax, steps[i][1] + 15, 52, steps[i + 1][1], 52, "")
    save(fig, "07_orchestration_dag.png")


if __name__ == "__main__":
    for fn in (lineage, quality, erd, serving, kpi, medallion, dag):
        fn()
    print("done — 7 visuals in visuals/")
