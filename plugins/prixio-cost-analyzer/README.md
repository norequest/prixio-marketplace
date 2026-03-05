# prixio-cost-analyzer

Monthly cost analysis and burn rate tracking for **Prixio LLC** (Lotify + Courio).

## Skills

| Skill | Script | Description |
|-------|--------|-------------|
| infrastructure-costs | `infra_calc.py` | Cloud, APIs, DevOps costs with reverse-charge VAT |
| team-costs | `team_calc.py` | Salaries, Georgian tax withholding, contractors |
| marketing-costs | `marketing_calc.py` | Ad spend, CAC, ROI with Georgian market channels |
| burn-rate | `burn_rate_calc.py` | Master aggregator: runway, break-even, projections |

## Quick Start

```bash
# Infrastructure costs (starter profile)
python3 plugins/prixio-cost-analyzer/skills/infrastructure-costs/scripts/infra_calc.py --preset starter

# Team costs (small team, IC Status)
python3 plugins/prixio-cost-analyzer/skills/team-costs/scripts/team_calc.py --preset small --regime ic

# Marketing costs with CAC
python3 plugins/prixio-cost-analyzer/skills/marketing-costs/scripts/marketing_calc.py --preset growth --new-customers 150

# Full burn rate analysis
python3 plugins/prixio-cost-analyzer/skills/burn-rate/scripts/burn_rate_calc.py --preset early_stage --revenue 5000 --cash-on-hand 50000
```

## Georgian Tax Context

- Reverse-charge VAT (18%) on foreign cloud/SaaS services
- Salary PIT: 20% standard, 5% IC Status, 0% GITA Startup (years 1-3)
- Employer pension: 2% on top of gross salary
- All amounts in Georgian Lari (GEL)
