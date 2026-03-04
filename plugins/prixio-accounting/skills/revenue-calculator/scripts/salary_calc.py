#!/usr/bin/env python3
"""Georgian salary tax calculator for Prixio LLC.

Supports standard, International Company (IC), and GITA Innovative Startup regimes.
Sources: matsne.gov.ge Tax Code, infohub.rs.ge
Updated: March 2026
"""
import argparse

REGIMES = {
    "standard": {"pit_rate": 0.20, "label": "Standard (20% PIT)"},
    "ic": {"pit_rate": 0.05, "label": "International Company (5% PIT)"},
    "startup_1_3": {"pit_rate": 0.00, "label": "GITA Startup Years 1-3 (0% PIT, max 10,000/mo)"},
    "startup_4_6": {"pit_rate": 0.05, "label": "GITA Startup Years 4-6 (5% PIT)"},
    "startup_7_10": {"pit_rate": 0.10, "label": "GITA Startup Years 7-10 (10% PIT)"},
}

PENSION_EMPLOYEE = 0.02
PENSION_EMPLOYER = 0.02


def state_pension_rate(annual_salary: float) -> float:
    """State pension contribution rate based on annual salary caps."""
    if annual_salary <= 24_000:
        return 0.02
    elif annual_salary <= 60_000:
        return 0.01
    else:
        return 0.00


def calculate_salary(gross: float, regime: str = "standard",
                     annual_salary: float | None = None) -> dict:
    pit_rate = REGIMES[regime]["pit_rate"]
    income_tax = round(gross * pit_rate, 2)
    emp_pension = round(gross * PENSION_EMPLOYEE, 2)
    empr_pension = round(gross * PENSION_EMPLOYER, 2)

    # State pension depends on annual salary; default to gross*12 estimate
    if annual_salary is None:
        annual_salary = gross * 12
    state_rate = state_pension_rate(annual_salary)
    state_pension = round(gross * state_rate, 2)

    net_employee = round(gross - income_tax - emp_pension, 2)
    total_empr_cost = round(gross + empr_pension, 2)
    rs_ge_payment = round(income_tax + emp_pension + empr_pension, 2)

    return {
        "gross_salary": gross,
        "regime": REGIMES[regime]["label"],
        "pit_rate_pct": pit_rate * 100,
        "income_tax_withheld": income_tax,
        "employee_pension_2pct": emp_pension,
        "employer_pension_2pct": empr_pension,
        "state_pension": state_pension,
        "state_pension_rate_pct": state_rate * 100,
        "annual_salary_estimate": annual_salary,
        "net_to_employee": net_employee,
        "total_employer_cost": total_empr_cost,
        "payment_to_rs_ge_by_15th": rs_ge_payment,
    }


def main():
    parser = argparse.ArgumentParser(description="Georgian salary calculator")
    parser.add_argument("--gross", type=float, required=True, help="Gross monthly salary in GEL")
    parser.add_argument("--regime", choices=REGIMES.keys(), default="standard",
                        help="Tax regime (default: standard)")
    parser.add_argument("--annual-salary", type=float, default=None,
                        help="Annual salary for state pension cap (default: gross×12)")
    args = parser.parse_args()

    r = calculate_salary(args.gross, args.regime, args.annual_salary)

    print(f"\n{'='*50}")
    print(f"  SALARY CALCULATION — Prixio LLC")
    print(f"  Regime: {r['regime']}")
    print(f"{'='*50}")
    print(f"  Gross salary:              {r['gross_salary']:>10.2f} GEL")
    print(f"  ──────────────────────────────────────────────")
    print(f"  Income tax ({r['pit_rate_pct']:.0f}%):        -{r['income_tax_withheld']:>10.2f} GEL")
    print(f"  Employee pension (2%):    -{r['employee_pension_2pct']:>10.2f} GEL")
    print(f"  ──────────────────────────────────────────────")
    print(f"  NET to employee:           {r['net_to_employee']:>10.2f} GEL")
    print(f"\n  Employer pension (2%):    +{r['employer_pension_2pct']:>10.2f} GEL  (extra cost)")
    print(f"  Total employer cost:       {r['total_employer_cost']:>10.2f} GEL")
    print(f"\n  ── Pay to rs.ge by 15th ───────────────────────")
    print(f"  Income tax + pensions:     {r['payment_to_rs_ge_by_15th']:>10.2f} GEL")
    print(f"  Forms: III-07 + III-09")
    print(f"\n  ── State pension (automatic) ──────────────────")
    print(f"  Annual salary estimate:    {r['annual_salary_estimate']:>10,.0f} GEL")
    print(f"  State rate:                {r['state_pension_rate_pct']:>9.0f}%", end="")
    if r['state_pension_rate_pct'] < 2:
        print(f"  (capped: >24k=1%, >60k=0%)")
    else:
        print(f"  (full match, salary ≤24k/yr)")
    print(f"  State adds:                {r['state_pension']:>10.2f} GEL")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
