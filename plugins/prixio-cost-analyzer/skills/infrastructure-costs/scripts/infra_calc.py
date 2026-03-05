#!/usr/bin/env python3
"""Infrastructure cost calculator for Prixio LLC.

Calculates monthly cloud, API, and DevOps costs with Georgian tax context.
Sources: platform-accounting.md, infohub.rs.ge
Updated: March 2026
"""
import argparse
import json

VAT_RATE = 0.18

PRESETS = {
    "starter": {
        "servers": 80,
        "database": 40,
        "cdn_storage": 15,
        "domain_ssl": 8,
        "payment_gateway": 20,
        "sms_notifications": 15,
        "email_service": 0,
        "maps_api": 25,
        "push_notifications": 0,
        "ci_cd": 0,
        "monitoring": 0,
        "logging": 0,
    },
    "growth": {
        "servers": 250,
        "database": 150,
        "cdn_storage": 60,
        "domain_ssl": 10,
        "payment_gateway": 80,
        "sms_notifications": 60,
        "email_service": 25,
        "maps_api": 100,
        "push_notifications": 15,
        "ci_cd": 30,
        "monitoring": 25,
        "logging": 20,
    },
    "scale": {
        "servers": 800,
        "database": 500,
        "cdn_storage": 200,
        "domain_ssl": 15,
        "payment_gateway": 300,
        "sms_notifications": 200,
        "email_service": 80,
        "maps_api": 350,
        "push_notifications": 50,
        "ci_cd": 80,
        "monitoring": 60,
        "logging": 50,
    },
}

CATEGORIES = {
    "servers": "Cloud/Hosting",
    "database": "Cloud/Hosting",
    "cdn_storage": "Cloud/Hosting",
    "domain_ssl": "Cloud/Hosting",
    "payment_gateway": "Third-party Services",
    "sms_notifications": "Third-party Services",
    "email_service": "Third-party Services",
    "maps_api": "Third-party Services",
    "push_notifications": "Third-party Services",
    "ci_cd": "DevOps",
    "monitoring": "DevOps",
    "logging": "DevOps",
}

LABELS = {
    "servers": "Servers/VPS",
    "database": "Managed Database",
    "cdn_storage": "CDN & Storage",
    "domain_ssl": "Domain & SSL",
    "payment_gateway": "Payment Gateway (TBC Pay)",
    "sms_notifications": "SMS/Notifications",
    "email_service": "Email Service",
    "maps_api": "Maps API (Courio)",
    "push_notifications": "Push Notifications",
    "ci_cd": "CI/CD Pipeline",
    "monitoring": "Monitoring & Uptime",
    "logging": "Logging",
}

# Foreign services subject to reverse-charge VAT
FOREIGN_SERVICES = {
    "servers", "database", "cdn_storage", "email_service", "maps_api",
    "push_notifications", "ci_cd", "monitoring", "logging",
}


def calculate_infra(costs: dict, vat_registered: bool = False) -> dict:
    category_totals = {}
    for key, amount in costs.items():
        cat = CATEGORIES.get(key, "Other")
        category_totals[cat] = round(category_totals.get(cat, 0) + amount, 2)

    grand_total = round(sum(costs.values()), 2)

    foreign_total = round(sum(v for k, v in costs.items() if k in FOREIGN_SERVICES), 2)
    reverse_charge_vat = round(foreign_total * VAT_RATE, 2)

    if vat_registered:
        vat_net_impact = 0.0
    else:
        vat_net_impact = reverse_charge_vat

    total_with_vat = round(grand_total + vat_net_impact, 2)

    return {
        "line_items": costs,
        "category_totals": category_totals,
        "grand_total": grand_total,
        "foreign_services_total": foreign_total,
        "reverse_charge_vat": reverse_charge_vat,
        "vat_registered": vat_registered,
        "vat_net_impact": vat_net_impact,
        "total_with_vat_impact": total_with_vat,
    }


def main():
    parser = argparse.ArgumentParser(description="Prixio infrastructure cost calculator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preset", choices=["starter", "growth", "scale"],
                       help="Use preset cost profile")
    group.add_argument("--monthly-json", type=str,
                       help="JSON object with cost line items")
    parser.add_argument("--vat", action="store_true",
                        help="Include reverse-charge VAT analysis")
    args = parser.parse_args()

    if args.preset:
        costs = PRESETS[args.preset]
        preset_name = args.preset.upper()
    else:
        costs = json.loads(args.monthly_json)
        preset_name = "CUSTOM"

    r = calculate_infra(costs, args.vat)

    print(f"\n{'='*60}")
    print(f"  INFRASTRUCTURE COSTS -- Prixio LLC ({preset_name})")
    print(f"  VAT-registered: {'Yes' if r['vat_registered'] else 'No'}")
    print(f"{'='*60}")

    current_cat = None
    for key, amount in r["line_items"].items():
        cat = CATEGORIES.get(key, "Other")
        if cat != current_cat:
            current_cat = cat
            print(f"\n  [{cat}]")
        label = LABELS.get(key, key)
        print(f"    {label:<35} {amount:>10.2f} GEL")

    print(f"\n  {'─'*54}")
    print(f"\n  CATEGORY SUMMARY:")
    for cat, total in r["category_totals"].items():
        pct = (total / r["grand_total"] * 100) if r["grand_total"] > 0 else 0
        print(f"    {cat:<35} {total:>10.2f} GEL  ({pct:>5.1f}%)")

    print(f"\n  {'─'*54}")
    print(f"  Subtotal:                             {r['grand_total']:>10.2f} GEL")

    if args.vat:
        print(f"\n  REVERSE-CHARGE VAT ANALYSIS:")
        print(f"    Foreign services total:             {r['foreign_services_total']:>10.2f} GEL")
        print(f"    Reverse-charge VAT (18%):           {r['reverse_charge_vat']:>10.2f} GEL")
        if r["vat_registered"]:
            print(f"    Input VAT credit:                  -{r['reverse_charge_vat']:>10.2f} GEL")
            print(f"    Net VAT impact:                     {0:>10.2f} GEL")
        else:
            print(f"    Net VAT impact (no credit):        +{r['vat_net_impact']:>10.2f} GEL")

    print(f"\n  {'─'*54}")
    print(f"  TOTAL MONTHLY INFRASTRUCTURE:         {r['total_with_vat_impact']:>10.2f} GEL")
    print(f"  Annual projection:                    {r['total_with_vat_impact'] * 12:>10.2f} GEL")

    if not r["vat_registered"] and r["reverse_charge_vat"] > 0:
        print(f"\n  NOTE: You pay {r['reverse_charge_vat']:.2f} GEL/month extra in")
        print(f"  reverse-charge VAT since Prixio is not VAT-registered.")
        print(f"  Annual extra cost: {r['reverse_charge_vat'] * 12:.2f} GEL")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
