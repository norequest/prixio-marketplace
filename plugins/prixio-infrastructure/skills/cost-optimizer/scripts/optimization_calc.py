#!/usr/bin/env python3
"""
Prixio Infrastructure Cost Optimizer

Analyzes current infrastructure spending and generates optimization
recommendations for Prixio LLC projects (Lotify, Courio, marketplace).

Usage:
    # Custom configuration:
    python optimization_calc.py --current-json '{
        "vercel": {"plan": "hobby", "cost_gel": 0},
        "railway": {"plan": "starter", "cost_gel": 15},
        "supabase_lotify": {"plan": "free", "cost_gel": 0},
        "supabase_courio": {"plan": "free", "cost_gel": 0},
        "upstash": {"plan": "free", "cost_gel": 0},
        "sentry": {"plan": "free", "cost_gel": 0},
        "domain": {"provider": "namecheap", "cost_gel": 30},
        "maps_api": {"provider": "mapbox", "cost_gel": 0}
    }' --vat

    # Preset configurations:
    python optimization_calc.py --preset current_free
    python optimization_calc.py --preset current_paid --vat
    python optimization_calc.py --preset growth --vat
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Optional


# --- Constants ---

# Approximate USD to GEL conversion rate
USD_TO_GEL = 2.75
EUR_TO_GEL = 2.95

# Georgian VAT reverse-charge rate for foreign digital services
VAT_RATE = 0.18


# --- Presets ---

PRESETS = {
    "current_free": {
        "description": "All services on free tiers (pre-revenue Prixio)",
        "services": {
            "vercel": {"plan": "hobby", "cost_gel": 0, "currency": "GEL"},
            "cloudflare_pages": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "railway": {"plan": "trial", "cost_gel": 0, "currency": "GEL"},
            "fly_io": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "supabase_lotify": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "supabase_courio": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "upstash": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "cloudflare_r2": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "sentry": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "resend": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "mapbox": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "fcm": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "uptimerobot": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "github_actions": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "cloudflare_dns": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "domain_com": {"provider": "namecheap", "cost_gel": 2.1, "currency": "GEL", "note": "~25 GEL/yr amortized"},
            "domain_ge": {"provider": "nic.ge", "cost_gel": 3.3, "currency": "GEL", "note": "~40 GEL/yr amortized"},
        },
    },
    "current_paid": {
        "description": "Railway starter + Supabase Pro for Lotify (early revenue)",
        "services": {
            "vercel": {"plan": "team", "cost_gel": 55, "currency": "USD", "cost_usd": 20},
            "railway": {"plan": "developer", "cost_gel": 41.25, "currency": "USD", "cost_usd": 15},
            "supabase_lotify": {"plan": "pro", "cost_gel": 68.75, "currency": "USD", "cost_usd": 25},
            "supabase_courio": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "upstash": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "cloudflare_r2": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "sentry": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "resend": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "mapbox": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "fcm": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "uptimerobot": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "github_actions": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "cloudflare_dns": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "domain_com": {"provider": "namecheap", "cost_gel": 2.1, "currency": "GEL"},
            "domain_ge": {"provider": "nic.ge", "cost_gel": 3.3, "currency": "GEL"},
            "magti_sms": {"provider": "magti", "cost_gel": 5, "currency": "GEL", "note": "estimated ~100 SMS/mo"},
        },
    },
    "growth": {
        "description": "Multiple paid services (scaling phase)",
        "services": {
            "vercel": {"plan": "team", "cost_gel": 55, "currency": "USD", "cost_usd": 20},
            "railway": {"plan": "team", "cost_gel": 82.5, "currency": "USD", "cost_usd": 30},
            "supabase_lotify": {"plan": "pro", "cost_gel": 68.75, "currency": "USD", "cost_usd": 25},
            "supabase_courio": {"plan": "pro", "cost_gel": 68.75, "currency": "USD", "cost_usd": 25},
            "upstash": {"plan": "pay_as_you_go", "cost_gel": 27.5, "currency": "USD", "cost_usd": 10},
            "cloudflare_r2": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "sentry": {"plan": "team", "cost_gel": 71.5, "currency": "USD", "cost_usd": 26},
            "resend": {"plan": "growth", "cost_gel": 55, "currency": "USD", "cost_usd": 20},
            "mapbox": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "fcm": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "uptimerobot": {"plan": "pro", "cost_gel": 19.25, "currency": "USD", "cost_usd": 7},
            "github_actions": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "cloudflare_dns": {"plan": "free", "cost_gel": 0, "currency": "GEL"},
            "hetzner_vps": {"plan": "cx22", "cost_gel": 11.8, "currency": "EUR", "cost_eur": 4},
            "domain_com": {"provider": "namecheap", "cost_gel": 2.1, "currency": "GEL"},
            "domain_ge": {"provider": "nic.ge", "cost_gel": 3.3, "currency": "GEL"},
            "magti_sms": {"provider": "magti", "cost_gel": 25, "currency": "GEL", "note": "estimated ~500 SMS/mo"},
            "tbc_pay": {"provider": "tbc", "cost_gel": 50, "currency": "GEL", "note": "estimated processing fees"},
        },
    },
}


# --- Data Structures ---


@dataclass
class Recommendation:
    action: str
    description: str
    current_cost_gel: float
    optimized_cost_gel: float
    effort: str  # Low, Medium, High
    risk: str  # Low, Medium, High
    prerequisites: list[str] = field(default_factory=list)

    @property
    def savings_gel(self) -> float:
        return self.current_cost_gel - self.optimized_cost_gel

    @property
    def savings_percent(self) -> float:
        if self.current_cost_gel == 0:
            return 0.0
        return (self.savings_gel / self.current_cost_gel) * 100


# --- Free Tier Limits ---

FREE_TIER_LIMITS = {
    "vercel": {"bandwidth_gb": 100, "deploys_per_day": 100, "commercial": False},
    "railway": {"credit_usd": 5, "exec_hours": 500},
    "fly_io": {"vms": 3, "bandwidth_gb": 160, "storage_gb": 3},
    "render": {"hours": 750, "spin_down_min": 15},
    "cloudflare_pages": {"bandwidth_gb": "unlimited", "builds_per_month": 500},
    "supabase": {"db_mb": 500, "connections": 50, "storage_gb": 1, "bandwidth_gb": 2, "projects": 2},
    "upstash": {"commands_per_day": 10000, "max_data_mb": 256, "databases": 1},
    "cloudflare_r2": {"storage_gb": 10, "reads_per_month": 1000000, "writes_per_month": 100000},
    "sentry": {"errors_per_month": 5000, "users": 1, "retention_days": 30},
    "resend": {"emails_per_day": 100, "emails_per_month": 3000, "domains": 1},
    "google_maps": {"monthly_credit_usd": 200},
    "mapbox": {"map_loads_per_month": 50000, "geocoding_per_month": 100000},
    "fcm": {"pushes": "unlimited"},
    "uptimerobot": {"monitors": 50, "check_interval_min": 5},
    "github_actions": {"minutes_public": 2000, "minutes_private": 500},
    "cloudflare_dns": {"queries": "unlimited"},
}


# --- Analysis Engine ---


def is_foreign_service(service_name: str) -> bool:
    """Determine if a service is foreign (subject to reverse-charge VAT)."""
    georgian_services = {
        "tbc_pay", "bog_ipay", "magti_sms", "domain_ge",
    }
    return service_name not in georgian_services


def calculate_vat(cost_gel: float, service_name: str) -> float:
    """Calculate VAT reverse-charge for foreign digital services."""
    if is_foreign_service(service_name) and cost_gel > 0:
        return cost_gel * VAT_RATE
    return 0.0


def analyze_services(services: dict, apply_vat: bool = False) -> dict:
    """Analyze all services and compute costs."""
    total_cost = 0.0
    total_vat = 0.0
    service_details = []

    for name, config in services.items():
        cost = config.get("cost_gel", 0)
        vat = calculate_vat(cost, name) if apply_vat else 0.0
        total_with_vat = cost + vat

        detail = {
            "name": name,
            "plan": config.get("plan", config.get("provider", "unknown")),
            "base_cost_gel": cost,
            "vat_gel": round(vat, 2),
            "total_cost_gel": round(total_with_vat, 2),
            "is_foreign": is_foreign_service(name),
            "note": config.get("note", ""),
        }
        service_details.append(detail)

        total_cost += cost
        total_vat += vat

    return {
        "services": service_details,
        "total_base_cost": round(total_cost, 2),
        "total_vat": round(total_vat, 2),
        "total_cost_with_vat": round(total_cost + total_vat, 2),
    }


def generate_recommendations(services: dict, apply_vat: bool = False) -> list[Recommendation]:
    """Generate optimization recommendations based on current services."""
    recommendations = []

    # --- Recommendation: Consolidate APIs on Hetzner VPS ---
    railway_cost = services.get("railway", {}).get("cost_gel", 0)
    fly_cost = services.get("fly_io", {}).get("cost_gel", 0)
    render_cost = services.get("render", {}).get("cost_gel", 0)
    hosting_total = railway_cost + fly_cost + render_cost

    hetzner_cx22_gel = 4 * EUR_TO_GEL  # ~11.80 GEL

    if hosting_total > hetzner_cx22_gel:
        savings = hosting_total - hetzner_cx22_gel
        if apply_vat:
            # Both are foreign, but Hetzner may be cheaper even with VAT
            current_vat = hosting_total * VAT_RATE
            new_vat = hetzner_cx22_gel * VAT_RATE
            savings = (hosting_total + current_vat) - (hetzner_cx22_gel + new_vat)

        recommendations.append(Recommendation(
            action="Consolidate APIs on Hetzner VPS",
            description=(
                f"Replace Railway/fly.io/Render with a single Hetzner CX22 VPS "
                f"(~{hetzner_cx22_gel:.0f} GEL/mo). Run Lotify + Courio APIs behind "
                f"Caddy reverse proxy. 2 vCPU, 4GB RAM handles both easily."
            ),
            current_cost_gel=round(hosting_total + (hosting_total * VAT_RATE if apply_vat else 0), 2),
            optimized_cost_gel=round(hetzner_cx22_gel + (hetzner_cx22_gel * VAT_RATE if apply_vat else 0), 2),
            effort="Medium",
            risk="Medium",
            prerequisites=[
                "Set up Hetzner VPS with Docker or systemd services",
                "Configure Caddy as reverse proxy with automatic HTTPS",
                "Set up deployment pipeline (GitHub Actions SSH deploy)",
                "Test both APIs on VPS before DNS switch",
            ],
        ))

    # --- Recommendation: Switch from Vercel Team to Cloudflare Pages ---
    vercel = services.get("vercel", {})
    if vercel.get("plan") == "team" and vercel.get("cost_gel", 0) > 0:
        vercel_cost = vercel["cost_gel"]
        if apply_vat:
            vercel_cost += vercel_cost * VAT_RATE

        recommendations.append(Recommendation(
            action="Switch from Vercel Team to Cloudflare Pages",
            description=(
                "Cloudflare Pages offers unlimited bandwidth, 500 builds/month, "
                "and is completely free. Both support Next.js (via @cloudflare/next-on-pages). "
                "Eliminates $20/mo Vercel Team cost."
            ),
            current_cost_gel=round(vercel_cost, 2),
            optimized_cost_gel=0,
            effort="Medium",
            risk="Low",
            prerequisites=[
                "Test build with @cloudflare/next-on-pages",
                "Verify all API routes work on Cloudflare Workers runtime",
                "Move DNS to Cloudflare (if not already)",
                "Update CI/CD pipeline",
            ],
        ))

    # --- Recommendation: Switch from Twilio to Magti ---
    twilio = services.get("twilio", {})
    if twilio.get("cost_gel", 0) > 0:
        magti_estimated = twilio["cost_gel"] * 0.25  # Magti is ~3-5x cheaper
        recommendations.append(Recommendation(
            action="Switch from Twilio to Magti for Georgian SMS",
            description=(
                "Magti SMS costs ~0.03-0.05 GEL per message vs Twilio's ~0.15-0.20 GEL. "
                "For Georgian phone numbers, Magti provides better delivery rates and "
                "3-5x lower cost. Also eliminates VAT reverse-charge as Magti is Georgian."
            ),
            current_cost_gel=round(twilio["cost_gel"] + (twilio["cost_gel"] * VAT_RATE if apply_vat else 0), 2),
            optimized_cost_gel=round(magti_estimated, 2),
            effort="Medium",
            risk="Low",
            prerequisites=[
                "Integrate Magti SMS API",
                "Test delivery to Georgian mobile numbers",
                "Keep Twilio as fallback for international numbers",
            ],
        ))

    # --- Recommendation: Use Cloudflare R2 instead of Supabase Storage ---
    for svc_name in ["supabase_lotify", "supabase_courio"]:
        svc = services.get(svc_name, {})
        if svc.get("plan") == "pro":
            recommendations.append(Recommendation(
                action=f"Offload {svc_name} media to Cloudflare R2",
                description=(
                    "Move user-uploaded images and auction photos to Cloudflare R2 "
                    "(10GB free, zero egress fees). Reduces Supabase Storage usage "
                    "and bandwidth, potentially allowing downgrade back to free tier "
                    "if database stays under 500MB."
                ),
                current_cost_gel=0,
                optimized_cost_gel=0,
                effort="Medium",
                risk="Low",
                prerequisites=[
                    "Set up R2 bucket with public access or signed URLs",
                    "Update upload logic to write to R2 via S3-compatible API",
                    "Migrate existing files from Supabase Storage to R2",
                    "Update frontend image URLs",
                ],
            ))

    # --- Recommendation: Downgrade Sentry if on paid plan ---
    sentry = services.get("sentry", {})
    if sentry.get("plan") == "team" and sentry.get("cost_gel", 0) > 0:
        sentry_cost = sentry["cost_gel"]
        if apply_vat:
            sentry_cost += sentry_cost * VAT_RATE

        recommendations.append(Recommendation(
            action="Downgrade Sentry to free tier",
            description=(
                "Sentry free tier offers 5,000 errors/month. If you're exceeding this, "
                "prioritize fixing the bugs causing errors rather than paying to track more. "
                "Use structured logging (pino) as a supplement."
            ),
            current_cost_gel=round(sentry_cost, 2),
            optimized_cost_gel=0,
            effort="Low",
            risk="Low",
            prerequisites=[
                "Review current error volume -- fix top error sources",
                "Set up pino structured logging as backup",
                "Configure Sentry sampling rate to stay within free limits",
            ],
        ))

    # --- Recommendation: Use Cloudflare Registrar for .com domains ---
    domain_com = services.get("domain_com", {})
    if domain_com.get("provider") == "namecheap":
        namecheap_monthly = domain_com.get("cost_gel", 2.1)
        cloudflare_monthly = 9 * USD_TO_GEL / 12  # At-cost, ~$9/yr
        if namecheap_monthly > cloudflare_monthly:
            recommendations.append(Recommendation(
                action="Transfer .com domains to Cloudflare Registrar",
                description=(
                    "Cloudflare Registrar charges at-cost (no markup). "
                    "Typical .com is ~$9.15/year vs Namecheap ~$12-14/year. "
                    "Small savings but zero effort after transfer."
                ),
                current_cost_gel=round(namecheap_monthly * 12, 2),
                optimized_cost_gel=round(cloudflare_monthly * 12, 2),
                effort="Low",
                risk="Low",
                prerequisites=[
                    "Unlock domain at Namecheap",
                    "Initiate transfer at Cloudflare (domain must be >60 days old)",
                    "Confirm transfer via email",
                ],
            ))

    # --- Recommendation: Consolidate Supabase projects ---
    lotify_supa = services.get("supabase_lotify", {})
    courio_supa = services.get("supabase_courio", {})
    if lotify_supa.get("plan") == "pro" and courio_supa.get("plan") == "pro":
        combined_cost = lotify_supa.get("cost_gel", 0) + courio_supa.get("cost_gel", 0)
        single_pro_cost = 25 * USD_TO_GEL
        if apply_vat:
            combined_cost += combined_cost * VAT_RATE
            single_pro_cost += single_pro_cost * VAT_RATE

        recommendations.append(Recommendation(
            action="Consolidate Supabase into single Pro project with schemas",
            description=(
                "Run Lotify and Courio in separate PostgreSQL schemas within one "
                "Supabase Pro project. Saves one Pro subscription ($25/mo). "
                "Use schema-level RLS and separate API keys via custom claims."
            ),
            current_cost_gel=round(combined_cost, 2),
            optimized_cost_gel=round(single_pro_cost, 2),
            effort="High",
            risk="Medium",
            prerequisites=[
                "Create schema migration plan",
                "Set up schema-level RLS policies",
                "Update connection strings in both apps",
                "Test thoroughly -- data isolation is critical",
                "Plan rollback strategy",
            ],
        ))

    # --- Recommendation: Replace UptimeRobot Pro with free alternatives ---
    uptimerobot = services.get("uptimerobot", {})
    if uptimerobot.get("plan") == "pro" and uptimerobot.get("cost_gel", 0) > 0:
        ur_cost = uptimerobot["cost_gel"]
        if apply_vat:
            ur_cost += ur_cost * VAT_RATE

        recommendations.append(Recommendation(
            action="Downgrade UptimeRobot to free tier",
            description=(
                "UptimeRobot free provides 50 monitors at 5-minute intervals. "
                "For early-stage products, 5-minute checks are sufficient. "
                "Supplement with Sentry for application-level monitoring."
            ),
            current_cost_gel=round(ur_cost, 2),
            optimized_cost_gel=0,
            effort="Low",
            risk="Low",
            prerequisites=[
                "Verify 5-minute check interval is acceptable",
                "Keep only essential monitors (remove duplicates)",
            ],
        ))

    # --- Recommendation: Downgrade Resend if on paid plan ---
    resend = services.get("resend", {})
    if resend.get("plan") == "growth" and resend.get("cost_gel", 0) > 0:
        resend_cost = resend["cost_gel"]
        if apply_vat:
            resend_cost += resend_cost * VAT_RATE

        recommendations.append(Recommendation(
            action="Evaluate Resend usage -- consider downgrade to free",
            description=(
                "Resend free tier allows 100 emails/day (3,000/month). "
                "If actual transactional email volume is under this limit, "
                "downgrade and save $20/mo."
            ),
            current_cost_gel=round(resend_cost, 2),
            optimized_cost_gel=0,
            effort="Low",
            risk="Low",
            prerequisites=[
                "Check actual email volume in Resend dashboard",
                "Verify 100/day limit is sufficient",
            ],
        ))

    # Sort by savings (highest first), then by effort (Low < Medium < High)
    effort_order = {"Low": 0, "Medium": 1, "High": 2}
    recommendations.sort(
        key=lambda r: (-r.savings_gel, effort_order.get(r.effort, 99))
    )

    return recommendations


# --- Output Formatting ---


def format_gel(amount: float) -> str:
    """Format amount in GEL."""
    return f"{amount:,.2f} GEL"


def print_report(
    analysis: dict,
    recommendations: list[Recommendation],
    apply_vat: bool,
    preset_name: Optional[str] = None,
):
    """Print the full optimization report."""
    print("=" * 70)
    print("  PRIXIO INFRASTRUCTURE COST OPTIMIZATION REPORT")
    print("=" * 70)

    if preset_name:
        preset_info = PRESETS.get(preset_name, {})
        print(f"\n  Preset: {preset_name} -- {preset_info.get('description', '')}")

    print(f"  VAT reverse-charge (18%): {'INCLUDED' if apply_vat else 'NOT INCLUDED'}")
    print()

    # --- Current Spending ---
    print("-" * 70)
    print("  CURRENT MONTHLY SPENDING")
    print("-" * 70)
    print()
    print(f"  {'Service':<25} {'Plan':<15} {'Base':>10} {'VAT':>10} {'Total':>10}")
    print(f"  {'-'*25} {'-'*15} {'-'*10} {'-'*10} {'-'*10}")

    for svc in analysis["services"]:
        if svc["base_cost_gel"] > 0 or svc["vat_gel"] > 0:
            note = f" ({svc['note']})" if svc.get("note") else ""
            print(
                f"  {svc['name']:<25} {svc['plan']:<15} "
                f"{format_gel(svc['base_cost_gel']):>10} "
                f"{format_gel(svc['vat_gel']):>10} "
                f"{format_gel(svc['total_cost_gel']):>10}"
                f"{note}"
            )

    # Free services summary
    free_services = [s for s in analysis["services"] if s["base_cost_gel"] == 0 and s["vat_gel"] == 0]
    if free_services:
        free_names = ", ".join(s["name"] for s in free_services)
        print(f"\n  Free tier: {free_names}")

    print()
    print(f"  {'TOTAL BASE COST:':>40} {format_gel(analysis['total_base_cost']):>10}")
    if apply_vat:
        print(f"  {'TOTAL VAT (18%):':>40} {format_gel(analysis['total_vat']):>10}")
    print(f"  {'TOTAL MONTHLY COST:':>40} {format_gel(analysis['total_cost_with_vat']):>10}")
    print()

    # --- Recommendations ---
    if not recommendations:
        print("-" * 70)
        print("  No optimization recommendations -- you are already well-optimized!")
        print("-" * 70)
        return

    total_current = sum(r.current_cost_gel for r in recommendations)
    total_optimized = sum(r.optimized_cost_gel for r in recommendations)
    total_savings = sum(r.savings_gel for r in recommendations)

    print("-" * 70)
    print("  OPTIMIZATION RECOMMENDATIONS")
    print("-" * 70)

    for i, rec in enumerate(recommendations, 1):
        if rec.savings_gel <= 0:
            continue
        print()
        print(f"  [{i}] {rec.action}")
        print(f"      {rec.description}")
        print(f"      Current: {format_gel(rec.current_cost_gel)} -> Optimized: {format_gel(rec.optimized_cost_gel)}")
        print(f"      SAVES: {format_gel(rec.savings_gel)}/mo ({rec.savings_percent:.0f}%)")
        print(f"      Effort: {rec.effort} | Risk: {rec.risk}")
        if rec.prerequisites:
            print("      Prerequisites:")
            for prereq in rec.prerequisites:
                print(f"        - {prereq}")

    # Zero-savings recommendations (optimizations that don't save money directly)
    zero_savings = [r for r in recommendations if r.savings_gel <= 0]
    if zero_savings:
        print()
        print("  NON-MONETARY OPTIMIZATIONS:")
        for rec in zero_savings:
            print(f"  - {rec.action}: {rec.description[:80]}...")

    # --- Summary ---
    print()
    print("-" * 70)
    print("  SAVINGS SUMMARY")
    print("-" * 70)
    print()
    print(f"  Current addressable cost:  {format_gel(total_current)}/mo")
    print(f"  After optimization:        {format_gel(total_optimized)}/mo")
    print(f"  Total potential savings:   {format_gel(total_savings)}/mo")
    if total_current > 0:
        pct = (total_savings / total_current) * 100
        print(f"  Savings percentage:        {pct:.0f}%")
    print(f"  Annual savings:            {format_gel(total_savings * 12)}/yr")
    print()

    final_monthly = analysis["total_cost_with_vat"] - total_savings
    print(f"  FINAL OPTIMIZED MONTHLY COST: {format_gel(max(0, final_monthly))}")
    print()
    print("=" * 70)


# --- Main ---


def main():
    parser = argparse.ArgumentParser(
        description="Prixio Infrastructure Cost Optimizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --preset current_free
  %(prog)s --preset current_paid --vat
  %(prog)s --preset growth --vat
  %(prog)s --current-json '{"vercel": {"plan": "hobby", "cost_gel": 0}}' --vat
        """,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--current-json",
        type=str,
        help="JSON object describing current services and costs",
    )
    group.add_argument(
        "--preset",
        type=str,
        choices=list(PRESETS.keys()),
        help="Use a preset configuration",
    )
    parser.add_argument(
        "--vat",
        action="store_true",
        help="Include 18%% VAT reverse-charge on foreign digital services",
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results as JSON instead of formatted text",
    )

    args = parser.parse_args()

    # Load services
    if args.preset:
        services = PRESETS[args.preset]["services"]
    else:
        try:
            services = json.loads(args.current_json)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
            sys.exit(1)

    # Analyze
    analysis = analyze_services(services, apply_vat=args.vat)
    recommendations = generate_recommendations(services, apply_vat=args.vat)

    if args.json_output:
        output = {
            "analysis": analysis,
            "recommendations": [
                {
                    "action": r.action,
                    "description": r.description,
                    "current_cost_gel": r.current_cost_gel,
                    "optimized_cost_gel": r.optimized_cost_gel,
                    "savings_gel": r.savings_gel,
                    "savings_percent": round(r.savings_percent, 1),
                    "effort": r.effort,
                    "risk": r.risk,
                    "prerequisites": r.prerequisites,
                }
                for r in recommendations
            ],
            "summary": {
                "total_current_cost": analysis["total_cost_with_vat"],
                "total_potential_savings": round(sum(r.savings_gel for r in recommendations), 2),
                "optimized_cost": round(
                    analysis["total_cost_with_vat"] - sum(r.savings_gel for r in recommendations), 2
                ),
            },
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print_report(analysis, recommendations, apply_vat=args.vat, preset_name=args.preset)


if __name__ == "__main__":
    main()
