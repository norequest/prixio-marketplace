---
name: declaration-assistant
description: >
  Guides through Georgian tax declarations on rs.ge step by step. Use this
  skill whenever users ask HOW to file a declaration, what forms to use,
  how to fill in specific fields, what zero declarations are, how to mark
  declarations on the information card, or need help with the rs.ge portal.
  Also triggers for: "how to declare", "how to file", "საინფორმაციო ბარათი",
  "zero declaration", "ნულოვანი დეკლარაცია", "form III", "withholding return",
  "how to submit", "rs.ge portal help".
allowed-tools: WebSearch, WebFetch, Read
---

# Declaration Assistant

I guide you through Georgian tax declarations on rs.ge step by step.

## The rs.ge Information Card (საინფორმაციო ბარათი)

This is the most important setup step. Done ONCE after company registration.

### How it works:
1. Log into rs.ge with your company credentials
2. Go to your taxpayer profile → "საინფორმაციო ბარათი" (Information Card)
3. Mark ONLY the declarations you will file regularly
4. **Critical rule**: Once marked, you MUST file it every month (even zero)

### For Prixio at launch (no employees, no VAT):
```
Mark ONLY if applicable:
☐ Withholding tax (III-07) — mark when you hire first employee
☐ Pension (III-09)          — mark when you hire first employee  
☐ VAT (III-10)              — mark when VAT-registered
☐ Corporate profit (III-04) — mark when distributing profits

DO NOT mark anything until it applies → avoids penalty obligations
```

## Filing a Zero Declaration

When you have a marked declaration but NO activity that month:

1. Log into rs.ge
2. Navigate to Declarations → select the declaration type
3. Fill in all fields as 0
4. Submit before the 15th
5. No payment needed (zero tax = zero payment)

**Never skip a zero** — 100 GEL penalty per skipped month.

## Withholding Tax Declaration (Form III-07)

Filed monthly when you have employees. Due: 15th of following month.

```
Fields to complete:
- Reporting period: [MM/YYYY]
- Employee count: [number]
- Total gross salaries paid: [GEL amount]
- Withheld income tax (20%): [gross × 0.20]
- Payment: transfer this amount to Revenue Service
```

### Example:
```
Employee salary: 2,000 GEL gross
Income tax withheld: 2,000 × 20% = 400 GEL
Employee receives: 2,000 - 400 = 1,600 GEL net
Prixio pays to rs.ge by 15th: 400 GEL
```

## Pension Contribution Declaration (Form III-09)

Filed monthly alongside withholding tax. Due: 15th of following month.

```
Fields:
- Gross salary: [amount]
- Employee pension (2%): [gross × 0.02]
- Employer pension (2%): [gross × 0.02]
- Total pension: [gross × 0.04] → paid to rs.ge
```

### Example:
```
Gross salary: 2,000 GEL
Employee pension: 2,000 × 2% = 40 GEL (deducted from salary)
Employer pension: 2,000 × 2% = 40 GEL (additional cost for Prixio)
State adds: 40 GEL (automatic)
Total pension payment by Prixio to rs.ge: 80 GEL (employee 40 + employer 40)
Employee net: 2,000 - 400 (tax) - 40 (pension) = 1,560 GEL
```

## Corporate Profit Tax Declaration (Form III-04)

Filed ONLY in months when profit is distributed. Due: 15th of following month.

```
When founder takes dividends:
- Dividend amount: [GEL]
- Corporate profit tax (15%): [amount × 0.15]  → Prixio pays this
- Dividend withholding (5%): [amount × 0.05]   → deducted from founder
- Founder receives net: [amount × 0.80]

Example — 10,000 GEL dividend:
  Corporate profit tax: 1,500 GEL (paid by company)
  Dividend withholding: 500 GEL (deducted from founder's 10,000)
  Founder receives: 9,500 GEL
  Total tax cost: 2,000 GEL (20% effective rate)
```

## VAT Declaration (Form III-10)

Filed monthly once VAT-registered. Due: 15th of following month.

```
Output VAT (VAT you charged customers):
  Lotify commissions × 18% = output VAT

Input VAT (VAT you paid on purchases):
  Software, equipment, services bought with VAT

VAT payable = Output VAT - Input VAT

If input VAT > output VAT → VAT credit (can offset future months)
```

## Useful rs.ge Navigation

For live instructions, WebSearch: "rs.ge [declaration name] შევსება"

Key pages on rs.ge:
- Declarations: eservices.rs.ge → Declarations
- Information card: your profile → Information Card (საინფორმაციო ბარათი)
- Payment: eservices.rs.ge → Payments

Load [tax-calendar reference](../georgian-tax-knowledge/references/tax-calendar.md)
for form numbers and deadlines.
