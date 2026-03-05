---
name: hosting-migration
description: >
  Step-by-step migration runbooks for moving Prixio LLC services between hosting
  providers. Includes DNS cutover, data migration, rollback plans, and downtime
  estimation. Triggers on: "migrate", "migration", "move to", "switch from",
  "switch to", "transfer", "Railway to Hetzner", "self-host", "move hosting".
allowed-tools: Bash, Read, Write, Edit
---

# Hosting Migration Skill

## Overview

This skill provides structured, battle-tested migration runbooks for moving Prixio LLC services (Lotify, Courio, and related infrastructure) between hosting providers. Every runbook follows the same methodology to minimize risk and downtime.

## Migration Methodology

All migrations follow a 4-phase approach:

### Phase 1: Prepare
- Audit current deployment (environment variables, secrets, dependencies, integrations)
- Provision target infrastructure
- Lower DNS TTL to 60s at least 24 hours before cutover
- Set up monitoring on both source and target

### Phase 2: Deploy
- Build and deploy the application on the target platform
- Configure environment variables, secrets, and integrations
- Set up SSL/TLS certificates
- Run the migration validator script (`scripts/migration_validator.py`)

### Phase 3: Cutover
- Verify target is healthy via staging domain or IP-based access
- Update DNS records to point to the new target
- Monitor error rates, latency, and webhook delivery
- Keep the source running in read-only/standby mode

### Phase 4: Decommission
- Wait 48-72 hours after cutover for DNS propagation and stability
- Verify no traffic is hitting the old source
- Take a final backup of the source
- Tear down the source infrastructure
- Update internal documentation and runbooks

## Supported Migration Paths

| Runbook | Source | Target | Typical Downtime |
|---------|--------|--------|-----------------|
| [railway-to-hetzner.md](runbooks/railway-to-hetzner.md) | Railway | Hetzner VPS | 2-5 min |
| [railway-to-flyio.md](runbooks/railway-to-flyio.md) | Railway | Fly.io | 2-5 min |
| [vercel-to-coolify.md](runbooks/vercel-to-coolify.md) | Vercel | Self-hosted Coolify | 2-5 min |
| [supabase-upgrade.md](runbooks/supabase-upgrade.md) | Supabase Free/Pro | Supabase Pro/Team | 0 min |
| [supabase-to-selfhosted.md](runbooks/supabase-to-selfhosted.md) | Supabase Cloud | Self-hosted PostgreSQL | 1-4 hours |

## How to Use Runbooks

1. **Read the entire runbook** before starting. Understand every step and the rollback plan.
2. **Schedule a maintenance window** if the migration involves downtime.
3. **Run the migration validator** before and after cutover:
   ```bash
   python3 scripts/migration_validator.py --source railway --target hetzner --app courio-api
   ```
4. **Follow the rollback plan** at the first sign of trouble. Do not improvise.
5. **Update this skill** with any lessons learned after each migration.

## Cost Context

All cost estimates reference GEL (Georgian Lari). Current approximate exchange rates:
- 1 USD ~ 2.7 GEL
- 1 EUR ~ 2.9 GEL

Prixio LLC operates under the Estonian tax model, so hosting costs are business expenses that reduce the taxable distribution base.

## Key Integration Points

When migrating any service, verify these integrations still work:
- **TBC Pay webhooks** -- payment callbacks must reach the new endpoint
- **Lotify <-> Courio webhooks** -- HMAC-SHA256 signed, verify both directions
- **Supabase connections** -- connection strings, pooler URLs, RLS policies
- **DNS and SSL** -- certificates must be valid for all custom domains
