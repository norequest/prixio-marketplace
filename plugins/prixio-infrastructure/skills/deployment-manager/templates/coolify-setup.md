# Coolify on Hetzner VPS - Setup Guide

Step-by-step guide for deploying Prixio services (Lotify + Courio) on a
Hetzner VPS using Coolify as the deployment platform.

---

## 1. Hetzner VPS Setup

### Recommended: CX32 (4 vCPU, 8 GB RAM, 80 GB NVMe)

1. Log in to [Hetzner Cloud Console](https://console.hetzner.cloud/).
2. Create a new project named `prixio-production`.
3. Add a server:
   - **Location:** Falkenstein (eu-central) or Helsinki (eu-north)
   - **Image:** Ubuntu 24.04
   - **Type:** CX32 (Shared vCPU, 4 cores, 8 GB RAM)
   - **Networking:** Enable public IPv4 + IPv6
   - **SSH Key:** Add your public SSH key
   - **Name:** `prixio-prod-01`
4. Add a firewall with the following rules:
   - Inbound: TCP 22 (SSH), TCP 80 (HTTP), TCP 443 (HTTPS), TCP 8000 (Coolify UI)
   - Outbound: Allow all
5. Attach the firewall to the server.

### Initial Server Hardening

```bash
# SSH into the server
ssh root@<server-ip>

# Update system
apt update && apt upgrade -y

# Create a non-root user
adduser prixio
usermod -aG sudo prixio

# Copy SSH keys to new user
rsync --archive --chown=prixio:prixio ~/.ssh /home/prixio

# Disable root SSH login
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd

# Set up automatic security updates
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

---

## 2. Install Coolify

```bash
# SSH as the non-root user
ssh prixio@<server-ip>

# Install Coolify (one-liner)
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | sudo bash

# Coolify will be available at: http://<server-ip>:8000
```

After installation:
1. Open `http://<server-ip>:8000` in your browser.
2. Create an admin account.
3. Complete the initial setup wizard.

---

## 3. GitHub Integration

1. In Coolify dashboard, go to **Sources** > **Add New**.
2. Select **GitHub App** (recommended over deploy keys).
3. Follow the OAuth flow to install the Coolify GitHub App on your organization.
4. Grant access to the specific repositories:
   - `prixio/lotify`
   - `prixio/courio`

---

## 4. Configure Applications

### Lotify API

1. Go to **Projects** > **Add New Resource** > **Application**.
2. Select your GitHub source and the `prixio/lotify` repository.
3. Configure:
   - **Branch:** `main`
   - **Build Pack:** Docker
   - **Dockerfile Path:** `Dockerfile.fastify`
   - **Build Args:** `APP_NAME=lotify-api`
   - **Port:** 3001
   - **Domain:** `api.lotify.ge`
4. Enable **Auto Deploy** on push to main.

### Courio API

1. Same steps as above but for `prixio/courio`.
2. Configure:
   - **Build Args:** `APP_NAME=courio-api`
   - **Port:** 3001 (internal, mapped differently)
   - **Domain:** `api.courio.ge`

### Lotify Web / Courio Admin

1. Same repository setup.
2. Configure:
   - **Build Pack:** Docker
   - **Dockerfile Path:** `Dockerfile.nextjs`
   - **Build Args:** `APP_NAME=lotify-web` (or `courio-admin`)
   - **Port:** 3000
   - **Domain:** `lotify.ge` (or `admin.courio.ge`)

---

## 5. SSL via Let's Encrypt

Coolify handles SSL automatically via its built-in Caddy/Traefik proxy:

1. Go to **Settings** > **SSL**.
2. Ensure Let's Encrypt is enabled (default).
3. For each application, set the **Domain** field. Coolify will automatically
   provision and renew certificates.

### DNS Configuration

Point your domains to the Hetzner VPS IP:

| Domain            | Type | Value          |
|-------------------|------|----------------|
| `lotify.ge`       | A    | `<server-ip>`  |
| `api.lotify.ge`   | A    | `<server-ip>`  |
| `admin.lotify.ge` | A    | `<server-ip>`  |
| `courio.ge`       | A    | `<server-ip>`  |
| `api.courio.ge`   | A    | `<server-ip>`  |
| `admin.courio.ge` | A    | `<server-ip>`  |

---

## 6. Environment Variable Management

1. In each application's settings, go to **Environment Variables**.
2. Add all required variables (never commit these to git):

### Lotify API

```
DATABASE_URL=postgresql://...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_ANON_KEY=...
TBC_PAY_CLIENT_ID=...
TBC_PAY_CLIENT_SECRET=...
TBC_PAY_PAYMENT_URL=...
COURIO_API_URL=https://api.courio.ge
COURIO_WEBHOOK_SECRET=...
REDIS_URL=redis://prixio-redis:6379
NODE_ENV=production
```

### Courio API

```
DATABASE_URL=postgresql://...
SUPABASE_URL=https://yyy.supabase.co
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_ANON_KEY=...
LOTIFY_WEBHOOK_URL=https://api.lotify.ge/webhooks/courio
LOTIFY_WEBHOOK_SECRET=...
REDIS_URL=redis://prixio-redis:6379
NODE_ENV=production
```

3. Mark sensitive values as **Secret** (they will be encrypted at rest).
4. Use **Shared Variables** for values common across applications.

---

## 7. Auto-Deploy from Main Branch

For each application:

1. Go to application **Settings** > **General**.
2. Enable **Auto Deploy**.
3. Set **Branch:** `main`.
4. Optionally enable **Preview Deployments** for pull requests.

Deploy flow:
```
Push to main --> GitHub webhook --> Coolify builds --> Health check --> Live
```

---

## 8. Backup Configuration

### Application Data

Coolify supports automated backups:

1. Go to **Settings** > **Backup**.
2. Configure S3-compatible storage (Hetzner Object Storage recommended):
   - **Endpoint:** `https://fsn1.your-objectstorage.com`
   - **Bucket:** `prixio-backups`
   - **Access Key / Secret Key:** from Hetzner
3. Set schedule: daily at 03:00 UTC.

### Database Backups

Since both projects use Supabase (hosted), database backups are managed by
Supabase's built-in point-in-time recovery. For additional safety:

```bash
# Manual backup via pg_dump (run from server or CI)
pg_dump "$DATABASE_URL" --format=custom --file="backup_$(date +%Y%m%d).dump"

# Upload to S3
aws s3 cp "backup_$(date +%Y%m%d).dump" s3://prixio-backups/db/
```

### Redis Backup

Redis is configured with `appendonly yes` in docker-compose. The AOF file is
persisted to the `redis-data` volume. For off-server backup:

```bash
# Copy RDB snapshot
docker cp prixio-redis:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb
```

---

## 9. Monitoring

Coolify provides basic monitoring out of the box. For production, consider:

1. **Uptime monitoring:** Use Uptime Kuma (can run as a Coolify service).
2. **Log aggregation:** Coolify shows real-time logs per application.
3. **Alerts:** Configure webhook notifications in Coolify to send alerts to
   Telegram or Discord when deployments fail.

---

## Cost Estimate

| Item                | Monthly Cost |
|---------------------|-------------|
| Hetzner CX32        | ~7.50 EUR   |
| Hetzner Object Storage (50 GB) | ~2.50 EUR |
| Domain (lotify.ge)  | ~10 EUR/yr  |
| Domain (courio.ge)  | ~10 EUR/yr  |
| **Total**           | **~12 EUR/mo** |

This replaces Railway/Vercel costs for self-hosted services while maintaining
the same deployment experience via Coolify.
