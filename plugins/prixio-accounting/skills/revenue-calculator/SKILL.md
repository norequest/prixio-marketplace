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

I perform all tax and fee calculations for Prixio LLC. Run scripts for
deterministic results — never estimate these by hand.

## Available Calculations

### 1. Salary Calculator
Run: `python3 {baseDir}/scripts/salary_calc.py --gross <amount>`

Calculates: income tax withheld, employee pension, employer pension,
employee net pay, total employer cost.

### 2. Dividend Calculator
Run: `python3 {baseDir}/scripts/dividend_calc.py --amount <amount>`

Calculates: corporate profit tax (15%), dividend withholding (5%),
founder net receipt, total tax burden.

### 3. Lotify Commission Split
Run: `python3 {baseDir}/scripts/lotify_calc.py --sale <amount> --rate <pct>`

Calculates: commission revenue, seller payout, VAT on commission (if registered),
TBC Pay fee estimate.

### 4. Courio Fee Split
Run: `python3 {baseDir}/scripts/courio_calc.py --delivery <amount>`

Calculates: platform fee (15%), courier payout, surge-adjusted price,
minimum price check.

### 5. VAT Threshold Tracker
Run: `python3 {baseDir}/scripts/vat_tracker.py --monthly <amounts_csv>`

Calculates: rolling 12-month turnover, months until 100,000 GEL threshold,
recommended registration date.

## Quick Reference Formulas

```
SALARY (gross G):
  Income tax     = G × 0.20
  Employee pension = G × 0.02
  Employer pension = G × 0.02  (extra cost)
  Net to employee  = G × 0.78
  Total employer cost = G × 1.02

DIVIDEND (amount D):
  Corporate profit tax = D × 0.15  (company pays)
  Dividend withholding = D × 0.05  (deducted from founder)
  Net to founder = D × 0.80  (after both taxes on gross)
  Effective tax rate on gross = 20%

LOTIFY COMMISSION (sale S, rate R%):
  Commission = S × (R/100)
  Seller payout = S - Commission
  VAT on commission = Commission × 0.18  (if VAT-registered)
  TBC Pay fee ≈ Commission × 0.015  (estimate ~1.5%)

COURIO (delivery price P):
  Platform fee = P × 0.15  (min 4 GEL delivery → 0.60 GEL fee)
  Courier payout = P × 0.85
  Instant payout fee = 0.50 GEL additional revenue

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

DIVIDEND under IC Status (amount D, non-resident shareholder):
  Corporate profit tax = D × 0.05
  Dividend withholding = 0
  Net to founder = D × 0.95

DIVIDEND under VZP (from export income, amount D):
  Corporate profit tax = 0
  Dividend withholding = D × 0.05
  Net to founder = D × 0.95

REVERSE-CHARGE VAT (foreign service cost C in GEL):
  VAT payable = C × 0.18
  If VAT-registered: input VAT credit = C × 0.18 → net = 0
  If NOT VAT-registered: net cost = C × 1.18

PENSION STATE CONTRIBUTION (annual salary A):
  If A ≤ 24,000 GEL: state = 2% of monthly gross
  If 24,000 < A ≤ 60,000: state = 1% of monthly gross
  If A > 60,000: state = 0%
```
