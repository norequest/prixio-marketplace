#!/usr/bin/env python3
"""VAT registration threshold tracker for Prixio LLC."""
import argparse

VAT_THRESHOLD = 100_000.0

def track_vat(monthly_revenues: list[float]) -> dict:
    total = sum(monthly_revenues)
    months_count = len(monthly_revenues)
    remaining = max(0.0, VAT_THRESHOLD - total)
    pct_used = round((total / VAT_THRESHOLD) * 100, 1)
    avg_monthly = round(total / months_count, 2) if months_count else 0

    months_to_threshold = None
    if avg_monthly > 0 and remaining > 0:
        months_to_threshold = round(remaining / avg_monthly, 1)

    status = "SAFE"
    if total >= VAT_THRESHOLD:
        status = "⚠️  THRESHOLD EXCEEDED — REGISTER FOR VAT NOW"
    elif pct_used >= 80:
        status = "⚠️  WARNING — approaching threshold (>80%)"
    elif pct_used >= 60:
        status = "🔶 CAUTION — past 60% of threshold"

    return {
        "months_tracked": months_count,
        "total_revenue_gel": round(total, 2),
        "vat_threshold_gel": VAT_THRESHOLD,
        "remaining_before_threshold": round(remaining, 2),
        "threshold_used_pct": pct_used,
        "avg_monthly_revenue": avg_monthly,
        "estimated_months_to_threshold": months_to_threshold,
        "status": status,
    }

def main():
    parser = argparse.ArgumentParser(description="VAT threshold tracker")
    parser.add_argument("--monthly", required=True,
                        help="Comma-separated monthly revenues e.g. 5000,7000,8500")
    args = parser.parse_args()

    revenues = [float(x.strip()) for x in args.monthly.split(",")]
    r = track_vat(revenues)

    print(f"\n{'='*45}")
    print(f"  VAT THRESHOLD TRACKER — Prixio LLC")
    print(f"{'='*45}")
    print(f"  Months tracked:           {r['months_tracked']:>10}")
    print(f"  Total revenue (12m):      {r['total_revenue_gel']:>10.2f} ₾")
    print(f"  VAT threshold:            {r['vat_threshold_gel']:>10,.0f} ₾")
    print(f"  Used:                     {r['threshold_used_pct']:>9.1f}%")
    print(f"  Remaining:                {r['remaining_before_threshold']:>10.2f} ₾")
    print(f"  Avg monthly revenue:      {r['avg_monthly_revenue']:>10.2f} ₾")
    if r['estimated_months_to_threshold']:
        print(f"  Est. months to threshold: {r['estimated_months_to_threshold']:>10.1f}")
    print(f"\n  STATUS: {r['status']}")
    print(f"{'='*45}\n")

if __name__ == "__main__":
    main()
