#!/usr/bin/env python3
"""Georgian dividend tax calculator for Prixio LLC (Estonian model).

Supports standard LLC, International Company (IC), and Virtual Zone (VZP) regimes.
Sources: matsne.gov.ge Tax Code, infohub.rs.ge guide 26xx
Updated: March 2026
"""
import argparse

REGIMES = {
    "standard": {
        "cit_rate": 0.15,
        "wht_rate": 0.05,
        "label": "Standard LLC (15% CIT + 5% WHT)",
    },
    "ic_resident": {
        "cit_rate": 0.05,
        "wht_rate": 0.05,
        "label": "International Company — resident founder (5% CIT + 5% WHT)",
    },
    "ic_nonresident": {
        "cit_rate": 0.05,
        "wht_rate": 0.00,
        "label": "International Company — non-resident founder (5% CIT + 0% WHT)",
    },
    "vzp_export": {
        "cit_rate": 0.00,
        "wht_rate": 0.05,
        "label": "Virtual Zone — export income (0% CIT + 5% WHT)",
    },
    "bank_2023": {
        "cit_rate": 0.20,
        "wht_rate": 0.00,
        "label": "Bank/microfinance dividend (20% CIT, 0% WHT on 2023+ profits)",
    },
}


def calculate_dividend(amount: float, regime: str = "standard") -> dict:
    cfg = REGIMES[regime]
    cit_rate = cfg["cit_rate"]
    wht_rate = cfg["wht_rate"]

    corp_profit_tax = round(amount * cit_rate, 2)
    div_withholding = round(amount * wht_rate, 2)
    net_to_founder = round(amount - div_withholding, 2)
    total_tax = round(corp_profit_tax + div_withholding, 2)
    effective_rate = round((total_tax / amount) * 100, 1) if amount > 0 else 0.0
    rs_ge_payment = round(corp_profit_tax + div_withholding, 2)

    # Gross-up calculation (for tax return purposes)
    if cit_rate > 0:
        gross_up_base = round(amount / (1 - cit_rate), 2)
        gross_up_tax = round(gross_up_base * cit_rate, 2)
    else:
        gross_up_base = amount
        gross_up_tax = 0.0

    return {
        "gross_dividend": amount,
        "regime": cfg["label"],
        "cit_rate_pct": cit_rate * 100,
        "wht_rate_pct": wht_rate * 100,
        "corporate_profit_tax": corp_profit_tax,
        "dividend_withholding": div_withholding,
        "net_to_founder": net_to_founder,
        "total_tax_burden": total_tax,
        "effective_tax_rate_pct": effective_rate,
        "payment_to_rs_ge_by_15th": rs_ge_payment,
        "gross_up_base": gross_up_base,
        "gross_up_tax": gross_up_tax,
    }


def main():
    parser = argparse.ArgumentParser(description="Georgian dividend calculator")
    parser.add_argument("--amount", type=float, required=True, help="Dividend amount in GEL")
    parser.add_argument("--regime", choices=REGIMES.keys(), default="standard",
                        help="Tax regime (default: standard)")
    args = parser.parse_args()

    r = calculate_dividend(args.amount, args.regime)

    print(f"\n{'='*55}")
    print(f"  DIVIDEND CALCULATION — Prixio LLC")
    print(f"  Regime: {r['regime']}")
    print(f"  (Estonian Profit Tax Model)")
    print(f"{'='*55}")
    print(f"  Dividend declared:          {r['gross_dividend']:>12.2f} GEL")
    print(f"  ───────────────────────────────────────────────────")
    print(f"  Corp. profit tax ({r['cit_rate_pct']:.0f}%):   -{r['corporate_profit_tax']:>12.2f} GEL  (company pays)")
    print(f"  Dividend WHT ({r['wht_rate_pct']:.0f}%):       -{r['dividend_withholding']:>12.2f} GEL  (from founder)")
    print(f"  ───────────────────────────────────────────────────")
    print(f"  Net to founder:             {r['net_to_founder']:>12.2f} GEL")
    print(f"  Total tax burden:           {r['total_tax_burden']:>12.2f} GEL")
    print(f"  Effective rate:             {r['effective_tax_rate_pct']:>11.1f}%")
    print(f"\n  ── Gross-up (tax return) ──────────────────────────")
    print(f"  Gross-up base:              {r['gross_up_base']:>12.2f} GEL")
    print(f"  Gross-up CIT:               {r['gross_up_tax']:>12.2f} GEL")
    print(f"\n  ── Pay to rs.ge by 15th ──────────────────────────")
    print(f"  CIT + WHT:                  {r['payment_to_rs_ge_by_15th']:>12.2f} GEL")
    print(f"  File: Form III-04")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
