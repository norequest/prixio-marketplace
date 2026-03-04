---
name: declaration-assistant
description: >
  Guides through Georgian tax declarations on rs.ge step by step. Use this
  skill whenever users ask HOW to file a declaration, what forms to use,
  how to fill in specific fields, what zero declarations are, how to mark
  declarations on the information card, or need help with the rs.ge portal.
  Also triggers for: "how to declare", "how to file", "საინფორმაციო ბარათი",
  "zero declaration", "ნულოვანი დეკლარაცია", "form III", "withholding return",
  "how to submit", "rs.ge portal help", "reverse-charge VAT", "უკუდაბეგვრა".
allowed-tools: WebSearch, WebFetch, Read
---

# Declaration Assistant

> **Sources**: infohub.rs.ge, rs.ge, matsne.gov.ge
> **Last updated**: March 2026

I guide you through Georgian tax declarations on rs.ge step by step.

## The rs.ge Information Card (საინფორმაციო ბარათი)

This is the most important setup step. Done ONCE after company registration.

### How it works:
1. Log into rs.ge with your company credentials
2. Go to your taxpayer profile → "საინფორმაციო ბარათი" (Information Card)
3. Mark ONLY the declarations you will file regularly
4. **Critical rule**: Once marked, you MUST file it every month (even zero)
5. Penalty for not filing a marked declaration: 200 GEL (first), 400 GEL (repeat in same year)

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

**Never skip a zero** — 200 GEL penalty first time, 400 GEL repeat.

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
Employee receives: 2,000 - 400 - 40 (pension) = 1,560 GEL net
Prixio pays to rs.ge by 15th: 400 GEL (income tax)
```

### If International Company Status (IC):
```
Employee salary: 2,000 GEL gross
Income tax withheld: 2,000 × 5% = 100 GEL (reduced IC rate)
Employee receives: 2,000 - 100 - 40 (pension) = 1,860 GEL net
Prixio pays to rs.ge by 15th: 100 GEL (income tax)
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
State adds: 40 GEL (automatic — for annual salary ≤24,000 GEL)
Total pension payment by Prixio to rs.ge: 80 GEL (employee 40 + employer 40)
Employee net: 2,000 - 400 (tax) - 40 (pension) = 1,560 GEL
Total employer cost: 2,000 + 40 (employer pension) = 2,040 GEL
```

### State pension contribution caps:
- Annual salary ≤24,000 GEL: State adds 2%
- Annual salary 24,000–60,000 GEL: State adds 1%
- Annual salary >60,000 GEL: State adds 0%

Pension is mandatory for Georgian citizens and permanent residents.

## Corporate Profit Tax Declaration (Form III-04)

Filed ONLY in months when profit is distributed. Due: 15th of following month.

**2026 update**: Form now requires information about controlled international transactions.

```
When founder takes dividends:
- Dividend amount: [GEL]
- Corporate profit tax (15%): [amount × 0.15]  → Prixio pays this
- Dividend withholding (5%): [amount × 0.05]   → deducted from founder
- Founder receives net: [amount × 0.80]

CIT credit mechanism: The 15% CIT paid can be credited against the 5%
dividend withholding. Total effective tax = 15% (not 15% + 5%).

Example — 10,000 GEL dividend:
  Corporate profit tax: 1,500 GEL (paid by company)
  Dividend withholding: 500 GEL (deducted from founder's 10,000)
  Founder receives: 9,500 GEL
  Total tax cost: 2,000 GEL (20% effective rate)
  Gross-up: 10,000 ÷ 0.85 × 0.15 = 1,764.71 GEL (alternative calculation)
```

### Special cases:
```
If International Company Status: CIT = 5%, dividend WHT = 0% (non-resident)
If VZP and export income: CIT = 0%, dividend WHT = 5%
If dividend from banks/microfinance (2026+): 0% tax, excluded from income
Intra-Georgian dividends between legal entities: EXEMPT from CIT
```

### Non-business expenses treated as distributions:
```
These trigger 15% CIT even without a formal dividend:
- Undocumented expenses
- Personal loans to founders
- Interest above 24% annual rate
- Representative expenses exceeding 1% of prior-year revenue
- Free goods/services to related parties
```

## VAT Declaration (Form III-10)

Filed monthly once VAT-registered. Due: 15th of following month.

```
Output VAT (VAT you charged customers):
  Lotify commissions × 18% = output VAT
  Courio platform fees × 18% = output VAT

Input VAT (VAT you paid on purchases):
  Software, equipment, services bought with VAT invoice

VAT payable = Output VAT - Input VAT

If input VAT > output VAT → VAT credit (can offset future months)
Refund mechanism: Input VAT reclaimed within 1–6 months
```

### Zero-rated supplies (0% VAT with input VAT deduction right):
- Exports of goods
- International transport services
- IT services to non-Georgian clients
- Tourism services (certain)

### VAT-exempt supplies (no VAT, no input deduction):
- Financial services
- Insurance
- Medical services
- Educational services

### 2026 new exemptions with input VAT deduction:
- Real estate/construction (until 2029, requires building permit)
- Investment gold (supply and import)

## Reverse-Charge VAT Declaration

Filed monthly by ALL businesses purchasing services from abroad — even non-VAT-registered.

```
When you pay for foreign services (SaaS, cloud, contractors):
  Service cost: 100 USD (converted to GEL at payment date rate)
  Reverse-charge VAT: GEL amount × 18%

If VAT-registered:
  Declare 18% → simultaneously claim input VAT → net effect = 0%

If NOT VAT-registered:
  Declare 18% → pay 18% → cannot reclaim
  Consider voluntary VAT registration if significant foreign purchases
```

## Useful rs.ge Navigation

For live instructions, WebSearch: "rs.ge [declaration name] შევსება"

Key pages on rs.ge:
- Declarations: eservices.rs.ge → Declarations
- Information card: your profile → Information Card (საინფორმაციო ბარათი)
- Payment: eservices.rs.ge → Payments
- IC Status application: rs.ge portal → submit enterprise data
- Tax calendar: rs.ge → tax calendar
- Legislation: rs.ge → Legislation tab
- Law news: rs.ge/LawNewsArchive

Load [tax-calendar reference](../georgian-tax-knowledge/references/tax-calendar.md)
for form numbers and deadlines.
