#!/usr/bin/env python3
"""Marketing and sales cost calculator for Prixio LLC.

Calculates advertising budgets, CAC, and ROI for Georgian market.
Sources: platform-accounting.md, Georgian market benchmarks
Updated: March 2026
"""
import argparse
import json

VAT_RATE = 0.18

PRESETS = {
    "bootstrap": {
        "google_ads": 100,
        "facebook_ads": 150,
        "tiktok_ads": 0,
        "seo_tools": 0,
        "social_tools": 0,
        "content_creation": 100,
        "graphic_design": 0,
        "photography_video": 0,
        "outdoor_ads": 0,
        "print_materials": 50,
        "events": 0,
        "referral_bonuses": 50,
        "crm": 0,
        "sales_commissions": 0,
        "mymarket_listings": 50,
        "telegram_promotion": 30,
    },
    "growth": {
        "google_ads": 600,
        "facebook_ads": 500,
        "tiktok_ads": 200,
        "seo_tools": 50,
        "social_tools": 30,
        "content_creation": 300,
        "graphic_design": 200,
        "photography_video": 100,
        "outdoor_ads": 0,
        "print_materials": 100,
        "events": 200,
        "referral_bonuses": 200,
        "crm": 50,
        "sales_commissions": 0,
        "mymarket_listings": 150,
        "telegram_promotion": 80,
    },
    "aggressive": {
        "google_ads": 2500,
        "facebook_ads": 2000,
        "tiktok_ads": 1000,
        "seo_tools": 150,
        "social_tools": 80,
        "content_creation": 800,
        "graphic_design": 500,
        "photography_video": 400,
        "outdoor_ads": 1500,
        "print_materials": 300,
        "events": 800,
        "referral_bonuses": 500,
        "crm": 100,
        "sales_commissions": 500,
        "mymarket_listings": 300,
        "telegram_promotion": 200,
    },
}

CATEGORIES = {
    "google_ads": "Digital Marketing",
    "facebook_ads": "Digital Marketing",
    "tiktok_ads": "Digital Marketing",
    "seo_tools": "Digital Marketing",
    "social_tools": "Digital Marketing",
    "content_creation": "Content & Creative",
    "graphic_design": "Content & Creative",
    "photography_video": "Content & Creative",
    "outdoor_ads": "Offline/Local",
    "print_materials": "Offline/Local",
    "events": "Offline/Local",
    "referral_bonuses": "Offline/Local",
    "crm": "Sales",
    "sales_commissions": "Sales",
    "mymarket_listings": "Georgian Channels",
    "telegram_promotion": "Georgian Channels",
}

LABELS = {
    "google_ads": "Google Ads",
    "facebook_ads": "Facebook/Instagram Ads",
    "tiktok_ads": "TikTok Ads",
    "seo_tools": "SEO Tools/Services",
    "social_tools": "Social Media Tools",
    "content_creation": "Content Creation",
    "graphic_design": "Graphic Design",
    "photography_video": "Photo/Video Production",
    "outdoor_ads": "Outdoor Advertising",
    "print_materials": "Print Materials/Flyers",
    "events": "Events/Sponsorship",
    "referral_bonuses": "Referral Bonuses",
    "crm": "CRM Software",
    "sales_commissions": "Sales Commissions",
    "mymarket_listings": "mymarket.ge Listings",
    "telegram_promotion": "Telegram Promotion",
}

# Foreign platforms subject to reverse-charge VAT
FOREIGN_PLATFORMS = {"google_ads", "facebook_ads", "tiktok_ads", "seo_tools",
                     "social_tools", "crm"}


def calculate_marketing(costs: dict, new_customers: int = 0,
                        monthly_revenue: float = 0,
                        vat_registered: bool = False) -> dict:
    category_totals = {}
    for key, amount in costs.items():
        cat = CATEGORIES.get(key, "Other")
        category_totals[cat] = round(category_totals.get(cat, 0) + amount, 2)

    grand_total = round(sum(costs.values()), 2)

    foreign_total = round(sum(v for k, v in costs.items() if k in FOREIGN_PLATFORMS), 2)
    reverse_charge_vat = round(foreign_total * VAT_RATE, 2)
    vat_net_impact = 0.0 if vat_registered else reverse_charge_vat
    total_with_vat = round(grand_total + vat_net_impact, 2)

    cac = round(total_with_vat / new_customers, 2) if new_customers > 0 else None
    roi_pct = round((monthly_revenue - total_with_vat) / total_with_vat * 100, 1) \
        if monthly_revenue > 0 and total_with_vat > 0 else None

    return {
        "line_items": costs,
        "category_totals": category_totals,
        "grand_total": grand_total,
        "foreign_platforms_total": foreign_total,
        "reverse_charge_vat": reverse_charge_vat,
        "vat_registered": vat_registered,
        "vat_net_impact": vat_net_impact,
        "total_with_vat_impact": total_with_vat,
        "new_customers": new_customers,
        "cac": cac,
        "monthly_revenue": monthly_revenue,
        "roi_pct": roi_pct,
    }


def main():
    parser = argparse.ArgumentParser(description="Prixio marketing cost calculator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preset", choices=["bootstrap", "growth", "aggressive"],
                       help="Use preset marketing profile")
    group.add_argument("--budget-json", type=str,
                       help="JSON object with marketing line items")
    parser.add_argument("--new-customers", type=int, default=0,
                        help="New customers acquired this month (for CAC)")
    parser.add_argument("--monthly-revenue", type=float, default=0,
                        help="Monthly revenue in GEL (for ROI)")
    parser.add_argument("--vat", action="store_true",
                        help="Include reverse-charge VAT analysis")
    args = parser.parse_args()

    if args.preset:
        costs = PRESETS[args.preset]
        preset_name = args.preset.upper()
    else:
        costs = json.loads(args.budget_json)
        preset_name = "CUSTOM"

    r = calculate_marketing(costs, args.new_customers,
                            args.monthly_revenue, args.vat)

    print(f"\n{'='*60}")
    print(f"  MARKETING COSTS -- Prixio LLC ({preset_name})")
    print(f"  VAT-registered: {'Yes' if r['vat_registered'] else 'No'}")
    print(f"{'='*60}")

    current_cat = None
    for key, amount in r["line_items"].items():
        if amount == 0:
            continue
        cat = CATEGORIES.get(key, "Other")
        if cat != current_cat:
            current_cat = cat
            print(f"\n  [{cat}]")
        label = LABELS.get(key, key)
        print(f"    {label:<35} {amount:>10.2f} GEL")

    print(f"\n  {'─'*54}")
    print(f"\n  CATEGORY SUMMARY:")
    for cat, total in r["category_totals"].items():
        if total == 0:
            continue
        pct = (total / r["grand_total"] * 100) if r["grand_total"] > 0 else 0
        print(f"    {cat:<35} {total:>10.2f} GEL  ({pct:>5.1f}%)")

    print(f"\n  {'─'*54}")
    print(f"  Subtotal:                             {r['grand_total']:>10.2f} GEL")

    if args.vat:
        print(f"\n  REVERSE-CHARGE VAT (foreign ad platforms):")
        print(f"    Foreign platforms total:             {r['foreign_platforms_total']:>10.2f} GEL")
        print(f"    Reverse-charge VAT (18%):           {r['reverse_charge_vat']:>10.2f} GEL")
        if r["vat_registered"]:
            print(f"    Net VAT impact:                     {0:>10.2f} GEL")
        else:
            print(f"    Net VAT impact (no credit):        +{r['vat_net_impact']:>10.2f} GEL")

    print(f"\n  TOTAL MONTHLY MARKETING:              {r['total_with_vat_impact']:>10.2f} GEL")

    if r["cac"] is not None:
        print(f"\n  ACQUISITION METRICS:")
        print(f"    New customers this month:           {r['new_customers']:>10}")
        print(f"    Customer Acquisition Cost (CAC):    {r['cac']:>10.2f} GEL")

    if r["roi_pct"] is not None:
        print(f"\n  ROI ANALYSIS:")
        print(f"    Monthly revenue:                    {r['monthly_revenue']:>10.2f} GEL")
        print(f"    Marketing spend:                    {r['total_with_vat_impact']:>10.2f} GEL")
        print(f"    Marketing ROI:                      {r['roi_pct']:>9.1f}%")
        if r["roi_pct"] < 0:
            print(f"    STATUS: Negative ROI -- marketing costs exceed revenue")
        elif r["roi_pct"] < 100:
            print(f"    STATUS: Positive but low -- revenue covers marketing")
        else:
            print(f"    STATUS: Strong ROI -- revenue > 2x marketing spend")

    print(f"\n  Annual projection:                    {r['total_with_vat_impact'] * 12:>10.2f} GEL")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
