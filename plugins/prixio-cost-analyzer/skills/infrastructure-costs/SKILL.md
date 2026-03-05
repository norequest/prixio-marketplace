---
name: infrastructure-costs
description: >
  Calculates monthly infrastructure costs for Prixio LLC. Use this skill
  for: cloud hosting, database, CDN, API services, DevOps tools, payment
  gateway fees, and third-party service costs. Triggers on: "infrastructure",
  "hosting", "cloud", "server", "API cost", "DevOps", "SaaS cost",
  "service cost", "infra".
allowed-tools: Bash, Read
---

# Infrastructure Cost Calculator

> **Context**: Prixio LLC (Lotify + Courio) Georgian IT startup
> **Last updated**: March 2026

## Usage

### Preset Mode
```bash
python3 {baseDir}/scripts/infra_calc.py --preset starter
python3 {baseDir}/scripts/infra_calc.py --preset growth --vat
python3 {baseDir}/scripts/infra_calc.py --preset scale --vat
```

### Custom Mode
```bash
python3 {baseDir}/scripts/infra_calc.py --monthly-json '{
  "servers": 150, "database": 80, "cdn_storage": 30, "domain_ssl": 10,
  "payment_gateway": 50, "sms_notifications": 40, "email_service": 15,
  "maps_api": 60, "push_notifications": 0,
  "ci_cd": 25, "monitoring": 20, "logging": 15
}'
```

### With VAT (reverse-charge on foreign services)
```bash
python3 {baseDir}/scripts/infra_calc.py --preset growth --vat
```

## Presets

| Preset | Monthly Range | Profile |
|--------|-------------|---------|
| starter | 250-400 GEL | Single VPS, free tiers, minimal APIs |
| growth | 800-1500 GEL | Managed DB, paid APIs, monitoring |
| scale | 3000-6000 GEL | Multi-server, full stack, redundancy |

## Georgian Tax Notes

- Foreign cloud services (AWS, GCP, Hetzner) = reverse-charge VAT 18%
- If NOT VAT-registered: reverse-charge is pure cost (+18%)
- If VAT-registered: input credit offsets, net = 0
- TBC Pay processing: ~1.5% on transaction volume
