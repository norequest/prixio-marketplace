# IT Tax Regime Comparison — Decision Guide

> **Last updated**: March 2026.

## Quick Decision Matrix

```
START HERE → What is your entity type?
│
├── Individual Entrepreneur (IE)
│   └── Revenue < 500K GEL? → Small Business Status (1% tax)
│   └── Revenue > 500K GEL? → Consider forming LLC
│
├── LLC (შპს) / JSC (სს)
│   ├── Do you export IT services?
│   │   ├── YES (100% export)
│   │   │   ├── Want 0% CIT, don't care about PIT? → VZP
│   │   │   ├── Want lower PIT for employees? → International Company
│   │   │   └── New startup with innovation? → GITA Innovative Startup
│   │   │
│   │   ├── YES (>98% export, <2% domestic)
│   │   │   └── → International Company Status
│   │   │
│   │   └── YES (mixed domestic + export)
│   │       └── → VZP (0% on exports, standard on domestic)
│   │
│   └── Domestic market only?
│       ├── Standard LLC → 15% CIT (Estonian model, only on distributed profits)
│       ├── Manufacturing? → Consider FIZ
│       └── Innovation + investment? → GITA Startup
│
└── Branch of Foreign Company
    └── Standard taxation (15% CIT on Georgian-source profits)
```

## Detailed Comparison

### Scenario 1: Solo Developer / Freelancer
**Best: Individual Entrepreneur + Small Business Status**
- 1% turnover tax on income up to 500K GEL
- Simplest structure, minimal compliance
- Cannot have VZP/IC status (those require legal entity)

### Scenario 2: IT Company Exporting Software (few employees)
**Best: LLC + VZP Status**
- 0% CIT on exported IT profits
- Employees still pay 20% PIT + 4% pension
- Good for: SaaS companies, outsourcing firms with mostly profit
- Apply: LEPL Financial-Analytical Service
- **Caution**: VZP eligible activities are NARROWER than IC — limited to software development and directly related services (maintenance, support, updates, licensing of Georgia-developed software)
- VZP certificates are **not binding** on tax authorities — substance matters more than certificate

### Scenario 3: IT Company with Many Employees Exporting
**Best: LLC + International Company Status**
- 5% CIT (slightly higher than VZP's 0%)
- BUT 5% PIT for employees (saves 15% per person!)
- 0% dividend for non-resident shareholders
- 0% property tax on non-land property used for permitted activities
- Good for: dev shops, agencies, companies where payroll > profit
- Apply: Revenue Service (rs.ge)
- **Requires**: 2+ years experience, 98%+ export revenue, adequate local staff
- IC eligible activities are BROADER and have CLEARER legal definitions (with NACE codes)

### Scenario 4: Early-Stage Innovative Startup
**Best: LLC + GITA Innovative Startup Status**
- 0% PIT years 1-3 → 5% years 4-6 → 10% years 7-10 (on salaries up to 10K GEL/mo)
- 0% CIT years 1-3 → 5% years 4-6 → 10% years 7-10
- Access to GITA grants ($2K-$250K)
- 300% R&D tax credit for innovative SMEs
- Good for: pre-revenue startups, deep tech, R&D-heavy
- Apply: gita.gov.ge (reviewed within 15 business days)
- **Requires**: 100K GEL investment from approved sources OR 150K GEL GITA grant
- **Growth requirement**: 5M GEL total investment by year 3; 15M GEL by year 6
- Registration fee: 200 GEL

### Scenario 5: Hardware + Software in Special Zone
**Best: FIZ Enterprise**
- 0% on almost everything (CIT, VAT, customs, property, dividends)
- Requires physical presence in Free Industrial Zone
- Good for: hardware manufacturing, data centers
- Locations: Kutaisi, Poti

## Cannot Combine

| ❌ | VZP + IC Status |
| ❌ | VZP + GITA Startup |
| ❌ | IC + GITA Startup |
| ❌ | VZP/IC + Small Business (different entity types) |
| ✅ | Any special status + VAT registration |
| ✅ | VZP + hiring employees (normal PIT applies) |

## Cost-Benefit Analysis Example

**Company**: 5 employees, 500K GEL annual revenue, 200K GEL distributed profit

| Regime | CIT | PIT (5 employees × 3K GEL/mo) | Total Tax |
|--------|-----|------|-----------|
| **Standard LLC** | 30,000 (15%) | 36,000 (20%) + pension | ~70,000+ |
| **VZP** | 0 (export) | 36,000 (20%) + pension | ~40,000 |
| **IC Status** | 10,000 (5%) | 9,000 (5%) + pension | ~23,000 |
| **GITA Startup (yr 1-3)** | 0 | 0 + pension | ~7,200 |

*Note: Pension = 4% employer+employee combined, cannot be avoided*
