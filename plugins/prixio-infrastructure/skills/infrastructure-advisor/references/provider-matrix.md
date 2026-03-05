# Provider Comparison Matrix

Detailed comparison of hosting providers for Prixio LLC's stack: Fastify 5 + Next.js 15 + Supabase + pnpm monorepo.

All costs in GEL (approximate at ~2.7 GEL/USD). Add 18% reverse-charge VAT to all foreign providers.

---

## Railway

| Attribute        | Details                                                |
|------------------|--------------------------------------------------------|
| Type             | PaaS (container-based)                                 |
| Managed DB       | Yes (PostgreSQL, MySQL, Redis, MongoDB)                |
| CDN              | No (use Cloudflare in front)                           |
| Free Tier        | $5 trial credit, then usage-based                      |
| Min Cost (GEL/mo)| ~14 (Hobby) / ~55 (Pro)                               |
| Latency Tbilisi  | ~80ms (US-West) / ~50ms (EU, if available)             |
| Docker           | Yes (Dockerfile or Nixpacks auto-detect)               |
| Auto-scale       | Yes (usage-based, horizontal replicas on Pro)          |

**Pros:**
- Courio API is already deployed here -- proven track record
- Excellent monorepo support (auto-detects pnpm workspaces)
- Simple Dockerfile deployments for Fastify 5
- Built-in PostgreSQL and Redis (useful for non-Supabase needs)
- Usage-based pricing means you only pay for what you use
- Good GitHub integration with preview deployments

**Cons:**
- No EU region guaranteed (depends on availability)
- US-based default adds ~30ms vs European providers
- Trial credit burns quickly with always-on services
- No built-in CDN or edge functions
- WebSocket support exists but less battle-tested than fly.io

---

## Hetzner Cloud

| Attribute        | Details                                                |
|------------------|--------------------------------------------------------|
| Type             | IaaS (VPS)                                             |
| Managed DB       | No (DIY or use managed add-ons)                        |
| CDN              | No                                                     |
| Free Tier        | No                                                     |
| Min Cost (GEL/mo)| ~7 (CX22: 2 vCPU, 4GB RAM)                            |
| Latency Tbilisi  | ~40ms (Helsinki, Finland)                              |
| Docker           | Yes (full root access)                                 |
| Auto-scale       | Manual (API-driven scaling possible)                   |

**Pros:**
- Best price-to-performance ratio in Europe
- Helsinki datacenter has lowest latency to Tbilisi (~40ms)
- Full root access -- run anything (Docker, Coolify, K3s)
- Predictable pricing, no surprise bills
- Excellent for Coolify self-hosted PaaS setup
- ARM instances (CAX) even cheaper for compatible workloads

**Cons:**
- No managed services -- you manage everything yourself
- No auto-scaling out of the box (need to script it)
- No built-in CI/CD or GitHub integration
- Requires DevOps knowledge for production setup
- No free tier (but extremely cheap entry point)

---

## Hetzner Dedicated

| Attribute        | Details                                                |
|------------------|--------------------------------------------------------|
| Type             | Bare metal dedicated server                            |
| Managed DB       | No                                                     |
| CDN              | No                                                     |
| Free Tier        | No                                                     |
| Min Cost (GEL/mo)| ~100 (AX41: AMD Ryzen 5, 64GB, 512GB NVMe)            |
| Latency Tbilisi  | ~40ms (Finland)                                        |
| Docker           | Yes (full root access)                                 |
| Auto-scale       | No (fixed hardware)                                    |

**Pros:**
- Unbeatable price for dedicated hardware
- Can run entire Prixio stack on one server (Coolify + Docker)
- No noisy neighbor issues
- Full NVMe storage for PostGIS and image processing
- 64GB RAM handles Supabase self-hosted + Redis + API servers
- Helsinki location = lowest latency to Tbilisi

**Cons:**
- Single point of failure without redundancy setup
- 1-48 hour provisioning time
- Hardware failures require Hetzner intervention
- No auto-scaling (need multiple servers + load balancer)
- Requires significant DevOps expertise

---

## fly.io

| Attribute        | Details                                                |
|------------------|--------------------------------------------------------|
| Type             | PaaS (microVM-based, edge compute)                     |
| Managed DB       | Yes (Fly Postgres, LiteFS for SQLite)                  |
| CDN              | Built-in (anycast, global edge)                        |
| Free Tier        | 3 shared VMs, 160GB bandwidth                          |
| Min Cost (GEL/mo)| 0 (free) / ~16 (with dedicated CPU)                    |
| Latency Tbilisi  | ~35ms (Warsaw, Poland -- closest PoP)                  |
| Docker           | Yes (Dockerfile required)                              |
| Auto-scale       | Yes (scale to zero, auto-scale on demand)              |

**Pros:**
- Lowest latency to Tbilisi among PaaS providers (Warsaw PoP)
- Excellent WebSocket support -- ideal for Lotify real-time bidding
- Scale-to-zero saves money during low-traffic periods
- Built-in anycast networking and TLS
- Good for globally distributed apps
- Free tier includes 3 VMs -- enough for MVP

**Cons:**
- Fly Postgres is not fully managed (you manage failover)
- Pricing can be unpredictable with many small machines
- CLI-first workflow, less polished dashboard than Railway
- Occasional reliability issues reported by community
- Volume storage is region-locked
- Less intuitive monorepo deployment than Railway

---

## Vercel

| Attribute        | Details                                                |
|------------------|--------------------------------------------------------|
| Type             | PaaS (serverless, edge-optimized for Next.js)          |
| Managed DB       | Vercel Postgres, KV, Blob (add-ons)                   |
| CDN              | Built-in (global edge network)                         |
| Free Tier        | Yes (generous: 100GB bandwidth, serverless functions)  |
| Min Cost (GEL/mo)| 0 (Hobby) / ~55 (Pro)                                 |
| Latency Tbilisi  | Edge-optimized (nearest PoP, likely Istanbul ~15ms)    |
| Docker           | No (serverless functions only)                         |
| Auto-scale       | Yes (automatic, serverless)                            |

**Pros:**
- First-class Next.js 15 support (made by same company)
- Lotify frontend already targets Vercel for SSR
- Global edge network delivers lowest frontend latency
- Generous free tier for hobby/MVP projects
- Automatic preview deployments per PR
- Built-in analytics and Web Vitals monitoring
- Excellent pnpm monorepo support with Turborepo

**Cons:**
- Cannot run Fastify 5 (no long-running processes or Docker)
- Only suitable for frontend/serverless, not API backends
- Pro plan ($20/mo) needed for commercial use
- Serverless cold starts can affect API response times
- Vendor lock-in with Vercel-specific features
- Add-on databases (Postgres, KV) are expensive vs Supabase

---

## AWS Lightsail

| Attribute        | Details                                                |
|------------------|--------------------------------------------------------|
| Type             | Simplified VPS (AWS ecosystem)                         |
| Managed DB       | Yes (managed PostgreSQL, MySQL)                        |
| CDN              | CloudFront integration available                       |
| Free Tier        | 3 months free (smallest instance)                      |
| Min Cost (GEL/mo)| ~10 (512MB) / ~27 (2GB)                               |
| Latency Tbilisi  | ~60ms (eu-central-1, Frankfurt)                        |
| Docker           | Yes (full root access on VPS)                          |
| Auto-scale       | Manual (but can upgrade to full EC2)                   |

**Pros:**
- Gateway to full AWS ecosystem if needed later
- Managed database option available
- Predictable pricing (unlike standard AWS)
- CloudFront CDN integration
- Snapshots and backups included
- 3-month free tier for testing

**Cons:**
- More expensive than Hetzner for equivalent specs
- Higher latency to Tbilisi than Hetzner or fly.io
- AWS console complexity even for Lightsail
- Limited compared to full EC2/ECS
- Bandwidth overage charges possible
- Frankfurt region, not the closest to Georgia

---

## DigitalOcean

| Attribute        | Details                                                |
|------------------|--------------------------------------------------------|
| Type             | IaaS/PaaS (Droplets + App Platform)                   |
| Managed DB       | Yes (PostgreSQL, MySQL, Redis, MongoDB)                |
| CDN              | Spaces CDN (S3-compatible)                             |
| Free Tier        | $200 credit for 60 days                                |
| Min Cost (GEL/mo)| ~11 (1 vCPU, 1GB) / ~16 (1 vCPU, 2GB)                |
| Latency Tbilisi  | ~55ms (Frankfurt)                                      |
| Docker           | Yes (Droplets: full access; App Platform: Dockerfile)  |
| Auto-scale       | Yes (App Platform auto-scales)                         |

**Pros:**
- Good balance of simplicity and power
- App Platform supports Docker and monorepos
- Managed PostgreSQL with connection pooling
- Spaces (S3-compatible) for image storage
- $200 trial credit is generous for MVP testing
- Good documentation and community

**Cons:**
- More expensive than Hetzner for equivalent VPS specs
- App Platform pricing can escalate quickly
- Frankfurt region only (no closer PoP to Georgia)
- Managed DB pricing adds up fast
- Less competitive than Railway for simple deployments

---

## Render

| Attribute        | Details                                                |
|------------------|--------------------------------------------------------|
| Type             | PaaS (container-based, Heroku alternative)             |
| Managed DB       | Yes (PostgreSQL with auto-backups)                     |
| CDN              | Built-in (Cloudflare-backed)                           |
| Free Tier        | Yes (750 hours/mo, spins down on inactivity)           |
| Min Cost (GEL/mo)| 0 (Free) / ~19 (Starter)                              |
| Latency Tbilisi  | ~80ms (Frankfurt)                                      |
| Docker           | Yes (Dockerfile support)                               |
| Auto-scale       | Yes (on paid plans)                                    |

**Pros:**
- Simple Heroku-like experience
- Free PostgreSQL database (90-day limit)
- Auto-deploy from GitHub
- Built-in cron jobs and background workers
- Good for simple Fastify 5 deployments

**Cons:**
- Free tier spins down on inactivity (30s cold start)
- Higher latency to Tbilisi than Hetzner/fly.io
- Less mature than Railway for monorepo support
- Free database expires after 90 days
- Limited WebSocket support on free tier
- Slower builds compared to Railway

---

## Coolify (Self-hosted on Hetzner)

| Attribute        | Details                                                |
|------------------|--------------------------------------------------------|
| Type             | Self-hosted PaaS (open-source, runs on any VPS)        |
| Managed DB       | Self-managed (one-click PostgreSQL, Redis, etc.)       |
| CDN              | No (use Cloudflare in front)                           |
| Free Tier        | N/A (software is free; pay only for VPS)               |
| Min Cost (GEL/mo)| ~7 (Hetzner CX22 cost only)                           |
| Latency Tbilisi  | ~40ms (Hetzner Finland)                                |
| Docker           | Yes (Docker Compose native support)                    |
| Auto-scale       | Manual (Coolify manages containers, not auto-scale)    |

**Pros:**
- Railway/Vercel-like UI on your own hardware
- Best cost efficiency: Hetzner pricing + zero platform markup
- Full control over data, logs, and configuration
- One-click deployments for Docker, Docker Compose, Nixpacks
- Built-in SSL, reverse proxy (Traefik/Caddy), monitoring
- No vendor lock-in -- standard Docker deployments
- GitHub/GitLab webhook deployments
- Helsinki = lowest latency to Tbilisi

**Cons:**
- You are the SRE -- responsible for uptime, backups, security
- Initial setup takes 1-2 hours
- No auto-scaling (manual container management)
- Coolify itself needs resources (~512MB RAM overhead)
- Less polished than Railway/Vercel dashboards
- Single server = single point of failure (unless you add nodes)
- Community support only (no enterprise SLA)

---

## Summary: Best Provider by Use Case

| Use Case                        | Recommended Provider        |
|---------------------------------|-----------------------------|
| Lotify Frontend (Next.js SSR)   | Vercel                      |
| Lotify API (Fastify 5)          | Railway (MVP) / fly.io (Growth) |
| Courio API (Fastify 5)          | Railway (current)           |
| Real-time Bidding (WebSockets)  | fly.io                      |
| PostGIS / Geospatial            | Supabase (managed) or Hetzner (self-hosted) |
| Image Processing                | Hetzner Cloud (CPU-heavy tasks) |
| Cost Optimization at Scale      | Hetzner Dedicated + Coolify |
| Lowest Latency to Tbilisi       | fly.io (Warsaw) or Hetzner (Helsinki) |
