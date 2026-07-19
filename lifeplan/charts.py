#!/usr/bin/env python3
"""Render the life-plan charts from data/lifeplan/results.json.

Palette and chart chrome follow the repo's viz conventions (categorical:
blue/green/magenta/yellow; recessive grid; text in ink, not series colors).
Run after model.py:  python3 lifeplan/charts.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "lifeplan"
R = json.loads((OUT / "results.json").read_text())

SURFACE = "#fcfcfb"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, BASE = "#e1e0d9", "#c3c2b7"
BLUE, GREEN, MAGENTA, YELLOW = "#2a78d6", "#008300", "#e87ba4", "#eda100"
RED = "#e34948"

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 11,
    "text.color": INK, "axes.edgecolor": BASE, "axes.labelcolor": INK2,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "savefig.dpi": 130,
    "savefig.bbox": "tight",
})

B = R["scenarios"]["baseline"]
YEARS = B["years"]
TIERS = R["meta"]["fi_tiers_eur"]
kfmt = mticker.FuncFormatter(lambda v, _: f"€{v/1e6:.1f}M" if v >= 1e6 else f"€{v/1e3:.0f}k")


def networth_fan():
    nw = B["networth"]
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.fill_between(YEARS, nw["p10"], nw["p90"], color=BLUE, alpha=0.13, lw=0,
                    label="10th–90th percentile")
    ax.fill_between(YEARS, nw["p25"], nw["p75"], color=BLUE, alpha=0.22, lw=0,
                    label="25th–75th percentile")
    ax.plot(YEARS, nw["p50"], color=BLUE, lw=2, label="Median")
    for (name, tier), fi in zip(TIERS.items(), B["fi"].values()):
        ax.axhline(tier, color=BASE, lw=1, ls=(0, (4, 4)))
        note = f"  {name} — €{tier/1e3:.0f}k" + (f", median {fi['median_year']}" if fi["median_year"] else "")
        ax.annotate(note, (YEARS[0], tier), textcoords="offset points",
                    xytext=(2, 4), fontsize=9, color=INK2)
        if fi["median_year"]:
            ax.plot([fi["median_year"]], [tier], "o", ms=7, color=BLUE,
                    mec=SURFACE, mew=1.5)
    ax.set_ylim(0, max(nw["p90"]) * 1.04)
    ax.set_xlim(YEARS[0], YEARS[-1])
    ax.yaxis.set_major_formatter(kfmt)
    ax.set_title("Net worth projection — baseline scenario (10,000 simulated paths, real €)",
                 fontsize=12, color=INK, loc="left")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.97), fontsize=9)
    fig.savefig(OUT / "networth_fan.png")
    plt.close(fig)


def income_composition():
    streams = B["income_streams_median"]
    order = ["platforms", "freelance", "salary", "product"]
    labels = {"platforms": "AI-training platforms", "freelance": "Freelancing",
              "salary": "Remote salary", "product": "Products & automation"}
    colors = {"platforms": MAGENTA, "freelance": GREEN,
              "salary": BLUE, "product": YELLOW}
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.stackplot(YEARS, [streams[k] for k in order],
                 colors=[colors[k] for k in order],
                 labels=[labels[k] for k in order],
                 edgecolor=SURFACE, linewidth=1.2, alpha=0.92)
    ax.set_xlim(YEARS[0], YEARS[-1])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"€{v/1e3:.1f}k"))
    ax.set_title("Median monthly net income by stream — baseline scenario",
                 fontsize=12, color=INK, loc="left")
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    fig.savefig(OUT / "income_composition.png")
    plt.close(fig)


def fi_probability():
    fig, ax = plt.subplots(figsize=(9, 4.8))
    tier_colors = [BLUE, GREEN, MAGENTA]
    for (name, fi), c in zip(B["fi"].items(), tier_colors):
        yrs = sorted(int(y) for y in fi["prob_by_year"])
        probs = [fi["prob_by_year"][str(y)] * 100 for y in yrs]
        ax.plot(yrs, probs, color=c, lw=2)
        ax.annotate(name, (yrs[-1], probs[-1]), textcoords="offset points",
                    xytext=(-4, 6), ha="right", fontsize=9.5, fontweight="bold",
                    color=INK)
    ax.axhline(50, color=BASE, lw=1, ls=(0, (4, 4)))
    ax.annotate("coin-flip (50%)", (YEARS[0], 50), textcoords="offset points",
                xytext=(2, 4), fontsize=8.5, color=MUTED)
    ax.set_ylim(0, 104)
    ax.set_xlim(2027, YEARS[-1])
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.set_title("Probability of having reached each financial-freedom tier — baseline",
                 fontsize=12, color=INK, loc="left")
    fig.savefig(OUT / "fi_probability.png")
    plt.close(fig)


def sensitivity_tornado():
    rows = sorted(R["sensitivity"], key=lambda s: -abs(s["delta_years"]))
    labels = [r["lever"] for r in rows][::-1]
    deltas = [r["delta_years"] for r in rows][::-1]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    colors = [RED if d > 0 else BLUE for d in deltas]
    bars = ax.barh(labels, deltas, color=colors, height=0.55, alpha=0.9)
    for bar, d in zip(bars, deltas):
        ax.annotate(f"{d:+.1f} y", (d, bar.get_y() + bar.get_height() / 2),
                    textcoords="offset points",
                    xytext=(6 if d >= 0 else -6, 0),
                    ha="left" if d >= 0 else "right", va="center",
                    fontsize=9.5, color=INK)
    ax.axvline(0, color=BASE, lw=1)
    ax.set_xlim(min(deltas) - 3, max(deltas) + 3)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Shift of median fat-FI year vs. baseline (years) — blue = sooner, red = later")
    ax.set_title("What actually moves your financial-freedom date",
                 fontsize=12, color=INK, loc="left")
    fig.savefig(OUT / "sensitivity.png")
    plt.close(fig)


if __name__ == "__main__":
    networth_fan()
    income_composition()
    fi_probability()
    sensitivity_tornado()
    print("charts written to", OUT)
