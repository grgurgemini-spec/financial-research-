#!/usr/bin/env python3
"""Monte Carlo simulation of the path to financial freedom.

Simulates monthly net income (four streams), expenses and an ETF portfolio
over 25 years for 10,000 paths, across career phases anchored to the user's
actual situation (geodesy Master's student in Croatia, graduating ~2027-07).

Income-stream distributions are anchored on the researched ranges in
data/opportunities.json and REPORT.md; every tunable number lives in
ASSUMPTIONS below. Run:  python3 lifeplan/model.py
Outputs: data/lifeplan/results.json  (+ prints headline numbers)

This is a model, not a prophecy: it quantifies the *consequences* of the
assumptions, which are themselves uncertain.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "lifeplan"

SEED = 42
N_PATHS = 10_000
MONTHS = 300                    # 25 years
START = (2026, 8)               # first simulated month: Aug 2026
GRAD_MONTH = 11                 # 2027-07: graduation -> salary starts
PRODUCT_START = 29              # 2029-01: EO SaaS revenue ramp begins

ASSUMPTIONS = {
    "expenses": {
        "student_eur_mo": 700,          # user: EUR 500-900 band
        "independent_eur_mo": 1100,     # after graduation
        "step_2032_eur_mo": 200,        # lifestyle/family step at 2032
        "real_growth_yr": 0.015,
    },
    "platforms": {                       # AI-training platforms (P1 only)
        "rate_eur_hr": (8, 20),          # region-tiered, uniform per path
        "hours_wk": 10,
        "noise_sigma": 0.30,
    },
    "freelance": {                       # automation + GIS freelancing mix
        "base_full_eur_mo": 1300,        # median at ~25 h/wk after ramp
        "ramp_months": 6,
        "skill_sigma": 0.50,             # per-path lognormal dispersion
        "noise_sigma": 0.40,
        "p2_hours_scale": 0.45,          # ~10 h/wk once employed
        "real_growth_yr": 0.05,          # reputation/rate growth
    },
    "salary_net_eur_mo": {               # remote geospatial track (net)
        "baseline":  {"start": (2300, 300, 1800, 2800), "growth": (0.06, 0.03), "cap": 7000},
        "aggressive": {"start": (2800, 300, 2300, 3400), "growth": (0.08, 0.03), "cap": 9000},
        "croatia-local": {"start": (1500, 200, 1200, 1900), "growth": (0.04, 0.02), "cap": 3500},
        "job_loss_hazard_mo": 0.004,     # ~5%/yr
        "gap_months": (2, 5),
    },
    "product": {                          # EO micro-SaaS + automated streams
        "p_success": {"baseline": 0.55, "aggressive": 0.85, "croatia-local": 0.55},
        "plateau_median_eur_mo": 800,     # lognormal median if successful
        "plateau_sigma": 0.80,            # fat tail (micro-SaaS reality)
        "plateau_cap": 6000,
        "ramp_months": 36,
        "fail_residual_median": 100,      # Etsy/Apify trickle if SaaS fails
        "fail_residual_sigma": 0.60,
        "noise_sigma": 0.20,
    },
    "side_income_net_factor": 0.87,       # pausalni obrt tax + annual PO-SD
                                          # contributions + misc fees
    "etf": {"real_return_yr": 0.05, "vol_yr": 0.15},
    "fi_tiers_eur": {"lean (1.5k/mo)": 450_000,
                     "comfortable (2.5k/mo)": 750_000,
                     "fat (4k/mo)": 1_200_000},
}


def month_year(m: int) -> float:
    return START[0] + (START[1] - 1 + m) / 12.0


def lognormal_mult(rng, sigma, size):
    """Mean-1 lognormal multiplier."""
    return rng.lognormal(-sigma ** 2 / 2, sigma, size)


def simulate(scenario: str, rng: np.random.Generator,
             overrides: dict | None = None) -> dict:
    A = json.loads(json.dumps(ASSUMPTIONS))     # deep copy
    for path, value in (overrides or {}).items():
        node = A
        *keys, last = path.split(".")
        for k in keys:
            node = node[k]
        node[last] = value

    n, T = N_PATHS, MONTHS
    months = np.arange(T)
    years_since = months / 12.0

    # --- Stream 1: AI-training platforms (student year only, taper 3 mo) ---
    rate = rng.uniform(*A["platforms"]["rate_eur_hr"], n)[:, None]
    base_pl = rate * A["platforms"]["hours_wk"] * 4.33
    taper = np.clip((GRAD_MONTH + 3 - months) / 3.0, 0, 1)[None, :]
    platforms = base_pl * taper * lognormal_mult(rng, A["platforms"]["noise_sigma"], (n, T))

    # --- Stream 2: freelancing (ramp in P1, reduced hours after job starts) ---
    F = A["freelance"]
    skill = rng.lognormal(-F["skill_sigma"] ** 2 / 2, F["skill_sigma"], n)[:, None]
    ramp = np.clip((months + 1) / F["ramp_months"], 0, 1)[None, :]
    hours_scale = np.where(months < GRAD_MONTH, 1.0, F["p2_hours_scale"])[None, :]
    growth = (1 + F["real_growth_yr"]) ** years_since[None, :]
    freelance = (F["base_full_eur_mo"] * skill * ramp * hours_scale * growth
                 * lognormal_mult(rng, F["noise_sigma"], (n, T)))

    # --- Stream 3: salary (starts at graduation, growth, job-loss gaps) ---
    S = A["salary_net_eur_mo"][scenario]
    mu, sd, lo, hi = S["start"]
    start_salary = np.clip(rng.normal(mu, sd, n), lo, hi)[:, None]
    g = rng.normal(S["growth"][0], S["growth"][1], n)[:, None]
    yrs_working = np.clip((months - GRAD_MONTH) / 12.0, 0, None)[None, :]
    salary = np.where(months[None, :] >= GRAD_MONTH,
                      np.minimum(start_salary * (1 + g) ** yrs_working, S["cap"]), 0.0)
    # job-loss gaps: each loss event zeroes salary for gap months
    H = A["salary_net_eur_mo"]
    losses = rng.random((n, T)) < H["job_loss_hazard_mo"]
    losses[:, :GRAD_MONTH] = False
    gap_len = rng.integers(H["gap_months"][0], H["gap_months"][1] + 1, (n, T))
    gap_mask = np.zeros((n, T), dtype=bool)
    li, lm = np.nonzero(losses)
    for i, m0 in zip(li, lm):                       # sparse loop (~ n*T*hazard)
        gap_mask[i, m0:m0 + gap_len[i, m0]] = True
    salary = np.where(gap_mask, 0.0, salary)

    # --- Stream 4: product (Bernoulli success x lognormal plateau, ramp) ---
    P = A["product"]
    if scenario == "no-product":
        product = np.zeros((n, T))
    else:
        p_s = A["product"]["p_success"].get(scenario, A["product"]["p_success"]["baseline"])
        success = rng.random(n) < p_s
        plateau_ok = np.minimum(
            rng.lognormal(np.log(P["plateau_median_eur_mo"]), P["plateau_sigma"], n),
            P["plateau_cap"])
        plateau_fail = np.minimum(
            rng.lognormal(np.log(P["fail_residual_median"]), P["fail_residual_sigma"], n),
            500)
        plateau = np.where(success, plateau_ok, plateau_fail)[:, None]
        prog = np.clip((months - PRODUCT_START) / P["ramp_months"], 0, 1)[None, :]
        ramp_p = np.where(months[None, :] >= PRODUCT_START, prog ** 1.5, 0.0)
        product = plateau * ramp_p * lognormal_mult(rng, P["noise_sigma"], (n, T))

    side_net = A["side_income_net_factor"]
    income_streams = {
        "platforms": platforms * side_net,
        "freelance": freelance * side_net,
        "salary": salary,
        "product": product * side_net,
    }
    income = sum(income_streams.values())

    # --- Expenses ---
    E = A["expenses"]
    exp = np.where(months < GRAD_MONTH, E["student_eur_mo"], E["independent_eur_mo"])
    exp = exp + np.where(month_year(0) + years_since >= 2032, E["step_2032_eur_mo"], 0)
    expenses = (exp * (1 + E["real_growth_yr"]) ** years_since)[None, :] * np.ones((n, 1))

    # --- Portfolio: monthly ETF returns on balance + net savings ---
    etf = A["etf"]
    mu_m = (1 + etf["real_return_yr"]) ** (1 / 12) - 1
    sd_m = etf["vol_yr"] / np.sqrt(12)
    returns = rng.normal(mu_m, sd_m, (n, T))
    net = income - expenses
    portfolio = np.zeros((n, T))
    bal = np.zeros(n)
    for t in range(T):
        bal = np.maximum(bal * (1 + returns[:, t]) + net[:, t], 0.0)
        portfolio[:, t] = bal

    return {"income_streams": income_streams, "income": income,
            "expenses": expenses, "portfolio": portfolio}


def yearly_idx():
    """Indices of each December (or last simulated month)."""
    idx = [m for m in range(MONTHS) if (START[1] - 1 + m) % 12 == 11]
    return np.array(idx)


def fi_stats(portfolio: np.ndarray, tier: float) -> dict:
    crossed = portfolio >= tier
    ever = crossed.any(axis=1)
    first = np.where(ever, crossed.argmax(axis=1), MONTHS + 120)
    first_year = np.floor(month_year(0) + first / 12.0)
    yrs = np.arange(2027, int(month_year(MONTHS - 1)) + 1)
    prob_by_year = {int(y): round(float((first_year <= y).mean()), 3) for y in yrs}
    q = lambda p: (int(np.percentile(first_year[ever], p)) if ever.mean() > p / 100 else None)
    return {
        "prob_ever": round(float(ever.mean()), 3),
        "median_year": int(np.median(first_year)) if ever.mean() > 0.5 else None,
        "p10_year": q(10), "p90_year": q(90),
        "prob_by_year": prob_by_year,
    }


def summarize(sim: dict) -> dict:
    yi = yearly_idx()
    years = [int(month_year(m)) for m in yi]
    pct = lambda a: {f"p{p}": np.round(np.percentile(a[:, yi], p, axis=0), 0).tolist()
                     for p in (10, 25, 50, 75, 90)}
    med_streams = {k: np.round(np.median(v[:, yi], axis=0), 0).tolist()
                   for k, v in sim["income_streams"].items()}
    sr = np.clip(1 - sim["expenses"] / np.maximum(sim["income"], 1), -1, 1)
    return {
        "years": years,
        "networth": pct(sim["portfolio"]),
        "income_total": pct(sim["income"]),
        "income_streams_median": med_streams,
        "savings_rate_median": np.round(np.median(sr[:, yi], axis=0), 3).tolist(),
        "fi": {name: fi_stats(sim["portfolio"], tier)
               for name, tier in ASSUMPTIONS["fi_tiers_eur"].items()},
    }


def median_fat_fi_year(sim: dict) -> float:
    tier = ASSUMPTIONS["fi_tiers_eur"]["fat (4k/mo)"]
    crossed = sim["portfolio"] >= tier
    ever = crossed.any(axis=1)
    first = np.where(ever, crossed.argmax(axis=1), MONTHS + 120)
    return float(np.median(month_year(0) + first / 12.0))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scenarios = {}
    sims = {}
    for name in ["baseline", "no-product", "aggressive", "croatia-local"]:
        rng = np.random.default_rng(SEED)       # same shocks across scenarios
        sc = "baseline" if name == "no-product" else name
        sim = simulate(sc, rng) if name != "no-product" else simulate("baseline", rng)
        if name == "no-product":
            # rebuild without product income, same draws for comparability
            rng = np.random.default_rng(SEED)
            sim = simulate_no_product(rng)
        sims[name] = sim
        scenarios[name] = summarize(sim)
        print(f"[{name}] fat-FI median year: {median_fat_fi_year(sim):.1f} | "
              f"lean prob ever: {scenarios[name]['fi']['lean (1.5k/mo)']['prob_ever']}")

    # --- Sensitivity: change one lever on baseline, record median fat-FI shift ---
    base_year = median_fat_fi_year(sims["baseline"])
    levers = {
        "Product succeeds for sure (p=1.0)": {"product.p_success.baseline": 1.0},
        "Product never works (p=0)": {"product.p_success.baseline": 1e-9},
        "Fewer side hours now (25→15 h/wk)": {"freelance.base_full_eur_mo": 780},
        "Expenses +€300/mo": {"expenses.independent_eur_mo": 1400},
        "Expenses −€200/mo": {"expenses.independent_eur_mo": 900},
        "ETF returns 3% real (not 5%)": {"etf.real_return_yr": 0.03},
        "Salary: stay on local Croatian track": None,   # use scenario result
        "Salary: aggressive remote track": None,
    }
    sensitivity = []
    for label, ov in levers.items():
        if label.startswith("Salary: stay"):
            y = median_fat_fi_year(sims["croatia-local"])
        elif label.startswith("Salary: aggressive"):
            y = median_fat_fi_year(sims["aggressive"])
        else:
            rng = np.random.default_rng(SEED)
            y = median_fat_fi_year(simulate("baseline", rng, overrides=ov))
        sensitivity.append({"lever": label, "median_year": round(y, 1),
                            "delta_years": round(y - base_year, 1)})
        print(f"  sensitivity: {label}: {y:.1f} ({y - base_year:+.1f} y)")
    sensitivity.sort(key=lambda s: s["delta_years"])

    results = {
        "meta": {"seed": SEED, "n_paths": N_PATHS, "months": MONTHS,
                 "start": f"{START[0]}-{START[1]:02d}",
                 "generated": "2026-07-19",
                 "fi_tiers_eur": ASSUMPTIONS["fi_tiers_eur"],
                 "baseline_fat_fi_median_year": round(base_year, 1),
                 "assumptions": ASSUMPTIONS},
        "scenarios": scenarios,
        "sensitivity": sensitivity,
    }
    (OUT_DIR / "results.json").write_text(json.dumps(results, indent=1) + "\n")
    print(f"wrote {OUT_DIR / 'results.json'}")


def simulate_no_product(rng: np.random.Generator) -> dict:
    sim = simulate("baseline", rng)
    # zero out product with identical draws elsewhere is not possible post-hoc
    # (portfolio compounding), so re-run the accumulation without it:
    income = sim["income"] - sim["income_streams"]["product"]
    sim["income_streams"] = dict(sim["income_streams"], product=np.zeros_like(income))
    net = income - sim["expenses"]
    rng2 = np.random.default_rng(SEED + 1)
    etf = ASSUMPTIONS["etf"]
    mu_m = (1 + etf["real_return_yr"]) ** (1 / 12) - 1
    sd_m = etf["vol_yr"] / np.sqrt(12)
    returns = rng2.normal(mu_m, sd_m, net.shape)
    portfolio = np.zeros_like(net)
    bal = np.zeros(net.shape[0])
    for t in range(net.shape[1]):
        bal = np.maximum(bal * (1 + returns[:, t]) + net[:, t], 0.0)
        portfolio[:, t] = bal
    return {"income_streams": sim["income_streams"], "income": income,
            "expenses": sim["expenses"], "portfolio": portfolio}


if __name__ == "__main__":
    main()
