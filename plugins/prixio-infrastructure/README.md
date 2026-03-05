# prixio-infrastructure

Virtual DevOps engineer for **Prixio LLC** (Lotify + Courio). Covers the full infrastructure lifecycle: advise, deploy, migrate, audit, scale, optimize.

## Skills

| Skill | Description |
|-------|-------------|
| infrastructure-advisor | Compare hosting providers, recommend tiers, Georgian-specific factors |
| deployment-manager | Generate deployment configs, CI/CD pipelines, zero-downtime strategies |
| hosting-migration | Step-by-step migration runbooks between providers with rollback plans |
| production-readiness | Audit and harden setup for real traffic (security, reliability, observability) |
| scaling-planner | Capacity planning based on traffic projections and load profiles |
| cost-optimizer | Find waste, maximize free tiers, bundle analysis, VAT optimization |

## Quick Start

```bash
# Get hosting recommendation for current stage
# → triggers infrastructure-advisor

# Generate Dockerfile for Courio API
# → triggers deployment-manager

# Migrate Courio from Railway to Hetzner
# → triggers hosting-migration

# Run production readiness audit
# → triggers production-readiness

# Plan for 1000 concurrent users
# → triggers scaling-planner

# Find cost savings
# → triggers cost-optimizer
```

## Stack Context

- **Lotify**: Next.js 15 (Vercel) + Fastify 5 API + Supabase + Upstash Redis
- **Courio**: Fastify 5 API (Railway) + Next.js 15 Admin + Supabase + PostGIS + Expo SDK 54
- **Shared**: pnpm monorepo + Turborepo, TypeScript ESM, Georgian market (GEL currency)

## Georgian-Specific Considerations

- Reverse-charge VAT (18%) on foreign cloud services if not VAT-registered
- Latency to Tbilisi matters for real-time features (auctions, tracking)
- Limited local hosting options; Hetzner Finland is closest EU DC
- Data residency not legally required but preferred for financial data
