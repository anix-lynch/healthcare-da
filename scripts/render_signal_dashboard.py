#!/usr/bin/env python3
"""
Render an exec-style signal dashboard from signals_by_patient.csv.
Power-BI-LOOK (matplotlib) — NOT Power BI itself. Labeled honestly.
Same data + same method as the Vertex/Python cross-ref: complex_high_utilizer = 535.
"""
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

CSV = sys.argv[1] if len(sys.argv) > 1 else "data/raw/signals_by_patient.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "screenshots/signal_dashboard.png"

df = pd.read_csv(CSV)

# --- metrics ---
total = len(df)
high = int((df["cohort"] == "complex_high_utilizer").sum())
avg_los = df["avg_los_days"].mean()
now_pct = (df["tier_bucket"] == "NOW").mean() * 100 if "tier_bucket" in df else 0
anomalies = int(df["anomaly_flag"].sum()) if "anomaly_flag" in df else 0

# Power BI / French-coastal-ish palette
BG = "#F4F6F8"; CARD = "#FFFFFF"; INK = "#1B2A3A"
ACCENT = "#2E6E8E"; HOT = "#D9534F"; MUTE = "#9AA7B2"
COHORT_C = {"complex_high_utilizer": HOT, "cohort_2": ACCENT,
            "cohort_1": "#5B9BB5", "cohort_0": "#A9C7D6"}
TIER_C = {"NOW": HOT, "SOON": "#E8A13A", "WAIT": "#7FB07F"}

plt.rcParams["font.family"] = "DejaVu Sans"
fig = plt.figure(figsize=(15, 8.6), dpi=130)
fig.patch.set_facecolor(BG)
gs = fig.add_gridspec(3, 4, height_ratios=[0.62, 1.05, 1.05],
                      hspace=0.42, wspace=0.30,
                      left=0.045, right=0.965, top=0.92, bottom=0.07)

# --- title bar ---
fig.text(0.045, 0.965, "Healthcare Signal Dashboard",
         fontsize=23, fontweight="bold", color=INK)
fig.text(0.045, 0.935,
         "Patient-level risk signals  ·  synthetic data  ·  cluster cross-ref: silhouette 0.41",
         fontsize=11, color=MUTE)
fig.text(0.965, 0.958, "L1.5 SIGNALS", fontsize=11, fontweight="bold",
         color="#FFFFFF", ha="right",
         bbox=dict(boxstyle="round,pad=0.45", fc=HOT, ec="none"))

# --- KPI cards ---
kpis = [("Total Patients", f"{total:,}", ACCENT),
        ("High Utilizers", f"{high:,}", HOT),
        ("Avg LOS (days)", f"{avg_los:.1f}", ACCENT),
        ("Flagged Anomalies", f"{anomalies:,}", "#E8A13A")]
for i, (label, val, c) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.02, 0.05), 0.96, 0.9,
                 boxstyle="round,pad=0.02,rounding_size=0.06",
                 fc=CARD, ec="#E3E8EC", lw=1.2, transform=ax.transAxes))
    ax.text(0.5, 0.30, label, fontsize=11.5, color=MUTE, ha="center", transform=ax.transAxes)
    ax.text(0.5, 0.62, val, fontsize=27, fontweight="bold", color=c, ha="center", transform=ax.transAxes)

def card(ax, title):
    ax.set_facecolor(CARD)
    for s in ax.spines.values(): s.set_color("#E3E8EC")
    ax.set_title(title, fontsize=12.5, fontweight="bold", color=INK, loc="left", pad=10)
    ax.tick_params(colors=MUTE, labelsize=9.5)

# --- cohort bar (535 highlighted) ---
ax1 = fig.add_subplot(gs[1, 0:2]); card(ax1, "Patients by cohort  (high-utilizer cluster isolated)")
cc = df["cohort"].value_counts()
order = ["cohort_2", "cohort_1", "cohort_0", "complex_high_utilizer"]
cc = cc.reindex([o for o in order if o in cc.index])
bars = ax1.barh([o.replace("_", " ") for o in cc.index], cc.values,
                color=[COHORT_C.get(o, ACCENT) for o in cc.index])
for b, v in zip(bars, cc.values):
    ax1.text(v + total*0.008, b.get_y()+b.get_height()/2, f"{v:,}",
             va="center", fontsize=10, color=INK, fontweight="bold")
ax1.set_xlim(0, cc.values.max()*1.18); ax1.invert_yaxis()
ax1.grid(axis="x", color="#EEF1F3"); ax1.set_axisbelow(True)

# --- tier donut ---
ax2 = fig.add_subplot(gs[1, 2]); card(ax2, "Triage tier")
if "tier_bucket" in df:
    tc = df["tier_bucket"].value_counts().reindex(["NOW", "SOON", "WAIT"]).dropna()
    ax2.pie(tc.values, labels=tc.index, autopct="%1.0f%%", startangle=90,
            colors=[TIER_C.get(t, MUTE) for t in tc.index],
            wedgeprops=dict(width=0.42, edgecolor="white"),
            textprops=dict(fontsize=10, color=INK))
ax2.axis("equal")

# --- severity / esi ---
ax3 = fig.add_subplot(gs[1, 3]); card(ax3, "ESI tier mix")
if "esi_tier" in df:
    ec = df["esi_tier"].value_counts().sort_index()
    ax3.bar(ec.index.astype(str), ec.values, color=ACCENT)
    ax3.grid(axis="y", color="#EEF1F3"); ax3.set_axisbelow(True)
    ax3.set_xlabel("ESI", fontsize=9, color=MUTE)

# --- billing by cohort (high-util cost flex) ---
ax4 = fig.add_subplot(gs[2, 0:2]); card(ax4, "Avg total billing by cohort  ($)")
bb = df.groupby("cohort")["total_billing"].mean().reindex([o for o in order if o in cc.index])
bars = ax4.bar([o.replace("_", " ") for o in bb.index], bb.values,
               color=[COHORT_C.get(o, ACCENT) for o in bb.index])
for b, v in zip(bars, bb.values):
    ax4.text(b.get_x()+b.get_width()/2, v, f"${v:,.0f}", ha="center", va="bottom",
             fontsize=9.5, color=INK, fontweight="bold")
ax4.grid(axis="y", color="#EEF1F3"); ax4.set_axisbelow(True)
ax4.set_ylim(0, bb.values.max()*1.15)

# --- anomaly score distribution ---
ax5 = fig.add_subplot(gs[2, 2:4]); card(ax5, "Anomaly score distribution")
if "anomaly_score" in df:
    ax5.hist(df["anomaly_score"], bins=40, color=ACCENT, alpha=0.85)
    thr = df["anomaly_score"].quantile(0.95)
    ax5.axvline(thr, color=HOT, ls="--", lw=1.5)
    ax5.text(thr, ax5.get_ylim()[1]*0.9, "  95th pct flag", color=HOT, fontsize=9.5)
    ax5.grid(axis="y", color="#EEF1F3"); ax5.set_axisbelow(True)

fig.text(0.045, 0.012,
         "Synthetic data · rendered from signals_by_patient.csv (Python/matplotlib) · "
         "cohort method identical to Vertex run → complex_high_utilizer = 535",
         fontsize=8.5, color=MUTE)

fig.savefig(OUT, facecolor=BG, bbox_inches="tight")
print(f"saved {OUT}  ({total:,} rows, high={high})")
