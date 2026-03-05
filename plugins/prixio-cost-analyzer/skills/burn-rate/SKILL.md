---
name: burn-rate
description: >
  Master cost aggregator and burn rate analyzer for Prixio LLC. Combines
  all cost categories into a comprehensive monthly analysis with runway
  projections and break-even calculations. Triggers on: "burn rate",
  "runway", "total costs", "monthly budget", "break-even", "how long
  will money last", "cash runway", "budget overview", "cost summary".
allowed-tools: Bash, Read
---

# Burn Rate Analyzer

> **Context**: Prixio LLC (Lotify + Courio) Georgian IT startup
> **Last updated**: March 2026

## Usage

### Preset Mode
```bash
python3 {baseDir}/scripts/burn_rate_calc.py --preset pre_launch
python3 {baseDir}/scripts/burn_rate_calc.py --preset early_stage --revenue 5000 --cash-on-hand 50000
python3 {baseDir}/scripts/burn_rate_calc.py --preset growth_stage --revenue 25000 --cash-on-hand 200000
```

### Custom Mode
```bash
python3 {baseDir}/scripts/burn_rate_calc.py --costs-json '{
  "infrastructure": 800, "team": 12000, "marketing": 3000,
  "office": 600, "legal": 400, "financial": 150
}' --revenue 8000 --cash-on-hand 80000
```

## Presets

| Preset | Monthly Burn | Profile |
|--------|-------------|---------|
| pre_launch | 2000-3000 GEL | Founder only, minimal infra |
| early_stage | 8000-15000 GEL | Small team, growing |
| growth_stage | 25000-50000 GEL | Full team, aggressive marketing |

## Output Includes

- Category breakdown with percentages
- Monthly gross burn rate
- Net burn rate (costs - revenue)
- Cash runway in months
- Break-even revenue target
- 12-month cost projection
- Warning flags (low runway, cost concentration)
