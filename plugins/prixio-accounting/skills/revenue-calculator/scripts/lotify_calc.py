#!/usr/bin/env python3
"""Lotify auction commission calculator for Prixio LLC.

Calculates revenue split, VAT, and payment processing fees for auction sales.
Sources: platform-accounting.md, infohub.rs.ge guide 11xx
Updated: March 2026
"""
import argparse

TBC_PAY_FEE_RATE = 0.015  # ~1.5% estimate
VAT_RATE = 0.18


def calculate_lotify(sale_amount: float, commission_rate: float,
                     vat_registered: bool = False) -> dict:
    commission = round(sale_amount * (commission_rate / 100), 2)
    seller_payout = round(sale_amount - commission, 2)
    tbc_fee = round(commission * TBC_PAY_FEE_RATE, 2)

    vat_on_commission = round(commission * VAT_RATE, 2) if vat_registered else 0.0
    net_commission = round(commission - vat_on_commission - tbc_fee, 2)

    return {
        "sale_amount": sale_amount,
        "commission_rate_pct": commission_rate,
        "commission_revenue": commission,
        "seller_payout": seller_payout,
        "tbc_pay_fee_estimate": tbc_fee,
        "vat_registered": vat_registered,
        "vat_on_commission": vat_on_commission,
        "net_commission_after_vat_fees": net_commission,
    }


def main():
    parser = argparse.ArgumentParser(description="Lotify commission calculator")
    parser.add_argument("--sale", type=float, required=True, help="Sale amount in GEL")
    parser.add_argument("--rate", type=float, required=True, help="Commission rate in percent")
    parser.add_argument("--vat", action="store_true", help="Include VAT (if VAT-registered)")
    args = parser.parse_args()

    r = calculate_lotify(args.sale, args.rate, args.vat)

    print(f"\n{'='*55}")
    print(f"  LOTIFY COMMISSION — Prixio LLC")
    print(f"  VAT-registered: {'Yes' if r['vat_registered'] else 'No'}")
    print(f"{'='*55}")
    print(f"  Sale amount:                {r['sale_amount']:>12.2f} GEL")
    print(f"  Commission rate:            {r['commission_rate_pct']:>11.1f}%")
    print(f"  ───────────────────────────────────────────────────")
    print(f"  Commission (Prixio revenue):{r['commission_revenue']:>12.2f} GEL")
    print(f"  Seller payout (liability):  {r['seller_payout']:>12.2f} GEL")
    print(f"  ───────────────────────────────────────────────────")
    print(f"  TBC Pay fee (~1.5%):       -{r['tbc_pay_fee_estimate']:>12.2f} GEL")
    if r['vat_registered']:
        print(f"  VAT on commission (18%):   -{r['vat_on_commission']:>12.2f} GEL")
    print(f"  ───────────────────────────────────────────────────")
    print(f"  Net commission:             {r['net_commission_after_vat_fees']:>12.2f} GEL")
    print(f"\n  NOTE: Escrow funds ({r['seller_payout']:.2f} GEL) are LIABILITY,")
    print(f"  not revenue. Only commission counts for VAT threshold.")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
