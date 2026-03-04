# Prixio Accounting Plugin

Claude Code plugin for Georgian tax compliance — Prixio LLC (Lotify + Courio).

## What it does

Ask Claude Code anything about Georgian accounting and get precise, actionable answers:

- "What do I need to file on rs.ge this month?"
- "How much income tax do I withhold from a 3,000 GEL salary?"
- "When do I need to register for VAT?"
- "How do I declare dividends? How much tax?"
- "What is the Estonian profit tax model?"
- "How does Lotify commission revenue get booked?"

The agent searches the web for current information when needed and runs
calculation scripts for exact numbers.

## Plugin Structure

```
prixio-accounting-plugin/
├── .claude-plugin/
│   └── plugin.json                    ← plugin manifest
├── agents/
│   └── accounting-agent.md            ← main agent definition
└── skills/
    ├── georgian-tax-knowledge/        ← SKILL 1: tax law knowledge base
    │   ├── SKILL.md
    │   ├── references/
    │   │   ├── tax-calendar.md        ← all deadlines & form numbers
    │   │   └── platform-accounting.md ← Lotify/Courio revenue accounting
    │   └── scripts/
    │       └── fetch_live_data.py     ← fetches live data from rs.ge
    ├── declaration-assistant/         ← SKILL 2: step-by-step filing guide
    │   └── SKILL.md
    └── revenue-calculator/            ← SKILL 3: tax calculation scripts
        ├── SKILL.md
        └── scripts/
            ├── salary_calc.py         ← gross→net salary calculator
            ├── dividend_calc.py       ← dividend tax calculator
            └── vat_tracker.py         ← VAT threshold tracker
```

## Install

```bash
# From Claude Code — add this folder as a local marketplace:
/plugin marketplace add ~/Desktop/prixio-marketplace

# Install the plugin:
/plugin install prixio-accounting@prixio-marketplace

# Restart Claude Code, then just ask naturally:
# "What tax declarations do I need to file this month?"
```

## Usage Examples

```
You: What do I need to file on rs.ge this month as a new LLC with no employees?

You: Calculate salary tax for a 2,500 GEL gross salary.

You: I want to take 10,000 GEL as dividends. What taxes do I pay?

You: My last 8 months revenue: 8000, 9000, 11000, 12000, 10000, 13000, 14000, 15000.
     Am I close to the VAT threshold?

You: Explain the Estonian profit tax model and when it's beneficial for Prixio.

You: How do I book Lotify escrow funds in accounting?
```

## Tax Rates (Georgia 2025)

| Tax | Rate |
|-----|------|
| Corporate profit (Estonian model) | 15% on distributed profits only |
| Retained/reinvested profits | 0% |
| VAT | 18% (threshold: 100,000 GEL/year) |
| Income tax (salaries) | 20% flat |
| Pension (employee) | 2% |
| Pension (employer) | 2% |
| Dividends | 5% withholding |

Monthly filing deadline: **15th of every month** via rs.ge

---

⚠️ Always verify final filings with a licensed Georgian accountant.
