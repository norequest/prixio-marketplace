---
name: cost-optimizer
description: >
  Finds infrastructure cost savings for Prixio LLC. Audits current spending,
  maximizes free tiers, recommends consolidation, and tracks VAT impact.
  Triggers on: "optimize cost", "save money", "reduce cost", "too expensive",
  "free tier", "cheaper", "cost optimization", "waste", "overpaying",
  "consolidate", "bundle".
allowed-tools: Bash, Read
---

# Cost Optimizer

Infrastructure cost optimization skill for Prixio LLC projects (Lotify, Courio, and future marketplace services).

## Usage Modes

### 1. Audit Mode (default)

Analyze current infrastructure spending across all Prixio projects and report:

- Total monthly cost in GEL
- Per-service breakdown
- Free tier utilization percentage
- Services approaching free tier limits
- Potential VAT liability (18% reverse-charge on foreign services)

```
"audit my infrastructure costs"
"what am I spending on infrastructure?"
"show current costs"
```

### 2. Optimization Mode

Generate actionable recommendations to reduce spending:

```
"optimize my infrastructure costs"
"how can I save money on hosting?"
"find cost savings"
```

### 3. Comparison Mode

Compare specific service alternatives:

```
"should I use Railway or Hetzner?"
"compare Vercel vs Cloudflare Pages"
"is Supabase Pro worth it?"
```

### 4. Growth Planning Mode

Project costs at different scale milestones:

```
"what will costs look like at 1000 users?"
"plan infrastructure for growth"
"when should I upgrade from free tiers?"
```

## What It Analyzes

### Services Tracked

- **Hosting:** Vercel, Railway, Hetzner, fly.io, Render, Cloudflare Pages
- **Database:** Supabase (PostgreSQL), Upstash Redis
- **Storage:** Supabase Storage, Cloudflare R2
- **Email:** Resend
- **Maps:** Google Maps Platform, Mapbox
- **Monitoring:** Sentry, UptimeRobot
- **CI/CD:** GitHub Actions
- **Payments:** TBC Pay
- **SMS:** Magti SMS
- **Push Notifications:** Firebase Cloud Messaging (FCM)
- **DNS/CDN:** Cloudflare
- **Domains:** Namecheap, .ge registrars

### Cost Categories

1. **Fixed costs** -- Monthly subscriptions (hosting plans, domain renewals)
2. **Usage-based costs** -- API calls, bandwidth, storage, compute hours
3. **Transaction costs** -- Payment processing fees (TBC Pay ~1.5%)
4. **Tax costs** -- VAT reverse-charge (18%) on foreign digital services

## How Savings Are Calculated

### Step 1: Baseline Assessment

Read the current infrastructure JSON (passed via `--current-json` or `--preset`) and calculate total monthly cost including:

- Direct service costs in GEL
- Currency conversion (EUR/USD to GEL at current rates)
- VAT reverse-charge where applicable

### Step 2: Optimization Analysis

For each service, evaluate:

- **Right-sizing:** Is the current tier appropriate for actual usage?
- **Free tier headroom:** How much free quota remains unused?
- **Alternative services:** Cheaper alternatives that meet requirements?
- **Consolidation:** Can multiple services be replaced by one? (e.g., single Hetzner VPS for multiple APIs)
- **Georgian alternatives:** Local services that avoid VAT and reduce latency (e.g., Magti over Twilio)

### Step 3: Recommendation Generation

Each recommendation includes:

- **Action:** What to change
- **Current cost:** What you pay now
- **Optimized cost:** What you would pay after the change
- **Monthly savings:** Difference in GEL
- **Effort level:** Low / Medium / High
- **Risk level:** Low / Medium / High
- **Prerequisites:** What must happen first

Recommendations are sorted by savings amount (highest first), with effort and risk as tiebreakers.

### Step 4: Summary Report

Output includes:

- Current total monthly cost
- Optimized total monthly cost
- Total potential savings (GEL and percentage)
- Prioritized action list
- Timeline for implementation

## Georgian Tax Context

Prixio LLC operates under the Estonian corporate tax model:

- **No CIT** on retained earnings
- **VAT not registered** (register at 100,000 GEL turnover threshold)
- **Reverse-charge VAT (18%)** applies to foreign digital services (hosting, SaaS)
- Foreign service costs should factor in this 18% when comparing with Georgian alternatives

## Reference Files

- `references/free-tier-limits.md` -- Comprehensive free tier limits for all tracked services
- `scripts/optimization_calc.py` -- Automated cost analysis and recommendation engine
