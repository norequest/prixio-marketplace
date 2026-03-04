#!/usr/bin/env python3
"""Courio delivery platform fee calculator for Prixio LLC.

Calculates revenue split, VAT, and courier payouts for deliveries.
Sources: platform-accounting.md, infohub.rs.ge guide 11xx
Updated: March 2026
"""
import argparse

PLATFORM_FEE_RATE = 0.15
MIN_DELIVERY_PRICE = 4.0
INSTANT_PAYOUT_FEE = 0.50
VAT_RATE = 0.18


def calculate_courio(delivery_price: float, vat_registered: bool = False,
                     instant_payout: bool = False) -> dict:
    if delivery_price < MIN_DELIVERY_PRICE:
        delivery_price = MIN_DELIVERY_PRICE

    platform_fee = round(delivery_price * PLATFORM_FEE_RATE, 2)
    courier_payout = round(delivery_price - platform_fee, 2)

    total_revenue = platform_fee
    if instant_payout:
        total_revenue = round(total_revenue + INSTANT_PAYOUT_FEE, 2)

    vat_on_fee = round(total_revenue * VAT_RATE, 2) if vat_registered else 0.0
    net_revenue = round(total_revenue - vat_on_fee, 2)

    return {
        "delivery_price": delivery_price,
        "platform_fee_15pct": platform_fee,
        "courier_payout": courier_payout,
        "instant_payout_requested": instant_payout,
        "instant_payout_fee": INSTANT_PAYOUT_FEE if instant_payout else 0.0,
        "total_prixio_revenue": total_revenue,
        "vat_registered": vat_registered,
        "vat_on_revenue": vat_on_fee,
        "net_revenue_after_vat": net_revenue,
    }


def main():
    parser = argparse.ArgumentParser(description="Courio delivery fee calculator")
    parser.add_argument("--delivery", type=float, required=True,
                        help="Delivery price in GEL")
    parser.add_argument("--vat", action="store_true", help="Include VAT (if VAT-registered)")
    parser.add_argument("--instant", action="store_true",
                        help="Include instant payout fee (0.50 GEL)")
    args = parser.parse_args()

    r = calculate_courio(args.delivery, args.vat, args.instant)

    print(f"\n{'='*55}")
    print(f"  COURIO DELIVERY — Prixio LLC")
    print(f"  VAT-registered: {'Yes' if r['vat_registered'] else 'No'}")
    print(f"{'='*55}")
    print(f"  Delivery price:             {r['delivery_price']:>12.2f} GEL")
    print(f"  (min {MIN_DELIVERY_PRICE:.0f} GEL enforced)")
    print(f"  ───────────────────────────────────────────────────")
    print(f"  Platform fee (15%):         {r['platform_fee_15pct']:>12.2f} GEL  (revenue)")
    print(f"  Courier payout (85%):       {r['courier_payout']:>12.2f} GEL  (liability)")
    if r['instant_payout_requested']:
        print(f"  Instant payout fee:        +{r['instant_payout_fee']:>12.2f} GEL  (revenue)")
    print(f"  ───────────────────────────────────────────────────")
    print(f"  Total Prixio revenue:       {r['total_prixio_revenue']:>12.2f} GEL")
    if r['vat_registered']:
        print(f"  VAT on revenue (18%):      -{r['vat_on_revenue']:>12.2f} GEL")
    print(f"  Net revenue:                {r['net_revenue_after_vat']:>12.2f} GEL")
    print(f"\n  NOTE: Courier payout ({r['courier_payout']:.2f} GEL) is LIABILITY,")
    print(f"  not revenue. Only fees count for VAT threshold.")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
