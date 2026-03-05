#!/usr/bin/env python3
"""
Capacity planning calculator for Prixio LLC platforms (Lotify & Courio).

Usage:
  capacity_calc.py --concurrent-users N [--platform lotify|courio|both]
                   [--peak-multiplier N] [--output json|text]
  capacity_calc.py --preset early|growing|established|scale
                   [--platform lotify|courio|both] [--output json|text]

Examples:
  capacity_calc.py --preset early
  capacity_calc.py --concurrent-users 750 --platform lotify --output json
  capacity_calc.py --preset scale --platform both --output text
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional

# ---------------------------------------------------------------------------
# Infrastructure tier definitions
# ---------------------------------------------------------------------------

TIERS = [
    {
        "name": "Free",
        "server": "Supabase Free + Railway Free",
        "concurrent_users": 50,
        "requests_per_sec": 10,
        "db_connections": 50,
        "websocket_conns": 200,
        "storage_gb": 2,
        "monthly_cost_gel": 0,
    },
    {
        "name": "Starter",
        "server": "Hetzner CX22 + Supabase Pro",
        "concurrent_users": 500,
        "requests_per_sec": 100,
        "db_connections": 200,
        "websocket_conns": 2_000,
        "storage_gb": 8,
        "monthly_cost_gel": 200,
    },
    {
        "name": "Growth",
        "server": "Hetzner CX32 + Supabase Pro",
        "concurrent_users": 2_000,
        "requests_per_sec": 500,
        "db_connections": 500,
        "websocket_conns": 10_000,
        "storage_gb": 50,
        "monthly_cost_gel": 500,
    },
    {
        "name": "Scale",
        "server": "Hetzner CX42 + Supabase Team",
        "concurrent_users": 10_000,
        "requests_per_sec": 2_000,
        "db_connections": 1_000,
        "websocket_conns": 50_000,
        "storage_gb": 100,
        "monthly_cost_gel": 1_500,
    },
    {
        "name": "Enterprise",
        "server": "Multi-server + dedicated DB",
        "concurrent_users": 50_000,
        "requests_per_sec": 10_000,
        "db_connections": 5_000,
        "websocket_conns": 200_000,
        "storage_gb": 500,
        "monthly_cost_gel": 5_000,
    },
]

PRESETS = {
    "early": 100,
    "growing": 500,
    "established": 2_000,
    "scale": 10_000,
}

WARNING_THRESHOLD = 0.80  # Flag resources above 80% utilization


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ResourceEstimate:
    requests_per_sec: float = 0.0
    db_connections: int = 0
    websocket_conns: int = 0
    storage_growth_gb_per_month: float = 0.0
    notes: list = field(default_factory=list)


@dataclass
class PlanResult:
    concurrent_users: int = 0
    peak_multiplier: float = 3.0
    platform: str = "both"
    base_load: dict = field(default_factory=dict)
    peak_load: dict = field(default_factory=dict)
    recommended_tier: dict = field(default_factory=dict)
    bottlenecks: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    monthly_cost_gel: int = 0
    platform_notes: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Platform-specific load calculations
# ---------------------------------------------------------------------------

def calc_lotify_load(concurrent_users: int) -> ResourceEstimate:
    """Calculate Lotify (auction platform) resource requirements."""
    est = ResourceEstimate()

    # Traffic split: 80% browsing, 15% bidding, 5% admin
    browsing_users = concurrent_users * 0.80
    bidding_users = concurrent_users * 0.15
    admin_users = concurrent_users * 0.05

    # Requests/sec: browsing ~0.2 rps/user, bidding ~1 rps/user, admin ~0.1 rps/user
    est.requests_per_sec = (
        browsing_users * 0.2
        + bidding_users * 1.0
        + admin_users * 0.1
    )

    # WebSocket connections: 2x concurrent users (bidders subscribe to multiple auctions)
    est.websocket_conns = int(concurrent_users * 2)

    # DB connections: ~1 per 5 concurrent users with pooling, plus realtime subscriptions
    est.db_connections = int(concurrent_users / 5) + int(bidding_users * 0.5)

    # Storage: ~0.5 GB/month per 100 users (auction images, bid history)
    est.storage_growth_gb_per_month = (concurrent_users / 100) * 0.5

    est.notes = [
        "WebSocket factor: 2x concurrent users (multi-auction subscriptions)",
        "DB write burst at auction end: 10x normal rate for ~30 seconds",
        "Image CDN bandwidth scales with browsing users",
    ]

    return est


def calc_courio_load(concurrent_users: int) -> ResourceEstimate:
    """Calculate Courio (delivery platform) resource requirements."""
    est = ResourceEstimate()

    # Traffic split: 40% consumers, 30% couriers, 20% merchants, 10% admin
    consumer_users = concurrent_users * 0.40
    courier_users = concurrent_users * 0.30
    merchant_users = concurrent_users * 0.20
    admin_users = concurrent_users * 0.10

    # GPS updates: each active courier sends update every 10 seconds
    gps_writes_per_sec = courier_users / 10.0

    # Requests/sec: consumers ~0.3 rps, couriers GPS + app ~0.15 rps,
    # merchants ~0.2 rps, admin ~0.1 rps, plus PostGIS queries (2-3x GPS writes)
    est.requests_per_sec = (
        consumer_users * 0.3
        + courier_users * 0.15
        + merchant_users * 0.2
        + admin_users * 0.1
        + gps_writes_per_sec * 2.5  # PostGIS proximity queries
    )

    # WebSocket: consumers tracking + couriers streaming
    est.websocket_conns = int(consumer_users * 0.5 + courier_users * 1.0)

    # DB connections: GPS streaming holds connections; pooled for rest
    est.db_connections = int(courier_users * 0.3 + (concurrent_users - courier_users) / 5)

    # Storage: GPS data ~1 GB/month per 100 active couriers, plus order data
    est.storage_growth_gb_per_month = (
        (courier_users / 100) * 1.0
        + (consumer_users / 100) * 0.2
    )

    est.notes = [
        f"GPS writes: ~{gps_writes_per_sec:.1f}/sec ({int(courier_users)} active couriers, 10s interval)",
        f"PostGIS queries: ~{gps_writes_per_sec * 2.5:.1f}/sec (proximity checks per GPS update)",
        "Push notifications burst during peak delivery hours (18:00-21:00 Tbilisi)",
    ]

    return est


# ---------------------------------------------------------------------------
# Core planning logic
# ---------------------------------------------------------------------------

def combine_estimates(a: ResourceEstimate, b: ResourceEstimate) -> ResourceEstimate:
    """Combine two resource estimates (for 'both' platform mode)."""
    return ResourceEstimate(
        requests_per_sec=a.requests_per_sec + b.requests_per_sec,
        db_connections=a.db_connections + b.db_connections,
        websocket_conns=a.websocket_conns + b.websocket_conns,
        storage_growth_gb_per_month=a.storage_growth_gb_per_month + b.storage_growth_gb_per_month,
        notes=a.notes + b.notes,
    )


def apply_peak_multiplier(est: ResourceEstimate, multiplier: float) -> ResourceEstimate:
    """Apply peak traffic multiplier to an estimate."""
    return ResourceEstimate(
        requests_per_sec=est.requests_per_sec * multiplier,
        db_connections=int(est.db_connections * min(multiplier, 2.0)),  # Connections don't scale linearly
        websocket_conns=int(est.websocket_conns * min(multiplier, 2.0)),
        storage_growth_gb_per_month=est.storage_growth_gb_per_month,  # Storage unaffected by peak
        notes=est.notes,
    )


def find_tier(peak: ResourceEstimate) -> dict:
    """Find the minimum tier that satisfies peak resource requirements."""
    for tier in TIERS:
        if (
            peak.requests_per_sec <= tier["requests_per_sec"]
            and peak.db_connections <= tier["db_connections"]
            and peak.websocket_conns <= tier["websocket_conns"]
        ):
            return tier
    # If nothing fits, return Enterprise with a note
    return TIERS[-1]


def find_bottlenecks(peak: ResourceEstimate, tier: dict) -> list:
    """Identify which resources hit the tier limit first."""
    ratios = [
        ("requests_per_sec", peak.requests_per_sec / max(tier["requests_per_sec"], 1)),
        ("db_connections", peak.db_connections / max(tier["db_connections"], 1)),
        ("websocket_conns", peak.websocket_conns / max(tier["websocket_conns"], 1)),
    ]
    ratios.sort(key=lambda x: x[1], reverse=True)
    bottlenecks = []
    for resource, ratio in ratios:
        label = resource.replace("_", " ").title()
        pct = ratio * 100
        bottlenecks.append({
            "resource": label,
            "utilization_pct": round(pct, 1),
            "status": "OVER" if pct > 100 else ("WARNING" if pct > 80 else "OK"),
        })
    return bottlenecks


def find_warnings(peak: ResourceEstimate, tier: dict) -> list:
    """Flag resources above 80% of tier capacity."""
    warnings = []
    checks = [
        ("Requests/sec", peak.requests_per_sec, tier["requests_per_sec"]),
        ("DB connections", peak.db_connections, tier["db_connections"]),
        ("WebSocket connections", peak.websocket_conns, tier["websocket_conns"]),
    ]
    for name, used, limit in checks:
        ratio = used / max(limit, 1)
        if ratio > WARNING_THRESHOLD:
            warnings.append(
                f"{name}: {used:.0f} / {limit} ({ratio * 100:.0f}%) — "
                f"{'EXCEEDS CAPACITY' if ratio > 1.0 else 'approaching limit, plan upgrade'}"
            )
    return warnings


def platform_notes(platform: str) -> list:
    """Return platform-specific advisory notes."""
    notes = []
    if platform in ("lotify", "both"):
        notes.extend([
            "Lotify: Implement bid debouncing / queue for auction endings to mitigate thundering herd",
            "Lotify: Use Supabase Realtime channel-per-auction with fan-out limits",
            "Lotify: Consider Redis cache for hot auction data (current price, bid count)",
        ])
    if platform in ("courio", "both"):
        notes.extend([
            "Courio: Batch GPS writes (buffer 2-3 updates, flush together) to reduce DB pressure",
            "Courio: Use PostGIS spatial indexes and partition location_history by date",
            "Courio: Implement push notification queue to smooth delivery-hour bursts",
        ])
    if platform == "both":
        notes.extend([
            "Shared: Both platforms share Supabase Auth — account for combined token refresh load",
            "Shared: TBC Pay webhook processing peaks when auction endings coincide with delivery rush",
            "Shared: Courio->Lotify webhooks use dead letter queue; monitor DLQ depth at scale",
        ])
    return notes


def plan(concurrent_users: int, platform: str = "both", peak_multiplier: float = 3.0) -> PlanResult:
    """Run the full capacity planning calculation."""
    result = PlanResult(
        concurrent_users=concurrent_users,
        peak_multiplier=peak_multiplier,
        platform=platform,
    )

    # Calculate base load
    if platform == "lotify":
        base_est = calc_lotify_load(concurrent_users)
    elif platform == "courio":
        base_est = calc_courio_load(concurrent_users)
    else:
        lotify_est = calc_lotify_load(concurrent_users)
        courio_est = calc_courio_load(concurrent_users)
        base_est = combine_estimates(lotify_est, courio_est)

    # Apply peak multiplier
    peak_est = apply_peak_multiplier(base_est, peak_multiplier)

    result.base_load = {
        "requests_per_sec": round(base_est.requests_per_sec, 1),
        "db_connections": base_est.db_connections,
        "websocket_conns": base_est.websocket_conns,
        "storage_growth_gb_per_month": round(base_est.storage_growth_gb_per_month, 2),
    }
    result.peak_load = {
        "requests_per_sec": round(peak_est.requests_per_sec, 1),
        "db_connections": peak_est.db_connections,
        "websocket_conns": peak_est.websocket_conns,
        "storage_growth_gb_per_month": round(peak_est.storage_growth_gb_per_month, 2),
    }

    # Find tier and bottlenecks
    tier = find_tier(peak_est)
    result.recommended_tier = {
        "name": tier["name"],
        "server": tier["server"],
        "monthly_cost_gel": tier["monthly_cost_gel"],
    }
    result.monthly_cost_gel = tier["monthly_cost_gel"]
    result.bottlenecks = find_bottlenecks(peak_est, tier)
    result.warnings = find_warnings(peak_est, tier)
    result.platform_notes = platform_notes(platform)

    return result


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_text(result: PlanResult) -> str:
    """Format the plan result as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("  PRIXIO CAPACITY PLAN")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"  Concurrent Users:  {result.concurrent_users:,}")
    lines.append(f"  Platform:          {result.platform}")
    lines.append(f"  Peak Multiplier:   {result.peak_multiplier}x")
    lines.append("")

    lines.append("-" * 70)
    lines.append("  RESOURCE ESTIMATES")
    lines.append("-" * 70)
    lines.append(f"  {'Metric':<35} {'Base':>12} {'Peak ({0}x)':>12}".format(result.peak_multiplier))
    lines.append(f"  {'─' * 35} {'─' * 12} {'─' * 12}")
    for key in ["requests_per_sec", "db_connections", "websocket_conns", "storage_growth_gb_per_month"]:
        label = key.replace("_", " ").title()
        base_val = result.base_load[key]
        peak_val = result.peak_load[key]
        if isinstance(base_val, float):
            lines.append(f"  {label:<35} {base_val:>12.1f} {peak_val:>12.1f}")
        else:
            lines.append(f"  {label:<35} {base_val:>12,} {peak_val:>12,}")
    lines.append("")

    lines.append("-" * 70)
    lines.append("  RECOMMENDED TIER")
    lines.append("-" * 70)
    lines.append(f"  Tier:    {result.recommended_tier['name']}")
    lines.append(f"  Server:  {result.recommended_tier['server']}")
    lines.append(f"  Cost:    ~{result.monthly_cost_gel:,} GEL/month")
    lines.append("")

    lines.append("-" * 70)
    lines.append("  BOTTLENECK ANALYSIS")
    lines.append("-" * 70)
    for b in result.bottlenecks:
        marker = "!!" if b["status"] == "OVER" else ("**" if b["status"] == "WARNING" else "  ")
        lines.append(f"  {marker} {b['resource']:<30} {b['utilization_pct']:>6.1f}%  [{b['status']}]")
    lines.append("")

    if result.warnings:
        lines.append("-" * 70)
        lines.append("  WARNINGS")
        lines.append("-" * 70)
        for w in result.warnings:
            lines.append(f"  >> {w}")
        lines.append("")

    lines.append("-" * 70)
    lines.append("  PLATFORM-SPECIFIC NOTES")
    lines.append("-" * 70)
    for note in result.platform_notes:
        lines.append(f"  - {note}")
    lines.append("")

    lines.append("=" * 70)
    return "\n".join(lines)


def format_json(result: PlanResult) -> str:
    """Format the plan result as JSON."""
    return json.dumps(asdict(result), indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Prixio capacity planning calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Presets:
  early        100 concurrent users  (soft launch)
  growing      500 concurrent users  (traction)
  established  2,000 concurrent users (product-market fit)
  scale        10,000 concurrent users (scaling phase)

Examples:
  %(prog)s --preset early
  %(prog)s --concurrent-users 750 --platform lotify --output json
  %(prog)s --preset scale --platform both
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--concurrent-users", type=int, metavar="N",
        help="Target number of concurrent users",
    )
    group.add_argument(
        "--preset", choices=["early", "growing", "established", "scale"],
        help="Use a predefined traffic preset",
    )

    parser.add_argument(
        "--platform", choices=["lotify", "courio", "both"], default="both",
        help="Platform to plan for (default: both)",
    )
    parser.add_argument(
        "--peak-multiplier", type=float, default=3.0, metavar="N",
        help="Peak traffic multiplier (default: 3.0)",
    )
    parser.add_argument(
        "--output", choices=["json", "text"], default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    # Resolve concurrent users
    concurrent_users = args.concurrent_users if args.concurrent_users else PRESETS[args.preset]

    if concurrent_users < 1:
        print("Error: concurrent users must be at least 1", file=sys.stderr)
        sys.exit(1)

    # Run planning
    result = plan(
        concurrent_users=concurrent_users,
        platform=args.platform,
        peak_multiplier=args.peak_multiplier,
    )

    # Output
    if args.output == "json":
        print(format_json(result))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
