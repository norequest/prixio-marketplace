# Railway to Fly.io Migration Runbook

**Applicable to:** Courio API or Lotify API (Fastify 5, TypeScript ESM)
**Estimated downtime:** 2-5 minutes (DNS propagation only)
**Difficulty:** Low-Medium
**Cost impact:** Railway ~$5-20/mo variable -> Fly.io ~$3-15/mo (pay-per-use with free allowance)

---

## Prerequisites

- [ ] Fly.io account created at [fly.io](https://fly.io)
- [ ] `flyctl` CLI installed (`brew install flyctl`)
- [ ] Authenticated (`fly auth login`)
- [ ] DNS access for the application domain
- [ ] Current Railway environment variables exported
- [ ] Dockerfile in the project root or `apps/api/`

---

## Step 1: Initialize Fly App

**Rollback:** `fly apps destroy <app-name>`. No impact on production.

```bash
cd ~/Desktop/courio/courio

# Create a new Fly app (do NOT deploy yet)
fly launch --no-deploy --name courio-api-prod --region ams
```

This generates a `fly.toml`. Replace its contents with the configuration below.

---

## Step 2: Configure fly.toml

**Rollback:** Edit or delete `fly.toml`. No impact on production.

```toml
# fly.toml -- Courio API on Fly.io
app = "courio-api-prod"
primary_region = "ams"  # Amsterdam -- closest major region to Tbilisi

[build]
  dockerfile = "apps/api/Dockerfile"

[env]
  NODE_ENV = "production"
  HOST = "0.0.0.0"
  PORT = "3000"
  LOG_LEVEL = "info"

[http_service]
  internal_port = 3000
  force_https = true
  auto_stop_machines = "suspend"
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

  [http_service.concurrency]
    type = "requests"
    hard_limit = 250
    soft_limit = 200

[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  path = "/health"
  timeout = "5s"

[checks]
  [checks.health]
    grace_period = "10s"
    interval = "30s"
    method = "GET"
    path = "/health"
    port = 3000
    timeout = "5s"
    type = "http"

[[vm]]
  size = "shared-cpu-2x"
  memory = "1gb"
  cpu_kind = "shared"
  cpus = 2
```

### Key configuration notes:
- **`auto_stop_machines = "suspend"`** -- Machines suspend when idle, resume on request. Saves cost.
- **`min_machines_running = 1`** -- At least one machine always running (avoids cold start on first request).
- **`primary_region = "ams"`** -- Amsterdam is the closest major Fly.io region to Tbilisi (~2,800 km). Alternative: `waw` (Warsaw).

---

## Step 3: Configure Secrets

**Rollback:** `fly secrets unset <KEY>`. No impact on production.

```bash
# Set secrets (these are encrypted, NOT stored in fly.toml)
fly secrets set \
  SUPABASE_URL="https://your-project.supabase.co" \
  SUPABASE_ANON_KEY="eyJ..." \
  SUPABASE_SERVICE_ROLE_KEY="eyJ..." \
  DATABASE_URL="postgresql://postgres.[ref]:[password]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres" \
  TBC_PAY_CLIENT_ID="your-client-id" \
  TBC_PAY_CLIENT_SECRET="your-client-secret" \
  TBC_PAY_API_URL="https://api.tbcbank.ge" \
  TBC_PAY_CALLBACK_URL="https://api.courio.ge/webhooks/tbc-pay" \
  LOTIFY_WEBHOOK_URL="https://lotify.ge/api/webhooks/courio" \
  LOTIFY_WEBHOOK_SECRET="your-hmac-secret"

# Verify secrets are set (values are hidden)
fly secrets list
```

---

## Step 4: Deploy

**Rollback:** `fly deploy --image <previous-image>` or `fly releases rollback`. No impact on production yet (DNS still points to Railway).

```bash
# Deploy the application
fly deploy

# Watch the deployment
fly status
fly logs
```

### Verify deployment

```bash
# Fly.io gives you a default URL
curl -s https://courio-api-prod.fly.dev/health | jq .

# Check response time
curl -s -o /dev/null -w "Time: %{time_total}s\n" https://courio-api-prod.fly.dev/health
```

---

## Step 5: Auto-Scaling Configuration

**Rollback:** Adjust scaling parameters. No impact on production.

```bash
# Set scaling parameters
fly scale count 1 --max-per-region 3

# View current machine status
fly machine list
```

### Scaling strategy for Courio API:
- **Minimum:** 1 machine always running (avoid cold starts for webhooks)
- **Maximum:** 3 machines per region (handle traffic spikes)
- **Scale trigger:** When concurrent requests exceed soft_limit (200)

---

## Step 6: Health Checks

Fly.io uses the health checks defined in `fly.toml` to:
- Determine when a new deployment is healthy (rolling deploys)
- Restart unhealthy machines automatically
- Route traffic only to healthy machines

### Verify health checks are passing

```bash
fly checks list
fly status
```

### Custom health check endpoint (ensure your Fastify app has this)

```typescript
// In your Fastify app
fastify.get('/health', async () => {
  return {
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: process.env.npm_package_version || 'unknown',
  };
});
```

---

## Step 7: DNS Cutover

**Rollback:** Revert DNS record. Traffic returns to Railway within TTL.

### 7.1 Lower TTL (24 hours before)

```
api.courio.ge.  60  IN  CNAME  courio-api-production.up.railway.app.
```

### 7.2 Add custom domain to Fly.io

```bash
fly certs create api.courio.ge

# Fly.io will show you the required DNS records
# Usually a CNAME to <app-name>.fly.dev
fly certs show api.courio.ge
```

### 7.3 Update DNS

```
; Replace Railway CNAME with Fly.io
api.courio.ge.  60  IN  CNAME  courio-api-prod.fly.dev.
```

### 7.4 Wait for certificate provisioning

```bash
# Check certificate status
fly certs check api.courio.ge

# Watch until it shows "Ready"
watch -n 10 'fly certs show api.courio.ge'
```

### 7.5 Verify

```bash
curl -s https://api.courio.ge/health | jq .
```

---

## Step 8: Rollback Plan

### Instant rollback (DNS)

```
; Point back to Railway
api.courio.ge.  60  IN  CNAME  courio-api-production.up.railway.app.
```

### Fly.io deployment rollback

```bash
# List releases
fly releases

# Rollback to previous release
fly releases rollback <version>
```

### Full rollback to Railway

1. Revert DNS to Railway CNAME
2. Verify Railway service is still running
3. Destroy Fly.io app: `fly apps destroy courio-api-prod`

---

## Step 9: Post-Migration

### Set up CI/CD with GitHub Actions

```yaml
# .github/workflows/deploy-fly.yml
name: Deploy to Fly.io
on:
  push:
    branches: [main]
    paths:
      - 'apps/api/**'
      - 'packages/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

### Generate deploy token

```bash
fly tokens create deploy -x 999999h
# Add this as FLY_API_TOKEN in GitHub repo secrets
```

### Decommission Railway

Wait 48-72 hours, then follow the same decommission steps as in the Railway-to-Hetzner runbook.

---

## Post-Migration Checklist

- [ ] API responds on `https://api.courio.ge/health`
- [ ] Response times acceptable (<500ms)
- [ ] Health checks passing (`fly checks list`)
- [ ] TBC Pay webhooks working
- [ ] Lotify integration working (HMAC-SHA256)
- [ ] SSL certificate valid and auto-renewing
- [ ] Auto-scaling configured
- [ ] CI/CD pipeline set up
- [ ] DNS TTL restored to 3600
- [ ] Railway decommissioned
- [ ] Cost tracking enabled (`fly billing`)
