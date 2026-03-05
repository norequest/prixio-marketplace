# Free Tier Limits Reference

Comprehensive free tier reference for all services relevant to Prixio LLC infrastructure.

Last updated: 2026-03-06

---

## Hosting

| Service | Free Tier | Limits | When to Upgrade |
|---------|-----------|--------|-----------------|
| Vercel | Hobby | 100GB bandwidth, 100 deploys/day, no commercial use | Team plan ($20/mo) at revenue or commercial use |
| Railway | Trial $5 | $5 credit, 500 execution hours/month | Immediately for production workloads |
| Hetzner | None | N/A | Start at CX22 (~4 EUR/mo) for production APIs |
| fly.io | Free | 3 shared-cpu-1x VMs, 160GB outbound bandwidth, 3GB persistent storage | When need dedicated CPU or >3 VMs |
| Render | Free | 750 hours/month, spins down after 15min inactivity, 100GB bandwidth | Production needs always-on (Starter $7/mo) |
| Cloudflare Pages | Free | Unlimited bandwidth, 500 builds/month, 1 build at a time | >500 builds/month or need concurrent builds |

### Hosting Notes

- **Vercel Hobby** is explicitly non-commercial. Prixio must upgrade to Team ($20/mo per member) once generating revenue. However, for pre-revenue development and staging, Hobby is acceptable.
- **Railway Trial** credit depletes fast with always-on services. Starter plan ($5/mo + usage) is the minimum for production. Developer plan ($5/mo) includes $5 of usage.
- **Hetzner** has no free tier but offers the best price-to-performance ratio in Europe. CX22 (2 vCPU, 4GB RAM, 40GB NVMe) at ~4 EUR/mo can run multiple Fastify APIs behind a reverse proxy.
- **fly.io** free tier is generous for small services. Good for edge workers or lightweight APIs.
- **Render** free tier spins down -- first request after sleep takes 30-60 seconds. Not suitable for production APIs.
- **Cloudflare Pages** is truly free with unlimited bandwidth -- best option for static sites and SPAs.

---

## Database & Storage

| Service | Free Tier | Limits | When to Upgrade |
|---------|-----------|--------|-----------------|
| Supabase | Free | 500MB database, 50 direct connections, 1GB file storage, 2GB bandwidth, 2 projects | >50 concurrent users or >500MB data |
| Upstash Redis | Free | 10,000 commands/day, 256MB max data size, 1 database | >10,000 daily cache operations |
| Cloudflare R2 | Free | 10GB storage, 1M Class A reads/month, 100K Class B writes/month, no egress fees | Rarely -- limits are very generous |
| Supabase Storage | Included | 1GB on free plan, 100GB on Pro ($25/mo) | >1GB total stored files |
| PlanetScale | Deprecated free | No longer offers free tier | Use Supabase or self-hosted PostgreSQL |
| Neon | Free | 0.5GB storage, 1 project, 100 compute hours/month | >0.5GB or need >1 database |

### Database Notes

- **Supabase Free** allows 2 projects -- enough for Lotify + Courio during development. The 500MB limit is the first constraint hit; typical e-commerce with images metadata reaches this in 3-6 months.
- **Supabase Pro** ($25/mo per project) is the next step. 8GB database, 100GB storage, 250GB bandwidth, daily backups. Consider this when approaching 500MB or needing point-in-time recovery.
- **Upstash Redis** free tier resets daily. 10K commands/day supports ~7 commands/minute sustained. Sufficient for session caching and rate limiting at low traffic.
- **Cloudflare R2** has zero egress fees, making it ideal for serving images and static assets. 10GB free covers significant media storage.

---

## APIs & Services

| Service | Free Tier | Limits | When to Upgrade |
|---------|-----------|--------|-----------------|
| Sentry | Free (Developer) | 5,000 errors/month, 1 user, 30-day retention | >5,000 errors (fix bugs first!) |
| Resend | Free | 100 emails/day, 3,000 emails/month, 1 domain | >100 emails/day or multiple domains |
| Google Maps Platform | $200/mo credit | ~28,000 Dynamic Maps loads, ~40,000 Static Maps, ~40,000 Geocoding | Rarely -- $200 credit is generous |
| Mapbox | Free | 50,000 map loads/month, 100,000 geocoding requests/month | >50,000 monthly map loads |
| FCM (Firebase Cloud Messaging) | Free | Unlimited push notifications | Never -- always free |
| UptimeRobot | Free | 50 monitors, 5-minute check interval | Need <5min checks ($7/mo for 1-min) |
| GitHub Actions | Free | 2,000 minutes/month (public repos), 500 minutes/month (private repos) | Heavy CI usage on private repos |
| Cloudflare DNS | Free | Unlimited DNS queries, free SSL | Never for basic DNS |
| Cloudflare CDN | Free | Unlimited bandwidth, basic WAF | Need advanced WAF rules or Workers |

### API Notes

- **Sentry Free** at 5K errors/month: if you are hitting this limit, the priority is fixing bugs, not upgrading the plan. Only upgrade if errors are expected (e.g., client-side noise from diverse browsers).
- **Resend Free** at 100 emails/day is sufficient for early-stage transactional email (order confirmations, password resets). Growth plan ($20/mo) adds 50K emails/month.
- **Google Maps** $200/mo credit covers most small-to-medium applications. Monitor usage in Google Cloud Console. Consider Mapbox as an alternative with a more predictable free tier.
- **Mapbox** 50K free map loads/month is generous. For Lotify auction item locations, this should last well into growth phase.
- **FCM** is completely free with no limits -- always use it for push notifications.

---

## Georgian-Specific Services

| Service | Free Tier | Pricing | Notes |
|---------|-----------|---------|-------|
| TBC Pay | No free tier | ~1.5% per transaction + minimum monthly fees | Required for GEL payments; no real alternative in Georgia |
| BOG iPay | No free tier | ~1.5-2% per transaction | Alternative to TBC Pay |
| Magti SMS | No free tier | ~0.03-0.05 GEL per SMS | Significantly cheaper than Twilio for Georgian numbers |
| Twilio (GE) | No free tier | ~0.15-0.20 GEL per SMS to Georgia | 3-5x more expensive than Magti for local SMS |
| .ge Domain | No free tier | ~30-50 GEL/year via NIC.ge registrars | Required for Georgian market presence |

### Georgian Service Notes

- **TBC Pay** is the de facto standard for online payments in Georgia. Integration is straightforward with their SDK. No realistic alternative for GEL card payments.
- **Magti SMS** is the recommended provider for Georgian phone numbers. Direct API, reliable delivery, and 3-5x cheaper than international providers like Twilio.
- **Georgian hosting** options are limited and expensive compared to European providers. Use Hetzner (Falkenstein/Helsinki) for lowest latency to Georgia while maintaining European pricing.

---

## Domain Registrars

| Provider | .com Price | .ge Price | Notes |
|----------|-----------|-----------|-------|
| Namecheap | ~$9/year (~25 GEL) | N/A | Best for international TLDs |
| Cloudflare Registrar | At-cost (~$9/year) | N/A | Cheapest for .com, no markup |
| NIC.ge Registrars | N/A | ~30-50 GEL/year | Only option for .ge domains |

---

## Cost Comparison: Free vs First Paid Tier

| Service | Free Cost | First Paid Tier | Monthly Jump |
|---------|-----------|----------------|--------------|
| Vercel | $0 | $20/user/mo (Team) | +$20 |
| Railway | $0 (trial) | $5/mo + usage (Developer) | +$5-15 |
| Supabase | $0 | $25/mo/project (Pro) | +$25 |
| Upstash Redis | $0 | $10/mo (Pay-as-you-go at scale) | +$10 |
| Sentry | $0 | $26/mo (Team) | +$26 |
| Resend | $0 | $20/mo (Growth) | +$20 |
| UptimeRobot | $0 | $7/mo (Pro) | +$7 |

---

## Recommended Free Stack for Pre-Revenue Prixio

| Layer | Service | Why |
|-------|---------|-----|
| Frontend hosting | Cloudflare Pages | Truly free, unlimited bandwidth, fast global CDN |
| API hosting | fly.io free tier | 3 free VMs, no spin-down |
| Database | Supabase Free (x2) | One for Lotify, one for Courio |
| Cache | Upstash Redis Free | 10K commands/day sufficient for dev/early users |
| Object storage | Cloudflare R2 Free | 10GB, zero egress |
| Email | Resend Free | 100/day covers early transactional email |
| Maps | Mapbox Free | 50K loads/month |
| Push notifications | FCM | Always free |
| Monitoring | Sentry Free + UptimeRobot Free | Error tracking + uptime |
| DNS | Cloudflare Free | Fast, free, with proxy/SSL |
| CI/CD | GitHub Actions Free | 2K min/month for public repos |
| SMS | Magti (pay-per-use) | Cheapest for Georgian numbers |
| Payments | TBC Pay | Only realistic option for GEL |

**Total monthly cost of recommended free stack: 0 GEL** (excluding SMS and payment processing fees which are per-transaction).
