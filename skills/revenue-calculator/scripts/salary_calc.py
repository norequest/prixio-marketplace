#!/usr/bin/env python3
"""Georgian salary tax calculator for Prixio LLC."""
import argparse

def calculate_salary(gross: float) -> dict:
    income_tax     = round(gross * 0.20, 2)
    emp_pension    = round(gross * 0.02, 2)
    empr_pension   = round(gross * 0.02, 2)
    state_pension  = round(gross * 0.02, 2)
    net_employee   = round(gross - income_tax - emp_pension, 2)
    total_empr_cost = round(gross + empr_pension, 2)
    rs_ge_payment  = round(income_tax + emp_pension + empr_pension, 2)

    return {
        "gross_salary": gross,
        "income_tax_withheld_20pct": income_tax,
        "employee_pension_2pct": emp_pension,
        "employer_pension_2pct": empr_pension,
        "state_pension_2pct": state_pension,
        "net_to_employee": net_employee,
        "total_employer_cost": total_empr_cost,
        "payment_to_rs_ge_by_15th": rs_ge_payment,
    }

def main():
    parser = argparse.ArgumentParser(description="Georgian salary calculator")
    parser.add_argument("--gross", type=float, required=True, help="Gross salary in GEL")
    args = parser.parse_args()

    r = calculate_salary(args.gross)

    print(f"\n{'='*45}")
    print(f"  SALARY CALCULATION — Prixio LLC")
    print(f"{'='*45}")
    print(f"  Gross salary:             {r['gross_salary']:>10.2f} ₾")
    print(f"  ─────────────────────────────────────────")
    print(f"  Income tax (20%):        -{r['income_tax_withheld_20pct']:>10.2f} ₾")
    print(f"  Employee pension (2%):   -{r['employee_pension_2pct']:>10.2f} ₾")
    print(f"  ─────────────────────────────────────────")
    print(f"  NET to employee:          {r['net_to_employee']:>10.2f} ₾")
    print(f"\n  Employer pension (2%):   +{r['employer_pension_2pct']:>10.2f} ₾  (extra cost)")
    print(f"  Total employer cost:      {r['total_employer_cost']:>10.2f} ₾")
    print(f"\n  ── Pay to rs.ge by 15th ──────────────────")
    print(f"  Income tax + pensions:    {r['payment_to_rs_ge_by_15th']:>10.2f} ₾")
    print(f"  (State adds {r['state_pension_2pct']:.2f} ₾ pension match automatically)")
    print(f"{'='*45}\n")

if __name__ == "__main__":
    main()
