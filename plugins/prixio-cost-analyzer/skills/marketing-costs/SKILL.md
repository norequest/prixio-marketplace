---
name: marketing-costs
description: >
  Calculates monthly marketing and sales costs for Prixio LLC. Use this
  skill for: advertising budgets, digital marketing spend, CAC calculation,
  ROI analysis, Georgian market promotion costs. Triggers on: "marketing",
  "ads", "advertising", "CAC", "customer acquisition", "promotion",
  "ad spend", "marketing budget", "ROI".
allowed-tools: Bash, Read
---

# Marketing Cost Calculator

> **Context**: Prixio LLC (Lotify + Courio) Georgian IT startup
> **Last updated**: March 2026

## Usage

### Preset Mode
```bash
python3 {baseDir}/scripts/marketing_calc.py --preset bootstrap
python3 {baseDir}/scripts/marketing_calc.py --preset growth --new-customers 200 --vat
python3 {baseDir}/scripts/marketing_calc.py --preset aggressive --monthly-revenue 15000
```

### Custom Mode
```bash
python3 {baseDir}/scripts/marketing_calc.py --budget-json '{
  "google_ads": 500, "facebook_ads": 400, "tiktok_ads": 200,
  "seo_tools": 50, "social_tools": 30,
  "content_creation": 300, "graphic_design": 200,
  "outdoor_ads": 0, "print_materials": 100, "events": 0, "referral_bonuses": 200,
  "crm": 50, "sales_commissions": 0,
  "mymarket_listings": 100, "telegram_promotion": 50
}'
```

### With Analytics
```bash
python3 {baseDir}/scripts/marketing_calc.py --preset growth --new-customers 150 --monthly-revenue 8000
```

## Presets

| Preset | Monthly Range | Strategy |
|--------|-------------|----------|
| bootstrap | 300-600 GEL | Organic + minimal paid ads |
| growth | 2000-4000 GEL | Balanced paid + organic |
| aggressive | 8000-15000 GEL | Full-scale multi-channel |

## Georgian Market Notes

- Facebook is dominant social platform in Georgia
- mymarket.ge is key marketplace for awareness
- Telegram widely used for community building
- Reverse-charge VAT 18% on Google/Meta/TikTok ad spend
- Local outdoor advertising effective in Tbilisi (Rustaveli, Vake)
