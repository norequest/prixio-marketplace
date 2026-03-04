#!/usr/bin/env python3
"""Georgian dividend tax calculator for Prixio LLC (Estonian model)."""
import argparse

def calculate_dividend(amount: float) -> dict:
    corp_profit_tax   = round(amount * 0.15, 2)
    div_withholding   = round(amount * 0.05, 2)
    net_to_founder    = round(amount - div_withholding, 2)
    total_tax         = round(corp_profit_tax + div_withholding, 2)
    effective_rate    = round((total_tax / amount) * 100, 1)
    rs_ge_payment     = round(corp_profit_tax + div_withholding, 2)

    return {
        "gross_dividend": amount,
        "corporate_profit_tax_15pct": corp_profit_tax,
        "dividend_withholding_5pct": div_withholding,
        "net_to_founder": net_to_founder,
        "total_tax_burden": total_tax,
        "effective_tax_rate_pct": effective_rate,
        "payment_to_rs_ge_by_15th": rs_ge_payment,
    }

def main():
    parser = argparse.ArgumentParser(description="Georgian dividend calculator")
    parser.add_argument("--amount", type=float, required=True, help="Dividend amount in GEL")
    args = parser.parse_args()

    r = calculate_dividend(args.amount)

    print(f"\n{'='*45}")
    print(f"  DIVIDEND CALCULATION — Prixio LLC")
    print(f"  (Estonian Profit Tax Model)")
    print(f"{'='*45}")
    print(f"  Dividend declared:        {r['gross_dividend']:>10.2f} ₾")
    print(f"  ─────────────────────────────────────────")
    print(f"  Corp. profit tax (15%):  -{r['corporate_profit_tax_15pct']:>10.2f} ₾  (company pays)")
    print(f"  Dividend withholding(5%):-{r['dividend_withholding_5pct']:>10.2f} ₾  (from founder)")
    print(f"  ─────────────────────────────────────────")
    print(f"  Net to founder:           {r['net_to_founder']:>10.2f} ₾")
    print(f"  Total tax burden:         {r['total_tax_burden']:>10.2f} ₾")
    print(f"  Effective rate:           {r['effective_tax_rate_pct']:>9.1f}%")
    print(f"\n  ── Pay to rs.ge by 15th ──────────────────")
    print(f"  Corp tax + withholding:   {r['payment_to_rs_ge_by_15th']:>10.2f} ₾")
    print(f"  File: Form III-04")
    print(f"{'='*45}\n")

if __name__ == "__main__":
    main()
