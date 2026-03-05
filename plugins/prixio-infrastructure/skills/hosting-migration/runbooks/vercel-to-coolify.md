# Vercel to Self-Hosted Coolify Migration Runbook

**Applicable to:** Lotify Web (Next.js 15), Courio Web (Next.js 15)
**Estimated downtime:** 2-5 minutes (DNS propagation only)
**Difficulty:** Medium
**Cost impact:** Vercel Pro $20/mo per project -> Coolify on Hetzner ~EUR 5-10/mo total for multiple projects

---

## When This Makes Sense

Migrate from Vercel to self-hosted Coolify when:

- **Cost:** Multiple Next.js projects on Vercel Pro adds up ($20/mo each). A single Hetzner VPS can host all of them for ~EUR 5-10/mo.
- **Control:** Need custom server configuration, specific Node.js versions, or non-standard build pipelines.
- **Data residency:** Need to control where your data is processed (relevant for Georgian market).
- **Custom domains:** Vercel charges for additional domains on lower tiers.
- **Build minutes:** Exceeding Vercel's build minute limits.

**Do NOT migrate if:**
- You rely heavily on Vercel's Edge Functions (no direct equivalent in Coolify)
- You need Vercel's global CDN for performance-critical pages
- Your team depends on Vercel's preview deployments for PR reviews (Coolify has this but it is less polished)

---

## Prerequisites

- [ ] Hetzner VPS provisioned (CX32 or larger recommended for multiple apps)
- [ ] Coolify installed on the VPS (see railway-to-hetzner.md Step 2, Option A)
- [ ] DNS access for all application domains
- [ ] Current Vercel environment variables exported
- [ ] Git repository accessible from the VPS

---

## Step 1: Export Vercel Configuration

**Rollback:** No impact on production.

```bash
# Install Vercel CLI if needed
pnpm add -g vercel

# List current environment variables
vercel env ls --environment production

# Pull env vars locally for reference
vercel env pull .env.vercel-backup

# Note current build settings
vercel inspect --json
```

---

## Step 2: Set Up Coolify Project

**Rollback:** Delete project in Coolify UI. No impact on production.

### 2.1 Access Coolify Dashboard

Navigate to `http://<HETZNER_IP>:8000` and log in.

### 2.2 Create New Project

1. Go to **Projects** -> **New Project**
2. Name: `lotify-web` (or `courio-web`)
3. Click **Create**

### 2.3 Add New Resource

1. Inside the project, click **New Resource**
2. Select **Public Repository** or **Private Repository (GitHub App)**
3. Connect your GitHub repository
4. Select the repository and branch (`main`)

### 2.4 Configure Build Settings

In the resource settings:

| Setting | Value |
|---------|-------|
| Build Pack | Nixpacks (auto-detects Next.js) or Dockerfile |
| Base Directory | `apps/web` (for monorepo) |
| Build Command | `pnpm --filter @lotify/web build` |
| Start Command | `pnpm --filter @lotify/web start` |
| Port | 3000 |
| Health Check Path | `/api/health` |

### 2.5 Alternative: Use a Dockerfile

If Nixpacks doesn't work well with your monorepo, create a Dockerfile:

```dockerfile
# apps/web/Dockerfile
FROM node:20-alpine AS base
RUN corepack enable && corepack prepare pnpm@latest --activate

FROM base AS deps
WORKDIR /app
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY apps/web/package.json ./apps/web/
COPY packages/ ./packages/
RUN pnpm install --frozen-lockfile --filter @lotify/web...

FROM base AS build
WORKDIR /app
COPY --from=deps /app/ ./
COPY apps/web/ ./apps/web/
COPY turbo.json tsconfig.json ./
ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm --filter @lotify/web build

FROM node:20-alpine AS runtime
WORKDIR /app
RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001 -G appgroup
COPY --from=build --chown=appuser:appgroup /app/apps/web/.next/standalone ./
COPY --from=build --chown=appuser:appgroup /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=build --chown=appuser:appgroup /app/apps/web/public ./apps/web/public
USER appuser
EXPOSE 3000
ENV NODE_ENV=production
ENV HOSTNAME="0.0.0.0"
CMD ["node", "apps/web/server.js"]
```

> **Important:** For standalone output, add to `next.config.ts`:
> ```typescript
> const nextConfig = {
>   output: 'standalone',
> };
> ```

---

## Step 3: Configure Environment Variables

**Rollback:** Update variables in Coolify UI. No impact on production.

In Coolify, go to your resource -> **Environment Variables** and add:

```
# Public (available in browser)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_APP_URL=https://lotify.ge
NEXT_PUBLIC_API_URL=https://api.lotify.ge
NEXT_PUBLIC_TBC_PAY_MERCHANT_ID=your-merchant-id

# Server-only
SUPABASE_SERVICE_ROLE_KEY=eyJ...
TBC_PAY_CLIENT_SECRET=your-client-secret
```

---

## Step 4: Edge Function Alternatives

Vercel Edge Functions do not have a direct equivalent in Coolify. Here are alternatives:

| Vercel Feature | Coolify Alternative |
|----------------|-------------------|
| Edge Functions | Next.js API routes (Node.js runtime) |
| Edge Middleware | Next.js middleware (runs in Node.js, not at edge) |
| Edge Config | Environment variables or Redis |
| Image Optimization | `next/image` with `sharp` (installed automatically) |
| ISR | ISR works natively in Next.js standalone mode |
| Cron Jobs | Coolify has built-in cron or use system cron on VPS |

### Middleware Consideration

If you use Next.js middleware for geo-detection or similar edge features:

```typescript
// middleware.ts
// This will still work, but runs in Node.js instead of at the edge
// Performance difference is negligible for Georgian users connecting to a European server
export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

---

## Step 5: CDN Setup with Cloudflare

**Rollback:** Disable Cloudflare proxy (grey cloud icon). No impact on production.

Since Coolify doesn't have Vercel's global CDN, add Cloudflare as a CDN layer:

### 5.1 Add domain to Cloudflare

1. Go to [dash.cloudflare.com](https://dash.cloudflare.com)
2. Add your domain (e.g., `lotify.ge`)
3. Update nameservers at your registrar to Cloudflare's

### 5.2 Configure DNS

```
lotify.ge.     A     <HETZNER_IP>     Proxied (orange cloud)
www.lotify.ge. CNAME lotify.ge        Proxied (orange cloud)
```

### 5.3 Cloudflare Settings

| Setting | Value | Why |
|---------|-------|-----|
| SSL/TLS | Full (Strict) | Caddy/Coolify provides valid cert |
| Always Use HTTPS | On | Redirect HTTP to HTTPS |
| Minimum TLS | 1.2 | Security |
| Auto Minify | CSS, JS | Performance |
| Brotli | On | Compression |
| Cache Level | Standard | Cache static assets |
| Browser Cache TTL | 1 month | For static assets |

### 5.4 Page Rules (or Cache Rules)

```
# Cache static assets aggressively
lotify.ge/_next/static/*  -> Cache Level: Cache Everything, Edge TTL: 1 month
lotify.ge/images/*        -> Cache Level: Cache Everything, Edge TTL: 1 week

# Bypass cache for API routes
lotify.ge/api/*           -> Cache Level: Bypass
```

---

## Step 6: Deploy and Test

**Rollback:** N/A -- testing only, production still on Vercel.

### 6.1 Deploy in Coolify

Click **Deploy** in the Coolify dashboard, or push to the configured branch.

### 6.2 Test via Coolify-provided URL

Coolify gives each deployment a URL like `https://<random>.coolify.domain`. Test:

```bash
curl -s https://<coolify-url>/api/health | jq .

# Test page rendering
curl -s -o /dev/null -w "%{http_code}" https://<coolify-url>/

# Check response time
curl -s -o /dev/null -w "Time: %{time_total}s\n" https://<coolify-url>/
```

### 6.3 Visual comparison

Open both the Vercel deployment and Coolify deployment side by side. Check:
- [ ] Homepage renders correctly
- [ ] Authentication flow works
- [ ] Images load (next/image optimization)
- [ ] Fonts load
- [ ] API routes respond
- [ ] i18n routing works (Georgian/English)

---

## Step 7: DNS Cutover

**Rollback:** Revert DNS to Vercel. Traffic returns within TTL.

### 7.1 Lower TTL (24 hours before)

In Cloudflare (or your DNS provider):
```
lotify.ge.  60  IN  A  <VERCEL_IP>
```

### 7.2 Update DNS to Hetzner

```
lotify.ge.  60  IN  A  <HETZNER_IP>
```

If using Cloudflare proxy, the change is nearly instant since Cloudflare handles the routing.

### 7.3 Configure domain in Coolify

In Coolify resource settings, add the production domain (`lotify.ge`) and Coolify will configure SSL automatically.

### 7.4 Verify

```bash
curl -s https://lotify.ge/api/health | jq .
```

---

## Step 8: Rollback Plan

### Quick rollback (DNS)

```
; Point back to Vercel
lotify.ge.  60  IN  CNAME  cname.vercel-dns.com.
```

### Full rollback

1. Revert DNS to Vercel
2. Verify Vercel deployment is still active (Vercel keeps deployments)
3. Delete Coolify resource if abandoning migration

---

## Post-Migration Checklist

- [ ] All pages render correctly
- [ ] Authentication works (Supabase Auth)
- [ ] API routes respond correctly
- [ ] Image optimization works (sharp)
- [ ] ISR/SSR works correctly
- [ ] i18n routing works (ka/en)
- [ ] Cloudflare CDN caching works
- [ ] SSL certificate valid
- [ ] Response times acceptable
- [ ] Build/deploy pipeline works (push to main -> auto deploy)
- [ ] Preview deployments work for PRs (optional)
- [ ] DNS TTL restored to 3600
- [ ] Vercel project archived
- [ ] Cost savings confirmed
