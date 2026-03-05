---
name: infrastructure-advisor
description: >
  Compares hosting providers and recommends infrastructure tiers for Prixio LLC
  (Lotify + Courio). Considers cost, performance, Georgian-specific factors
  (latency to Tbilisi, reverse-charge VAT), and stage-appropriate recommendations.
  Triggers on: "hosting", "which provider", "recommend", "compare", "infrastructure",
  "Hetzner", "Railway", "Vercel", "fly.io", "AWS", "cloud", "what server".
allowed-tools: Bash, Read
---

# Infrastructure Advisor

Recommends and compares cloud infrastructure for Prixio LLC projects (Lotify and Courio).

## How to Use

**Ask a question:**
- "Which provider should I use for Lotify?"
- "Compare Hetzner vs Railway for my stack"
- "What's the cheapest way to host Courio API?"
- "Recommend infrastructure for our MVP stage"

**Or request a specific comparison:**
- "Compare all providers for Fastify 5 backend"
- "What will hosting cost at 10k users?"

The advisor considers your exact stack (Fastify 5, Next.js 15, Supabase, pnpm monorepo) and Georgian-specific factors like latency to Tbilisi and reverse-charge VAT.

## Provider Comparison Matrix

| Provider         | Best For                | Min Cost (GEL/mo) | Latency to Tbilisi | Free Tier | Docker | Auto-scale |
|------------------|-------------------------|--------------------|---------------------|-----------|--------|------------|
| Railway          | API deployment, MVP     | 0 (trial) / ~14    | ~80ms (US) / ~50ms (EU) | $5 trial credit | Yes | Yes |
| Hetzner Cloud    | Cost-effective VPS      | ~7                 | ~40ms (Finland)     | No        | Yes    | Manual     |
| Hetzner Dedicated| High-traffic production | ~100               | ~40ms (Finland)     | No        | Yes    | No         |
| fly.io           | Edge compute, low latency| 0 / ~16           | ~35ms (Warsaw)      | 3 free VMs | Yes  | Yes        |
| Vercel           | Next.js frontend, SSR   | 0 / ~55            | Edge (global)       | Yes (generous) | No | Yes    |
| AWS Lightsail    | Simple VPS              | ~10                | ~60ms (Frankfurt)   | 3-mo free | Yes    | Manual     |
| DigitalOcean     | Balanced VPS            | ~11                | ~55ms (Frankfurt)   | $200 credit (60d) | Yes | Yes |
| Render           | Simple deployments      | 0 / ~19            | ~80ms (Frankfurt)   | Yes       | Yes    | Yes        |
| Coolify (self-hosted) | Full control on Hetzner | ~7 (Hetzner cost) | ~40ms (Finland) | N/A   | Yes    | Manual     |

**Note:** All GEL costs are approximate at ~2.7 GEL/USD. Add 18% for reverse-charge VAT on all foreign providers.

## Evaluation Criteria

1. **Cost (GEL/month)** -- Total monthly spend including compute, storage, bandwidth, and managed services. All foreign services incur 18% reverse-charge VAT.
2. **Latency to Tbilisi** -- Round-trip time from provider's nearest datacenter to Tbilisi, Georgia. Critical for TBC Pay webhook response times and real-time auction bidding.
3. **Free Tier** -- Availability and generosity of free tier for MVP/development stage.
4. **Managed DB Support** -- Whether the provider offers managed PostgreSQL (though Prixio uses Supabase as primary DB).
5. **Docker Support** -- Ability to deploy Docker containers (required for Fastify 5 API).
6. **Auto-scaling** -- Automatic horizontal or vertical scaling for traffic spikes (auction endings, delivery surges).

## Stage Recommendations

### MVP Stage (0-1k users, current)

**Recommended stack: Free tiers + Supabase Free**

| Service        | Provider       | Cost/mo | Notes                              |
|----------------|----------------|---------|------------------------------------|
| Lotify Frontend| Vercel Free    | 0 GEL   | Next.js 15 SSR, generous free tier |
| Lotify API     | Railway (trial)| 0 GEL   | $5 credit, Fastify 5 container     |
| Courio API     | Railway (trial)| 0 GEL   | Already deployed here              |
| Database       | Supabase Free  | 0 GEL   | 500MB, 2 projects                  |
| Redis/Cache    | Upstash Free   | 0 GEL   | 10k commands/day                   |
| **Total**      |                | **0 GEL** | Perfect for validation            |

### Growth Stage (1k-10k users)

**Recommended stack: Managed services with predictable pricing**

| Service        | Provider        | Cost/mo   | Notes                              |
|----------------|-----------------|-----------|-------------------------------------|
| Lotify Frontend| Vercel Pro      | ~55 GEL   | More bandwidth, analytics           |
| Lotify API     | Railway Pro     | ~28-55 GEL| Auto-sleep, usage-based             |
| Courio API     | Railway Pro     | ~28-55 GEL| WebSocket support for tracking      |
| Database       | Supabase Pro    | ~68 GEL   | 8GB, daily backups, no pause        |
| Redis/Cache    | Upstash Pro     | ~14-27 GEL| Higher limits                       |
| **Total**      |                 | **~195-260 GEL** | + 18% VAT = ~230-307 GEL    |

### Scale Stage (10k+ users)

**Recommended stack: Hetzner dedicated + Coolify for cost control**

| Service        | Provider              | Cost/mo    | Notes                             |
|----------------|-----------------------|------------|-----------------------------------|
| Lotify Frontend| Vercel Pro / self-host| ~55-0 GEL  | Or Coolify + Hetzner              |
| API Servers    | Hetzner Dedicated     | ~135-270 GEL| AX41: 64GB RAM, 512GB NVMe      |
| Orchestration  | Coolify (self-hosted) | 0 GEL      | On Hetzner, replaces Railway      |
| Database       | Supabase Pro / Team   | ~68-540 GEL| Or self-hosted Supabase on Hetzner|
| Redis/Cache    | Self-hosted Redis     | 0 GEL      | On Hetzner dedicated server       |
| CDN            | Cloudflare Free/Pro   | 0-55 GEL   | Global edge caching               |
| **Total**      |                       | **~260-865 GEL** | + 18% VAT where applicable  |

## Georgian Tax Note

All foreign cloud services are subject to **18% reverse-charge VAT** under Georgian tax law. As Prixio LLC operates under the Estonian model (profit distribution tax), this VAT is an additional cost on every invoice from foreign providers. This does not apply to Prixio's own self-hosted infrastructure on owned hardware.

See `references/georgian-infra.md` for detailed tax implications and `references/provider-matrix.md` for the full provider comparison.

## Reference Files

- `references/provider-matrix.md` -- Detailed provider comparison with pros/cons
- `references/georgian-infra.md` -- Georgian-specific infrastructure considerations
- `references/stack-requirements.md` -- Lotify and Courio infrastructure requirements
