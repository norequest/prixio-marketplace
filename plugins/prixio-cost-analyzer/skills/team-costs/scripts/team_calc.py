#!/usr/bin/env python3
"""Team and personnel cost calculator for Prixio LLC.

Calculates salaries with Georgian tax withholding, pension, and contractor costs.
Sources: Georgian Tax Code, infohub.rs.ge
Updated: March 2026
"""
import argparse
import json

REGIMES = {
    "standard": {"pit_rate": 0.20, "label": "Standard (20% PIT)"},
    "ic": {"pit_rate": 0.05, "label": "IC Status (5% PIT)"},
    "startup_1_3": {"pit_rate": 0.00, "label": "GITA Startup Yr 1-3 (0% PIT)"},
    "startup_4_6": {"pit_rate": 0.05, "label": "GITA Startup Yr 4-6 (5% PIT)"},
    "startup_7_10": {"pit_rate": 0.10, "label": "GITA Startup Yr 7-10 (10% PIT)"},
}

EMPLOYEE_PENSION_RATE = 0.02
EMPLOYER_PENSION_RATE = 0.02

PRESETS = {
    "solo": {
        "employees": [
            {"role": "Founder/CEO", "gross": 0, "count": 1},
        ],
        "accountant": 300,
        "lawyer": 200,
    },
    "small": {
        "employees": [
            {"role": "Founder/CEO", "gross": 2000, "count": 1},
            {"role": "Full-stack Developer", "gross": 3500, "count": 1},
            {"role": "Mobile Developer", "gross": 3000, "count": 1},
            {"role": "Customer Support", "gross": 1000, "count": 1},
        ],
        "accountant": 400,
        "lawyer": 300,
    },
    "medium": {
        "employees": [
            {"role": "Founder/CEO", "gross": 3000, "count": 1},
            {"role": "Full-stack Developer", "gross": 4000, "count": 2},
            {"role": "Mobile Developer", "gross": 3500, "count": 1},
            {"role": "Designer", "gross": 2500, "count": 1},
            {"role": "QA Engineer", "gross": 2000, "count": 1},
            {"role": "Marketing Manager", "gross": 2000, "count": 1},
            {"role": "Customer Support", "gross": 1200, "count": 2},
        ],
        "accountant": 600,
        "lawyer": 400,
    },
}


def calc_state_pension(monthly_gross: float, annual_salary: float) -> float:
    """State pension contribution based on annual salary brackets."""
    if annual_salary <= 24000:
        return round(monthly_gross * 0.02, 2)
    elif annual_salary <= 60000:
        return round(monthly_gross * 0.01, 2)
    else:
        return 0.0


def calc_employee(gross: float, regime: str, annual_salary: float = None) -> dict:
    if annual_salary is None:
        annual_salary = gross * 12

    pit_rate = REGIMES[regime]["pit_rate"]

    if regime == "startup_1_3" and gross > 10000:
        pit = round((gross - 10000) * 0.20 + 0, 2)
    else:
        pit = round(gross * pit_rate, 2)

    emp_pension = round(gross * EMPLOYEE_PENSION_RATE, 2)
    er_pension = round(gross * EMPLOYER_PENSION_RATE, 2)
    state_pension = calc_state_pension(gross, annual_salary)
    net_pay = round(gross - pit - emp_pension, 2)
    total_employer_cost = round(gross + er_pension, 2)

    return {
        "gross": gross,
        "pit": pit,
        "pit_rate_pct": pit_rate * 100,
        "employee_pension": emp_pension,
        "employer_pension": er_pension,
        "state_pension": state_pension,
        "net_pay": net_pay,
        "total_employer_cost": total_employer_cost,
    }


def calculate_team(employees: list, regime: str,
                   accountant: float = 0, lawyer: float = 0) -> dict:
    results = []
    total_gross = 0
    total_pit = 0
    total_emp_pension = 0
    total_er_pension = 0
    total_net = 0
    total_employer_cost = 0
    headcount = 0

    for emp in employees:
        role = emp.get("role", "Employee")
        gross = emp.get("gross", 0)
        count = emp.get("count", 1)

        if gross == 0:
            results.append({
                "role": role, "count": count, "gross": 0,
                "pit": 0, "employee_pension": 0, "employer_pension": 0,
                "net_pay": 0, "total_employer_cost": 0,
            })
            headcount += count
            continue

        calc = calc_employee(gross, regime)
        results.append({
            "role": role,
            "count": count,
            **calc,
        })
        total_gross += gross * count
        total_pit += calc["pit"] * count
        total_emp_pension += calc["employee_pension"] * count
        total_er_pension += calc["employer_pension"] * count
        total_net += calc["net_pay"] * count
        total_employer_cost += calc["total_employer_cost"] * count
        headcount += count

    contractor_total = round(accountant + lawyer, 2)
    grand_total = round(total_employer_cost + contractor_total, 2)

    return {
        "regime": regime,
        "regime_label": REGIMES[regime]["label"],
        "employees": results,
        "headcount": headcount,
        "total_gross": round(total_gross, 2),
        "total_pit": round(total_pit, 2),
        "total_employee_pension": round(total_emp_pension, 2),
        "total_employer_pension": round(total_er_pension, 2),
        "total_net_pay": round(total_net, 2),
        "total_employer_cost": round(total_employer_cost, 2),
        "accountant_monthly": accountant,
        "lawyer_monthly": lawyer,
        "contractor_total": contractor_total,
        "grand_total": grand_total,
    }


def main():
    parser = argparse.ArgumentParser(description="Prixio team cost calculator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preset", choices=["solo", "small", "medium"],
                       help="Use preset team profile")
    group.add_argument("--team-json", type=str,
                       help="JSON array of team members")
    parser.add_argument("--regime", choices=list(REGIMES.keys()),
                        default="standard", help="Tax regime")
    parser.add_argument("--accountant", type=float, default=0,
                        help="Monthly outsourced accountant cost (GEL)")
    parser.add_argument("--lawyer", type=float, default=0,
                        help="Monthly outsourced lawyer retainer (GEL)")
    args = parser.parse_args()

    if args.preset:
        preset = PRESETS[args.preset]
        employees = preset["employees"]
        accountant = preset["accountant"]
        lawyer = preset["lawyer"]
        preset_name = args.preset.upper()
    else:
        employees = json.loads(args.team_json)
        accountant = args.accountant
        lawyer = args.lawyer
        preset_name = "CUSTOM"

    r = calculate_team(employees, args.regime, accountant, lawyer)

    print(f"\n{'='*70}")
    print(f"  TEAM COSTS -- Prixio LLC ({preset_name})")
    print(f"  Tax regime: {r['regime_label']}")
    print(f"  Headcount: {r['headcount']} employee(s)")
    print(f"{'='*70}")

    print(f"\n  {'Role':<25} {'Cnt':>3} {'Gross':>8} {'PIT':>8} {'EePen':>7}"
          f" {'Net':>8} {'ErCost':>9}")
    print(f"  {'─'*64}")

    for emp in r["employees"]:
        cnt = emp["count"]
        if emp["gross"] == 0:
            print(f"  {emp['role']:<25} {cnt:>3}      (no salary)")
            continue
        print(f"  {emp['role']:<25} {cnt:>3} {emp['gross']:>8.0f}"
              f" {emp['pit']:>8.0f} {emp['employee_pension']:>7.0f}"
              f" {emp['net_pay']:>8.0f} {emp['total_employer_cost']:>9.0f}")
        if cnt > 1:
            print(f"  {'  (x' + str(cnt) + ' total)':<25}     "
                  f"{emp['gross']*cnt:>8.0f}"
                  f" {emp['pit']*cnt:>8.0f} {emp['employee_pension']*cnt:>7.0f}"
                  f" {emp['net_pay']*cnt:>8.0f} {emp['total_employer_cost']*cnt:>9.0f}")

    print(f"\n  {'─'*64}")
    print(f"  {'EMPLOYEE TOTALS':<25}     {r['total_gross']:>8.0f}"
          f" {r['total_pit']:>8.0f} {r['total_employee_pension']:>7.0f}"
          f" {r['total_net_pay']:>8.0f} {r['total_employer_cost']:>9.0f}")

    print(f"\n  CONTRACTORS (no tax withholding):")
    if accountant > 0:
        print(f"    Outsourced Accountant:              {accountant:>10.0f} GEL/month")
    if lawyer > 0:
        print(f"    Outsourced Lawyer:                  {lawyer:>10.0f} GEL/month")
    print(f"    Contractor subtotal:                {r['contractor_total']:>10.0f} GEL/month")

    print(f"\n  {'─'*64}")
    print(f"  GRAND TOTAL (employer cost + contractors): {r['grand_total']:>10.0f} GEL/month")
    print(f"  Annual projection:                        {r['grand_total'] * 12:>10.0f} GEL/year")

    print(f"\n  COST BREAKDOWN:")
    if r["grand_total"] > 0:
        emp_pct = r["total_employer_cost"] / r["grand_total"] * 100
        con_pct = r["contractor_total"] / r["grand_total"] * 100
        print(f"    Salaries + tax:  {emp_pct:>5.1f}%")
        print(f"    Contractors:     {con_pct:>5.1f}%")

    print(f"\n  NOTE: Employer pension ({r['total_employer_pension']:.0f} GEL) is")
    print(f"  an additional cost above gross salary.")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
