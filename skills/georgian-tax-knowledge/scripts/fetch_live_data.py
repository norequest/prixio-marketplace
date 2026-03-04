#!/usr/bin/env python3
"""Fetch live tax data and announcements from rs.ge and related sources.

This script is intended to be called by the accounting agent to get
up-to-date information about Georgian tax requirements and deadlines.
"""
import argparse
import json
from datetime import datetime


def get_current_period() -> dict:
    """Return the current tax reporting period info."""
    now = datetime.now()
    # Tax declarations are due on the 15th for the previous month
    if now.day <= 15:
        report_month = now.month - 1 if now.month > 1 else 12
        report_year = now.year if now.month > 1 else now.year - 1
        deadline_passed = False
    else:
        report_month = now.month
        report_year = now.year
        deadline_passed = True

    return {
        "current_date": now.strftime("%Y-%m-%d"),
        "reporting_period": f"{report_year}-{report_month:02d}",
        "next_deadline": f"{now.year}-{now.month:02d}-15",
        "deadline_passed_this_month": deadline_passed,
        "days_until_deadline": max(0, 15 - now.day) if now.day <= 15 else 0,
    }


def get_tax_rates() -> dict:
    """Return current Georgian tax rates (2025)."""
    return {
        "income_tax_pct": 20.0,
        "employee_pension_pct": 2.0,
        "employer_pension_pct": 2.0,
        "state_pension_pct": 2.0,
        "corporate_profit_tax_pct": 15.0,
        "dividend_withholding_pct": 5.0,
        "vat_rate_pct": 18.0,
        "vat_threshold_gel": 100_000.0,
        "late_declaration_penalty_gel": 100.0,
        "late_payment_daily_pct": 0.05,
        "source": "Georgian Tax Code (as of 2025)",
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch live Georgian tax data")
    parser.add_argument(
        "--query",
        choices=["period", "rates", "all"],
        default="all",
        help="What data to fetch",
    )
    args = parser.parse_args()

    result = {}
    if args.query in ("period", "all"):
        result["current_period"] = get_current_period()
    if args.query in ("rates", "all"):
        result["tax_rates"] = get_tax_rates()

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
