#!/usr/bin/env python3
"""Burn rate and runway analyzer for Prixio LLC.

Master cost aggregator combining all expense categories with runway projections.
Sources: platform-accounting.md, Georgian startup benchmarks
Updated: March 2026
"""
import argparse
import json
import math

BUFFER_RATE = 0.10  # 10% contingency buffer

PRESETS = {
    "pre_launch": {
        "infrastructure": 300,
        "team": 500,
        "marketing": 400,
        "office": 0,
        "legal": 500,
        "financial": 50,
    },
    "early_stage": {
        "infrastructure": 900,
        "team": 7500,
        "marketing": 2500,
        "office": 400,
        "legal": 700,
        "financial": 120,
    },
    "growth_stage": {
        "infrastructure": 3500,
        "team": 25000,
        "marketing": 10000,
        "office": 1200,
        "legal": 1000,
        "financial": 350,
    },
}

CATEGORY_LABELS = {
    "infrastructure": "Infrastructure (cloud, APIs, DevOps)",
    "team": "Team (salaries + contractors)",
    "marketing": "Marketing & Sales",
    "office": "Office & Admin",
    "legal": "Legal & Compliance",
    "financial": "Financial (bank fees, FX)",
}


def calculate_burn_rate(costs: dict, revenue: float = 0,
                        cash_on_hand: float = 0) -> dict:
    subtotal = round(sum(costs.values()), 2)
    buffer = round(subtotal * BUFFER_RATE, 2)
    gross_burn = round(subtotal + buffer, 2)
    net_burn = round(gross_burn - revenue, 2)

    if net_burn > 0 and cash_on_hand > 0:
        runway_months = round(cash_on_hand / net_burn, 1)
    elif net_burn <= 0:
        runway_months = float("inf")
    else:
        runway_months = 0.0

    breakeven_revenue = gross_burn

    category_pcts = {}
    for cat, amount in costs.items():
        pct = round(amount / subtotal * 100, 1) if subtotal > 0 else 0
        category_pcts[cat] = pct

    warnings = []
    if runway_months != float("inf") and runway_months < 6:
        warnings.append(f"LOW RUNWAY: Only {runway_months:.1f} months of cash remaining")
    if runway_months != float("inf") and runway_months < 3:
        warnings.append("CRITICAL: Less than 3 months runway -- immediate action needed")
    for cat, pct in category_pcts.items():
        if pct > 60:
            label = CATEGORY_LABELS.get(cat, cat)
            warnings.append(f"CONCENTRATION: {label} is {pct}% of spend")
    if revenue > 0 and revenue < gross_burn * 0.1:
        warnings.append("Revenue covers less than 10% of costs")

    return {
        "costs": costs,
        "category_pcts": category_pcts,
        "subtotal": subtotal,
        "buffer": buffer,
        "buffer_rate_pct": BUFFER_RATE * 100,
        "gross_burn": gross_burn,
        "revenue": revenue,
        "net_burn": net_burn,
        "cash_on_hand": cash_on_hand,
        "runway_months": runway_months,
        "breakeven_revenue": breakeven_revenue,
        "annual_projection": round(gross_burn * 12, 2),
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="Prixio burn rate analyzer")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preset", choices=["pre_launch", "early_stage", "growth_stage"],
                       help="Use preset cost profile")
    group.add_argument("--costs-json", type=str,
                       help="JSON object with cost categories")
    parser.add_argument("--revenue", type=float, default=0,
                        help="Current monthly revenue in GEL")
    parser.add_argument("--cash-on-hand", type=float, default=0,
                        help="Current bank balance in GEL")
    args = parser.parse_args()

    if args.preset:
        costs = PRESETS[args.preset]
        preset_name = args.preset.upper().replace("_", " ")
    else:
        costs = json.loads(args.costs_json)
        preset_name = "CUSTOM"

    r = calculate_burn_rate(costs, args.revenue, args.cash_on_hand)

    print(f"\n{'='*65}")
    print(f"  BURN RATE ANALYSIS -- Prixio LLC ({preset_name})")
    print(f"{'='*65}")

    print(f"\n  MONTHLY COST BREAKDOWN:")
    print(f"  {'Category':<40} {'Amount':>10} {'Share':>7}")
    print(f"  {'─'*59}")
    for cat, amount in r["costs"].items():
        label = CATEGORY_LABELS.get(cat, cat)
        pct = r["category_pcts"].get(cat, 0)
        print(f"  {label:<40} {amount:>10.0f} GEL {pct:>5.1f}%")

    print(f"  {'─'*59}")
    print(f"  {'Subtotal':<40} {r['subtotal']:>10.0f} GEL")
    print(f"  {'Contingency buffer (' + str(int(r['buffer_rate_pct'])) + '%)':<40}"
          f" {r['buffer']:>10.0f} GEL")
    print(f"  {'─'*59}")
    print(f"  {'GROSS MONTHLY BURN':<40} {r['gross_burn']:>10.0f} GEL")

    if r["revenue"] > 0:
        print(f"\n  REVENUE vs COSTS:")
        print(f"    Monthly revenue:                    {r['revenue']:>10.0f} GEL")
        print(f"    Monthly costs:                     -{r['gross_burn']:>10.0f} GEL")
        print(f"    {'─'*49}")
        if r["net_burn"] > 0:
            print(f"    NET MONTHLY BURN:                  -{r['net_burn']:>10.0f} GEL")
        else:
            print(f"    NET MONTHLY SURPLUS:                {abs(r['net_burn']):>10.0f} GEL")

    if r["cash_on_hand"] > 0:
        print(f"\n  RUNWAY ANALYSIS:")
        print(f"    Cash on hand:                       {r['cash_on_hand']:>10.0f} GEL")
        if r["runway_months"] == float("inf"):
            print(f"    Runway:                           INFINITE (profitable)")
        else:
            print(f"    Runway:                             {r['runway_months']:>10.1f} months")
            if r["runway_months"] >= 1:
                depletion_note = f"~{math.ceil(r['runway_months'])} months from now"
            else:
                depletion_note = "IMMINENT"
            print(f"    Cash depletion:                     {depletion_note}")

    print(f"\n  BREAK-EVEN:")
    print(f"    Revenue needed to cover costs:       {r['breakeven_revenue']:>10.0f} GEL/month")
    if r["revenue"] > 0:
        gap = r["breakeven_revenue"] - r["revenue"]
        if gap > 0:
            print(f"    Revenue gap:                        {gap:>10.0f} GEL/month")
        else:
            print(f"    Surplus above break-even:            {abs(gap):>10.0f} GEL/month")

    print(f"\n  12-MONTH PROJECTION:")
    print(f"    Annual costs:                       {r['annual_projection']:>10.0f} GEL")
    if r["revenue"] > 0:
        annual_revenue = r["revenue"] * 12
        annual_net = annual_revenue - r["annual_projection"]
        print(f"    Annual revenue (flat):              {annual_revenue:>10.0f} GEL")
        if annual_net >= 0:
            print(f"    Annual net:                         {annual_net:>10.0f} GEL")
        else:
            print(f"    Annual net:                        -{abs(annual_net):>10.0f} GEL")

    if r["warnings"]:
        print(f"\n  WARNINGS:")
        for w in r["warnings"]:
            print(f"    >> {w}")

    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
