---
name: revenue-calculator
description: >
  Calculates Georgian taxes, fees, and net amounts for Prixio LLC. Use this
  skill whenever users need to calculate: salary net pay, withholding tax,
  pension contributions, dividend tax, VAT amounts, Lotify commission splits,
  Courio platform fee splits, or any Georgian tax calculation. Also triggers
  for: "how much tax", "calculate", "net salary", "gross to net", "commission
  split", "how much do I pay", "გამოთვალე", "რამდენი გადასახადი".
allowed-tools: Bash, Read
---

# Revenue Calculator

> **Sources**: matsne.gov.ge, infohub.rs.ge, rs.ge
> **Last updated**: March 2026

I perform all tax and fee calculations for Prixio LLC. Run scripts for
deterministic results — never estimate these by hand.

## Available Calculations

### 1. Salary Calculator
Run: `python3 {baseDir}/scripts/salary_calc.py --gross <amount> [--regime <regime>] [--annual-salary <amount>]`

Regimes: `standard` (20% PIT), `ic` (5% PIT), `startup_1_3` (0% PIT), `startup_4_6` (5%), `startup_7_10` (10%)

Calculates: income tax withheld, employee pension, employer pension,
state pension (with caps), employee net pay, total employer cost.

### 2. Dividend Calculator
Run: `python3 {baseDir}/scripts/dividend_calc.py --amount <amount> [--regime <regime>]`

Regimes: `standard` (15% CIT + 5% WHT), `ic_resident` (5% + 5%), `ic_nonresident` (5% + 0%), `vzp_export` (0% + 5%), `bank_2023` (20% + 0%)

Calculates: corporate profit tax, dividend withholding, gross-up,
founder net receipt, total tax burden.

### 3. Lotify Commission Split
Run: `python3 {baseDir}/scripts/lotify_calc.py --sale <amount> --rate <pct> [--vat]`

Calculates: commission revenue, seller payout, VAT on commission (if --vat),
TBC Pay fee estimate, net commission.

### 4. Courio Fee Split
Run: `python3 {baseDir}/scripts/courio_calc.py --delivery <amount> [--vat] [--instant]`

Calculates: platform fee (15%), courier payout, instant payout fee,
VAT on revenue, net revenue.

### 5. VAT Threshold Tracker
Run: `python3 {baseDir}/scripts/vat_tracker.py --monthly <amounts_csv>`

Calculates: rolling 12-month turnover, months until 100,000 GEL threshold,
status, non-registration penalty warning (5,000 GEL).

### 6. Tax Rates & Deadline Check
Run: `python3 {baseDir}/../georgian-tax-knowledge/scripts/fetch_live_data.py [--query rates|period|all]`

Returns: current reporting period, next deadline, all 2025-2026 tax rates as JSON.

## Quick Reference Formulas

```
SALARY (gross G, standard):
  Income tax     = G × 0.20
  Employee pension = G × 0.02
  Employer pension = G × 0.02  (extra cost)
  Net to employee  = G × 0.78
  Total employer cost = G × 1.02

SALARY under IC Status (gross G):
  Income tax     = G × 0.05  (reduced from 20%)
  Employee pension = G × 0.02
  Employer pension = G × 0.02
  Net to employee  = G × 0.93
  Total employer cost = G × 1.02

SALARY under GITA Startup Years 1-3 (gross G, max 10,000/month):
  Income tax     = 0  (exempt)
  Employee pension = G × 0.02
  Employer pension = G × 0.02
  Net to employee  = G × 0.98
  Total employer cost = G × 1.02

DIVIDEND (amount D, standard):
  Corporate profit tax = D × 0.15  (company pays)
  Dividend withholding = D × 0.05  (deducted from founder)
  Net to founder = D × 0.95  (after WHT)
  Company also pays CIT = D × 0.15 (separate)
  Total tax burden = D × 0.20  (CIT + WHT combined)
  Gross-up tax = D ÷ 0.85 × 0.15  (for tax return)

DIVIDEND under IC Status (amount D, non-resident shareholder):
  Corporate profit tax = D × 0.05
  Dividend withholding = 0
  Net to founder = D × 0.95 (after CIT only; WHT = 0)

DIVIDEND under VZP (from export income, amount D):
  Corporate profit tax = 0
  Dividend withholding = D × 0.05
  Net to founder = D × 0.95

LOTIFY COMMISSION (sale S, rate R%):
  Commission = S × (R/100)
  Seller payout = S - Commission
  VAT on commission = Commission × 0.18  (if VAT-registered)
  TBC Pay fee ≈ Commission × 0.015  (estimate ~1.5%)

COURIO (delivery price P):
  Platform fee = P × 0.15  (min 4 GEL delivery → 0.60 GEL fee)
  Courier payout = P × 0.85
  Instant payout fee = 0.50 GEL additional revenue

REVERSE-CHARGE VAT (foreign service cost C in GEL):
  VAT payable = C × 0.18
  If VAT-registered: input VAT credit = C × 0.18 → net = 0
  If NOT VAT-registered: net cost = C × 1.18

PENSION STATE CONTRIBUTION (annual salary A):
  If A ≤ 24,000 GEL: state = 2% of monthly gross
  If 24,000 < A ≤ 60,000: state = 1% of monthly gross
  If A > 60,000: state = 0%

PENALTIES:
  Late declaration: 200 GEL first time, 400 GEL repeat (same year)
  Late payment: 0.05% per day (~18.25% per annum)
  VAT non-registration: 5,000 GEL + retroactive VAT
  Tax understatement: 50% of understated amount
  Tax evasion: 100% + criminal liability
```
