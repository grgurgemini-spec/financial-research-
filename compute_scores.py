#!/usr/bin/env python3
"""Compute Best Option scores for data/opportunities.json (in place) and
print ranked markdown tables for REPORT.md.

Formula (documented in data meta + REPORT.md):
  income_score     = 10 * log10(income_mid) / log10(20000), capped to [0, 10]
  skill_component  = (5 - skill) / 4 * 10
  speed_component  = 10 - days_to_first_eur / 90 * 10, capped to [0, 10]
  cost_component   = 10 - upfront_cost_eur / 500 * 10, capped to [0, 10]
  ease_score       = mean(skill, speed, cost components)
  automation_score = automation_pct / 10
  lowrisk_score    = (5 - risk) / 4 * 10
  total = 0.40*income + 0.30*ease + 0.15*automation + 0.15*lowrisk
"""
import json
import math
from pathlib import Path

DATA = Path(__file__).parent / "data" / "opportunities.json"


def clamp(x, lo=0.0, hi=10.0):
    return max(lo, min(hi, x))


def score(o):
    income = clamp(10 * math.log10(max(o["income_mid"], 1)) / math.log10(20000))
    skill_c = (5 - o["skill"]) / 4 * 10
    speed_c = clamp(10 - o["time_to_first_eur_days"] / 90 * 10)
    cost_c = clamp(10 - o["upfront_cost_eur"] / 500 * 10)
    ease = (skill_c + speed_c + cost_c) / 3
    automation = o["automation_pct"] / 10
    lowrisk = (5 - o["risk"]) / 4 * 10
    total = 0.40 * income + 0.30 * ease + 0.15 * automation + 0.15 * lowrisk
    return {
        "income": round(income, 2),
        "ease": round(ease, 2),
        "automation": round(automation, 2),
        "lowrisk": round(lowrisk, 2),
        "total": round(total, 2),
    }


def table(rows, title):
    print(f"\n### {title}\n")
    print("| # | Opportunity | Category | Income €/mo (mid) | First € in | Skill | Automation | Risk | Score |")
    print("|---|---|---|---|---|---|---|---|---|")
    for i, o in enumerate(rows, 1):
        print(
            f"| {i} | {o['name']} | {o['category']} | "
            f"{o['income_low']}–{o['income_high']} ({o['income_mid']}) | "
            f"{o['time_to_first_eur_days']} d | {o['skill']}/5 | "
            f"{o['automation_pct']}% | {o['risk']}/5 | **{o['scores']['total']}** |"
        )


def main():
    data = json.loads(DATA.read_text())
    for o in data["opportunities"]:
        o["scores"] = score(o)
    ranked = sorted(data["opportunities"], key=lambda o: -o["scores"]["total"])
    data["opportunities"] = ranked
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    table(ranked, "Master ranking (best first)")
    table([o for o in ranked if o["automation_pct"] >= 80][:5], "Top fully-automated (≥80%)")
    table([o for o in ranked if o["category"] == "geospatial"][:5], "Top geospatial")


if __name__ == "__main__":
    main()
