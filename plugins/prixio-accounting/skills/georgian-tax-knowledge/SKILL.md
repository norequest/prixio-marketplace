---
name: georgian-tax-knowledge
description: >
  Comprehensive knowledge of Georgian tax law for LLC companies. Use this skill
  whenever users ask about: Georgian tax rates, rs.ge obligations, Estonian
  profit tax model, VAT thresholds, pension contributions, income tax withholding,
  dividend tax, virtual zone status, GITA innovative startup status, SARAS
  financial reporting, monthly declarations, annual filings, or any Georgian
  Revenue Service (შემოსავლების სამსახური) requirement. Also triggers for:
  "საგადასახადო", "დღგ", "საპენსიო", "rs.ge", "ბრუნვა", "მოგება".
allowed-tools: WebSearch, WebFetch, Read
---

# Georgian Tax Knowledge Base

## Core Tax Rates (2025)

| Tax | Rate | Applies To |
|-----|------|------------|
| Corporate Profit Tax | 15% | Distributed profits ONLY (Estonian model) |
| Retained/reinvested profit | 0% | No tax until distributed |
| VAT (დღგ) | 18% | Turnover above 100,000 GEL/12 months |
| VAT on IT exports | 0% | Services to non-Georgian clients |
| Income Tax (სახელფასო) | 20% flat | Employee salaries — employer withholds |
| Pension — employee | 2% | Of gross salary |
| Pension — employer | 2% | Of gross salary (employer pays) |
| Pension — state | 2% | State match |
| Dividend withholding | 5% | Paid to individuals (resident or not) |
| Property tax | Up to 1% | Average annual book value of fixed assets |

## Monthly Filing Obligations (15th of every month)

Every LLC in Georgia must file monthly via rs.ge — **even zero declarations**.

### What to file by the 15th:

```
If you have employees:
  ✅ Withholding tax declaration (20% income tax)
  ✅ Pension contribution declaration (2% + 2%)
  ✅ Payment of withheld amounts

If VAT-registered:
  ✅ VAT declaration
  ✅ VAT payment

If profit distributed this month:
  ✅ Corporate profit tax declaration (15%)
  ✅ Dividend withholding (5%)

Always:
  ✅ Zero declaration if marked on information card but no activity
```

⚠️ **Critical**: If you mark a declaration type on your rs.ge information card,
you MUST file it every month — even zeros. Failure = 100 GEL penalty per month.

## Annual Obligations

| Deadline | Obligation |
|----------|------------|
| March 31 | Individual entrepreneur income tax declaration |
| April 1 | Annual NAPR registration update (legal requirement, not tax) |
| October 1 | SARAS financial report submission (for eligible entities) |

## VAT Registration

- **Mandatory threshold**: 100,000 GEL turnover in any rolling 12-month period
- **Voluntary**: Can register before threshold
- **IT services exported**: 0% VAT regardless of registration status
- **Domestic services**: 18% once registered

### Prixio VAT Logic
- Lotify commissions from Georgian sellers = domestic = 18% once registered
- Courio fees from Georgian senders = domestic = 18% once registered
- If expanding internationally: export portion = 0%

## SARAS Financial Reporting Categories

| Category | Revenue | Assets | Employees | Standard |
|----------|---------|--------|-----------|----------|
| I (Large) | >100M GEL | — | — | Full IFRS |
| II (Medium) | ≤100M GEL | — | ≤250 | IFRS or IFRS SME |
| III (Small) | ≤20M GEL | ≤10M | ≤50 | IFRS or IFRS SME |
| IV (Micro) | ≤2M GEL | ≤1M | ≤10 | SARAS Category IV Standard |

**Prixio at launch = Category IV** — simplified financial statements, no mandatory audit.
Submission deadline: October 1 of the following year.

## Estonian Profit Tax Model (Key Rules)

```
Revenue earned → stays in company → 0% tax
Revenue distributed as dividends → 15% corporate tax + 5% dividend withholding
Non-business expenses → treated as profit distribution → 15% tax
Personal expenses through company → taxable distribution
```

## Virtual Zone (VZP) Status

- Corporate tax on qualifying IT exports: **0%**
- VAT on qualifying IT exports: **0%**
- Dividend tax: **5%** (same)
- **Only applies to**: services delivered to clients OUTSIDE Georgia
- **Does NOT apply to**: Lotify/Courio domestic Georgian market revenue

## GITA Innovative Startup Status

- Salary income tax exemption for employees: **1-3 years**
- Renewable annually up to 10 years
- Requirements: 100,000 GEL investment from investors/accelerators OR 150,000 GEL state grants
- Apply at: gita.gov.ge
- In force since: September 24, 2025

## Penalty Reference

| Violation | Penalty |
|-----------|---------|
| Late declaration | 100 GEL per month |
| Late payment | 0.05% per day |
| Unmarked zero declaration | 100 GEL per month |
| VAT non-registration after threshold | Significant; retroactive VAT liability |

## Key Resources

Load these references for detailed information:
- [Georgian tax calendar](./references/tax-calendar.md)
- [Platform revenue accounting](./references/platform-accounting.md)

For live updates, always WebSearch: "rs.ge [topic] 2025" or "Georgia tax [topic] 2025"
