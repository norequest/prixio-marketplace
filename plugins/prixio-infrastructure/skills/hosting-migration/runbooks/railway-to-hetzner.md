# Railway to Hetzner VPS Migration Runbook

**Applicable to:** Courio API (Fastify 5, TypeScript ESM, Docker)
**Estimated downtime:** 2-5 minutes (DNS propagation only)
**Difficulty:** Medium
**Cost impact:** Railway ~$5-20/mo variable -> Hetzner CX32 ~EUR 5.39/mo fixed (~15.6 GEL/mo)

---

## Prerequisites

Before starting, ensure you have:

- [ ] Hetzner Cloud account created at [console.hetzner.cloud](https://console.hetzner.cloud)
- [ ] SSH key pair generated (`ssh-keygen -t ed25519 -C "prixio-hetzner"`)
- [ ] SSH public key added to Hetzner Cloud Console -> Security -> SSH Keys
- [ ] DNS access for `courio-api-production.up.railway.app` replacement domain
- [ ] Current Railway environment variables exported (see Step 4)
- [ ] Docker Hub or GitHub Container Registry (GHCR) account for image hosting
- [ ] This runbook read in full before starting

## Pre-Migration Checklist

```bash
# Export current Railway env vars
railway variables --json > railway-env-backup.json

# Note current DNS TTL
dig courio-api-production.up.railway.app +short

# Take note of current API response for comparison
curl -s https://courio-api-production.up.railway.app/health | jq .
```

---

## Step 1: Provision Hetzner CX32 VPS

**Rollback:** Delete the server from Hetzner Console. No impact on production.

### 1.1 Create the server

```bash
# Install hcloud CLI if not present
brew install hcloud

# Configure CLI
hcloud context create prixio
# Enter your Hetzner API token when prompted

# Create CX32 server (4 vCPU, 8GB RAM, 80GB SSD)
# Location: Helsinki (hel1) or Nuremberg (nbg1) -- closest to Tbilisi
hcloud server create \
  --name courio-api-prod \
  --type cx32 \
  --image ubuntu-24.04 \
  --location hel1 \
  --ssh-key prixio-hetzner
```

### 1.2 Note the server IP

```bash
export HETZNER_IP=$(hcloud server ip courio-api-prod)
echo "Server IP: $HETZNER_IP"
```

### 1.3 Configure firewall

```bash
hcloud firewall create --name courio-api-fw

# Allow SSH, HTTP, HTTPS
hcloud firewall add-rule courio-api-fw --direction in --protocol tcp --port 22 --source-ips 0.0.0.0/0 --source-ips ::/0 --description "SSH"
hcloud firewall add-rule courio-api-fw --direction in --protocol tcp --port 80 --source-ips 0.0.0.0/0 --source-ips ::/0 --description "HTTP"
hcloud firewall add-rule courio-api-fw --direction in --protocol tcp --port 443 --source-ips 0.0.0.0/0 --source-ips ::/0 --description "HTTPS"

hcloud firewall apply-to-resource courio-api-fw --type server --server courio-api-prod
```

---

## Step 2: Install Docker + Coolify

**Rollback:** Re-provision the server or uninstall. No impact on production.

### Option A: Coolify (Recommended -- gives you a UI)

```bash
ssh root@$HETZNER_IP

# Install Coolify (self-hosted PaaS)
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

# Coolify will be available at http://<HETZNER_IP>:8000
# Complete the setup wizard in the browser
```

### Option B: Direct Docker (lighter weight)

```bash
ssh root@$HETZNER_IP

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose plugin
apt install docker-compose-plugin -y

# Verify
docker --version
docker compose version

# Create app directory
mkdir -p /opt/courio-api
```

---

## Step 3: Build and Push Docker Image

**Rollback:** No impact on production. Image is pushed to registry only.

### 3.1 Ensure Dockerfile exists in Courio API

The Courio API should already have a Dockerfile. If not, create one:

```dockerfile
# /apps/api/Dockerfile
FROM node:20-alpine AS base
RUN corepack enable && corepack prepare pnpm@latest --activate

FROM base AS deps
WORKDIR /app
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY apps/api/package.json ./apps/api/
COPY packages/ ./packages/
RUN pnpm install --frozen-lockfile --filter @courio/api...

FROM base AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/apps/api/node_modules ./apps/api/node_modules
COPY --from=deps /app/packages/ ./packages/
COPY apps/api/ ./apps/api/
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json tsconfig.json ./
RUN pnpm --filter @courio/api build

FROM node:20-alpine AS runtime
WORKDIR /app
RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001 -G appgroup
COPY --from=build --chown=appuser:appgroup /app/apps/api/dist ./dist
COPY --from=build --chown=appuser:appgroup /app/apps/api/node_modules ./node_modules
COPY --from=build --chown=appuser:appgroup /app/apps/api/package.json ./
USER appuser
EXPOSE 3000
ENV NODE_ENV=production
CMD ["node", "dist/index.js"]
```

### 3.2 Build and push

```bash
# Using GitHub Container Registry
docker build -t ghcr.io/prixio/courio-api:latest -f apps/api/Dockerfile .
docker push ghcr.io/prixio/courio-api:latest

# Tag with commit SHA for rollback capability
export SHA=$(git rev-parse --short HEAD)
docker tag ghcr.io/prixio/courio-api:latest ghcr.io/prixio/courio-api:$SHA
docker push ghcr.io/prixio/courio-api:$SHA
```

---

## Step 4: Configure Environment Variables

**Rollback:** Update env vars. No impact on production.

### 4.1 Create .env file on server

```bash
ssh root@$HETZNER_IP

cat > /opt/courio-api/.env << 'ENVEOF'
# Server
NODE_ENV=production
HOST=0.0.0.0
PORT=3000

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres

# TBC Pay
TBC_PAY_CLIENT_ID=your-client-id
TBC_PAY_CLIENT_SECRET=your-client-secret
TBC_PAY_API_URL=https://api.tbcbank.ge
TBC_PAY_CALLBACK_URL=https://api.courio.ge/webhooks/tbc-pay

# Lotify Integration (HMAC webhooks)
LOTIFY_WEBHOOK_URL=https://lotify.ge/api/webhooks/courio
LOTIFY_WEBHOOK_SECRET=your-hmac-secret

# Logging
LOG_LEVEL=info
ENVEOF

chmod 600 /opt/courio-api/.env
```

> **IMPORTANT:** Copy the actual values from `railway-env-backup.json`. Do NOT commit the `.env` file to git.

### 4.2 Create docker-compose.yml

```bash
cat > /opt/courio-api/docker-compose.yml << 'EOF'
services:
  courio-api:
    image: ghcr.io/prixio/courio-api:latest
    container_name: courio-api
    restart: unless-stopped
    env_file: .env
    ports:
      - "127.0.0.1:3000:3000"
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: "2.0"
EOF
```

---

## Step 5: Set Up SSL with Caddy

**Rollback:** Remove Caddy, no impact on production (still on Railway).

### 5.1 Install Caddy as reverse proxy

```bash
ssh root@$HETZNER_IP

# Install Caddy
apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt update && apt install caddy -y
```

### 5.2 Configure Caddyfile

```bash
cat > /etc/caddy/Caddyfile << 'EOF'
api.courio.ge {
    reverse_proxy localhost:3000

    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        Referrer-Policy "strict-origin-when-cross-origin"
    }

    log {
        output file /var/log/caddy/courio-api.log {
            roll_size 10mb
            roll_keep 5
        }
    }
}
EOF

# Reload Caddy
systemctl reload caddy
```

> Caddy automatically provisions and renews Let's Encrypt certificates.

---

## Step 6: Test on New Server

**Rollback:** N/A -- this is testing only, production is still on Railway.

### 6.1 Start the application

```bash
ssh root@$HETZNER_IP
cd /opt/courio-api
docker compose up -d

# Check logs
docker compose logs -f --tail 50
```

### 6.2 Test via staging domain or direct IP

```bash
# Add a temporary staging DNS record: staging-api.courio.ge -> HETZNER_IP
# Or test directly via IP (SSL won't work, but HTTP will)

# Health check
curl -s http://$HETZNER_IP:3000/health | jq .

# If staging DNS is set up with Caddy:
curl -s https://staging-api.courio.ge/health | jq .
```

### 6.3 Run migration validator

```bash
python3 scripts/migration_validator.py \
  --source railway \
  --target hetzner \
  --app courio-api \
  --source-url https://courio-api-production.up.railway.app \
  --target-url https://staging-api.courio.ge
```

### 6.4 Run smoke tests

```bash
# Test key API endpoints
curl -s https://staging-api.courio.ge/health
curl -s -o /dev/null -w "%{http_code}" https://staging-api.courio.ge/api/v1/status

# Test response times (should be <500ms)
curl -s -o /dev/null -w "Time: %{time_total}s\n" https://staging-api.courio.ge/health
```

---

## Step 7: DNS Cutover

**Rollback:** Revert DNS A record to Railway's IP/CNAME. DNS will propagate back within TTL (60s if lowered).

### 7.1 Lower TTL (24 hours before cutover)

```
; In your DNS provider (Cloudflare, etc.)
; Change TTL for api.courio.ge from 3600 to 60
api.courio.ge.  60  IN  CNAME  courio-api-production.up.railway.app.
```

### 7.2 Perform the cutover

```
; Replace CNAME with A record pointing to Hetzner
api.courio.ge.  60  IN  A  <HETZNER_IP>
```

### 7.3 Monitor

```bash
# Watch DNS propagation
watch -n 5 'dig api.courio.ge +short'

# Monitor application logs
ssh root@$HETZNER_IP 'docker compose -f /opt/courio-api/docker-compose.yml logs -f --tail 20'

# Monitor Caddy access logs
ssh root@$HETZNER_IP 'tail -f /var/log/caddy/courio-api.log'
```

### 7.4 Verify from multiple locations

```bash
# Use DNS propagation checker
# https://www.whatsmydns.net/#A/api.courio.ge

# Or use curl with specific DNS
curl --resolve api.courio.ge:443:$HETZNER_IP https://api.courio.ge/health
```

---

## Step 8: Verify Webhooks

**Rollback:** If webhooks fail, revert DNS immediately (Step 7 rollback).

### 8.1 TBC Pay webhooks

- Log into TBC Pay merchant portal
- Update the callback URL if it was hardcoded to Railway URL (it should use the domain)
- Trigger a test payment or wait for the next real transaction
- Verify webhook received in application logs:
  ```bash
  ssh root@$HETZNER_IP 'docker compose -f /opt/courio-api/docker-compose.yml logs --tail 100 | grep -i "tbc\|webhook\|payment"'
  ```

### 8.2 Lotify <-> Courio integration

- The webhook URL should use `api.courio.ge` domain, so DNS cutover handles this
- If Lotify has the Railway URL hardcoded, update it in Lotify's environment variables
- Verify HMAC-SHA256 signature validation works:
  ```bash
  # Check for any webhook signature errors
  ssh root@$HETZNER_IP 'docker compose -f /opt/courio-api/docker-compose.yml logs --tail 200 | grep -i "hmac\|signature\|lotify"'
  ```
- Create a test shipment in Lotify and verify Courio receives the webhook
- Update a shipment status in Courio and verify Lotify receives the callback

### 8.3 Supabase Realtime

- Verify Realtime subscriptions still work (connections go from app to Supabase, not affected by migration)
- Check that RLS policies are not IP-restricted (they shouldn't be, but verify)

---

## Step 9: Decommission Railway

**Rollback:** Re-deploy on Railway from git. Railway keeps deployment history.

> **Wait at least 48-72 hours** after cutover before decommissioning.

### 9.1 Verify no traffic on Railway

```bash
# Check Railway logs for any remaining traffic
railway logs --tail 50
```

### 9.2 Stop Railway service

```bash
# Scale to zero first (keep the project for rollback)
railway service update --replicas 0

# After 1 week of stability, fully remove
railway service delete
```

### 9.3 Clean up

- Remove Railway CLI config if no longer needed
- Update internal documentation to reflect new hosting
- Remove Railway-specific environment variables or configs from the repo
- Increase DNS TTL back to 3600 (1 hour):
  ```
  api.courio.ge.  3600  IN  A  <HETZNER_IP>
  ```

---

## Rollback Summary

| Step | Rollback Action | Time to Recover |
|------|----------------|-----------------|
| 1-2 | Delete Hetzner server | Instant |
| 3 | Delete Docker image from registry | Instant |
| 4-5 | N/A (production unchanged) | N/A |
| 6 | Remove staging DNS | Instant |
| 7 | Revert DNS A record to Railway | 60s-5min (TTL) |
| 8 | Revert DNS (webhooks follow DNS) | 60s-5min |
| 9 | Re-deploy on Railway | 5-10 min |

---

## Post-Migration Checklist

- [ ] API responds correctly on `https://api.courio.ge/health`
- [ ] Response times are within acceptable range (<500ms)
- [ ] TBC Pay webhooks are being received and processed
- [ ] Lotify webhooks are being sent and received (both directions)
- [ ] SSL certificate is valid and auto-renewing (Caddy)
- [ ] Application logs are being collected
- [ ] Server monitoring is set up (uptime, CPU, memory, disk)
- [ ] Automatic Docker image updates are configured (Watchtower or CI/CD)
- [ ] DNS TTL restored to normal (3600)
- [ ] Railway service decommissioned
- [ ] Internal documentation updated
- [ ] Cost savings confirmed (~$10-15/mo saved)
- [ ] Backup strategy in place for Hetzner VPS (Hetzner snapshots or rsync)
