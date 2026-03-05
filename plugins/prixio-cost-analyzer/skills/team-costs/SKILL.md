---
name: team-costs
description: >
  Calculates monthly team and personnel costs for Prixio LLC with Georgian
  tax law compliance. Use this skill for: salary calculations, hiring costs,
  employer tax burden, contractor costs, team budget planning. Triggers on:
  "team cost", "salary cost", "hiring", "personnel", "employee cost",
  "contractor", "outsource", "how much to hire".
allowed-tools: Bash, Read
---

# Team Cost Calculator

> **Context**: Prixio LLC (Lotify + Courio) Georgian IT startup
> **Last updated**: March 2026

## Usage

### Preset Mode
```bash
python3 {baseDir}/scripts/team_calc.py --preset solo
python3 {baseDir}/scripts/team_calc.py --preset small --regime ic
python3 {baseDir}/scripts/team_calc.py --preset medium --regime startup_1_3
```

### Custom Mode
```bash
python3 {baseDir}/scripts/team_calc.py --team-json '[
  {"role": "developer", "gross": 3500, "count": 2},
  {"role": "designer", "gross": 2000, "count": 1},
  {"role": "support", "gross": 1000, "count": 2}
]' --regime standard --accountant 500 --lawyer 300
```

### Tax Regimes
| Regime | PIT Rate | Notes |
|--------|----------|-------|
| standard | 20% | Default Georgian rate |
| ic | 5% | International Company status |
| startup_1_3 | 0% | GITA Startup years 1-3 (max 10,000/mo) |
| startup_4_6 | 5% | GITA Startup years 4-6 |
| startup_7_10 | 10% | GITA Startup years 7-10 |

## Georgian Market Salary Ranges (GEL/month gross)

| Role | Junior | Mid | Senior |
|------|--------|-----|--------|
| Full-stack Dev | 2000 | 3500 | 6000 |
| Mobile Dev | 2000 | 3500 | 5500 |
| Designer | 1200 | 2000 | 3500 |
| QA Engineer | 1200 | 2000 | 3000 |
| DevOps | 2500 | 3500 | 5000 |
| Marketing | 1200 | 2000 | 3000 |
| Support | 800 | 1000 | 1500 |
