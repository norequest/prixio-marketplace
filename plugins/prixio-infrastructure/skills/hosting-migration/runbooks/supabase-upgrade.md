# Supabase Tier Upgrade Runbook

**Applicable to:** All Prixio projects using Supabase (Lotify, Courio)
**Estimated downtime:** 0 minutes (tier upgrades are non-disruptive)
**Difficulty:** Low
**Cost impact:** Varies by tier (see below)

---

## Tier Comparison

| Feature | Free | Pro ($25/mo) | Team ($599/mo) |
|---------|------|-------------|----------------|
| **Database** | | | |
| Dedicated Postgres | Shared | Dedicated | Dedicated |
| Database size | 500 MB | 8 GB (then $0.125/GB) | 8 GB (then $0.125/GB) |
| Automatic backups | None | 7 days | 14 days |
| Point-in-time recovery | No | No | Yes |
| **Connections** | | | |
| Direct connections | 60 | 200 | 200 |
| Pooler connections (Supavisor) | 200 | 1,500 | 1,500 |
| **Auth** | | | |
| MAU | 50,000 | 100,000 | 100,000 |
| Social OAuth | Yes | Yes | Yes |
| SSO/SAML | No | No | Yes |
| **Storage** | | | |
| Storage | 1 GB | 100 GB | 100 GB |
| File upload limit | 50 MB | 5 GB | 5 GB |
| **Realtime** | | | |
| Concurrent connections | 200 | 500 | 500 |
| Messages/month | 2 million | 5 million | 5 million |
| **Edge Functions** | | | |
| Invocations/month | 500,000 | 2 million | 2 million |
| **Compute** | | | |
| Compute | Shared | Dedicated (Micro default) | Dedicated (Small default) |
| **Support** | | | |
| Support | Community | Email | Priority |
| SLA | None | None | 99.9% uptime |

### Cost in GEL (approximate, 1 USD ~ 2.7 GEL)

| Tier | USD/month | GEL/month |
|------|-----------|-----------|
| Free | $0 | 0 GEL |
| Pro | $25 | ~67.5 GEL |
| Team | $599 | ~1,617 GEL |

---

## Free to Pro: When to Upgrade

Upgrade from Free to Pro when ANY of these are true:

### Database Size > 400 MB
```sql
-- Check current database size
SELECT pg_size_pretty(pg_database_size('postgres'));
```

### Connection Saturation
```sql
-- Check current connections vs limit
SELECT count(*) as current_connections,
       (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_connections
FROM pg_stat_activity;
```

### Need for Backups
- Free tier has NO automatic backups
- Pro tier includes 7-day automatic daily backups

### Storage > 900 MB
```sql
-- Check storage usage via Supabase dashboard
-- Or via API
```

### Need for Custom Domains
- Free tier: `<project-ref>.supabase.co`
- Pro tier: Custom domain (e.g., `db.lotify.ge`)

---

## How to Upgrade: Free to Pro

### Step 1: Review Current Usage

Go to Supabase Dashboard -> Project Settings -> Usage

Note:
- Current database size
- Current connection count (peak)
- Current storage usage
- Current MAU (monthly active users)

### Step 2: Add Payment Method

1. Go to [supabase.com/dashboard/org](https://supabase.com/dashboard/org)
2. Select your organization
3. Go to **Billing**
4. Add a payment method (credit card)

### Step 3: Upgrade

1. Go to **Billing** -> **Subscription**
2. Click **Upgrade to Pro**
3. Review the changes
4. Confirm

### Step 4: Verify

```bash
# Test connection (should now support more concurrent connections)
# No application changes needed -- the upgrade is seamless
curl -s https://<project-ref>.supabase.co/rest/v1/ \
  -H "apikey: <anon-key>" \
  -H "Authorization: Bearer <anon-key>"
```

### What Changes Immediately

- Connection limits increase (60 -> 200 direct, 200 -> 1,500 pooler)
- Compute upgrades to dedicated (may cause a brief restart, <30 seconds)
- Automatic daily backups begin
- Storage limit increases to 100 GB
- File upload limit increases to 5 GB

---

## Pro to Team: When to Upgrade

Upgrade to Team only when you need:

- **Point-in-time recovery (PITR)** -- essential for financial data (TBC Pay transactions)
- **SSO/SAML** -- if enterprise customers need single sign-on
- **SLA guarantee** -- 99.9% uptime SLA
- **Priority support** -- faster response from Supabase team
- **SOC 2 compliance** -- if required by partners

> For Prixio's current scale, Pro is sufficient. Team tier at ~1,617 GEL/mo is only justified when revenue supports it.

---

## Connection Pooling: Supavisor Setup

Supabase uses Supavisor (built-in connection pooler) by default. Here is how to optimize it.

### Connection String Formats

```bash
# Direct connection (bypasses pooler, use for migrations only)
postgresql://postgres.[ref]:[password]@db.[ref].supabase.co:5432/postgres

# Transaction mode pooler (recommended for serverless/API)
postgresql://postgres.[ref]:[password]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres

# Session mode pooler (for features needing session state like LISTEN/NOTIFY)
postgresql://postgres.[ref]:[password]@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
```

### Best Practices for Prixio Apps

```typescript
// In your Fastify/API app -- use transaction mode pooler
const DATABASE_URL = process.env.DATABASE_URL;
// This should be the :6543 (transaction mode) URL

// For Supabase Realtime -- uses its own connection, no pooler needed
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  realtime: {
    params: {
      eventsPerSecond: 10,
    },
  },
});
```

### Monitoring Connections

```sql
-- Current connections by application
SELECT application_name, count(*)
FROM pg_stat_activity
GROUP BY application_name
ORDER BY count(*) DESC;

-- Connection states
SELECT state, count(*)
FROM pg_stat_activity
GROUP BY state;

-- Kill idle connections (if needed)
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < NOW() - INTERVAL '10 minutes'
  AND application_name NOT IN ('supavisor', 'supabase_admin');
```

---

## Monitoring: When to Upgrade

Set up alerts for these thresholds:

### Database Size

| Threshold | Action |
|-----------|--------|
| 70% of limit | Plan upgrade timeline |
| 85% of limit | Initiate upgrade |
| 95% of limit | Urgent -- upgrade immediately |

### Connection Count

| Threshold | Action |
|-----------|--------|
| 60% of max pooler connections | Monitor closely |
| 80% of max pooler connections | Optimize queries, reduce idle connections |
| 90% of max pooler connections | Upgrade tier |

### Compute (CPU/Memory)

Check in Supabase Dashboard -> Reports -> Database:
- **CPU > 80% sustained** -- consider compute add-on upgrade
- **Memory > 80% sustained** -- consider compute add-on upgrade
- **Disk I/O saturation** -- consider compute add-on with more IOPS

### Storage

| Threshold | Action |
|-----------|--------|
| 70% of limit | Audit storage usage, clean up if possible |
| 85% of limit | Plan upgrade or add storage add-on |

---

## Compute Add-ons (Pro tier)

Instead of upgrading to Team, you can add compute to Pro:

| Compute Size | vCPU | RAM | Price/mo | GEL/mo |
|-------------|------|-----|----------|--------|
| Micro (default) | 2 | 1 GB | included | - |
| Small | 2 | 2 GB | $25 | ~67.5 |
| Medium | 2 | 4 GB | $50 | ~135 |
| Large | 4 | 8 GB | $100 | ~270 |
| XL | 8 | 16 GB | $200 | ~540 |

### How to change compute

1. Dashboard -> Project Settings -> Compute
2. Select new compute size
3. Confirm (causes a brief restart, <1 minute)

---

## Checklist

- [ ] Reviewed current usage metrics
- [ ] Confirmed payment method is set up
- [ ] Scheduled upgrade during low-traffic period (for compute changes)
- [ ] Verified application uses pooler connection string (`:6543`)
- [ ] Set up monitoring alerts for key thresholds
- [ ] Updated budget tracking with new monthly cost
- [ ] Tested application after upgrade
- [ ] Documented the upgrade in internal changelog
