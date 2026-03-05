# Infrastructure Tier Benchmarks

Capacity limits, costs, and bottleneck analysis for each infrastructure tier.

---

## Tier Overview

| Tier       | Server                          | Concurrent Users | Requests/sec | DB Connections | WebSocket Conns | Monthly Cost (GEL) |
|------------|---------------------------------|------------------|--------------|----------------|-----------------|---------------------|
| Free       | Supabase Free + Railway Free    | 50               | 10           | 50             | 200             | 0                   |
| Starter    | Hetzner CX22 + Supabase Pro    | 500              | 100          | 200            | 2,000           | ~200                |
| Growth     | Hetzner CX32 + Supabase Pro    | 2,000            | 500          | 500            | 10,000          | ~500                |
| Scale      | Hetzner CX42 + Supabase Team   | 10,000           | 2,000        | 1,000          | 50,000          | ~1,500              |
| Enterprise | Multi-server + dedicated DB     | 50,000+          | 10,000+      | 5,000+         | 200,000+        | ~5,000+             |

---

## Detailed Tier Specifications

### Free Tier

- **Server**: Supabase Free (500 MB DB, 1 GB bandwidth) + Railway Free (500 hours/month)
- **Best for**: Development, demos, < 50 concurrent users
- **Limits**: 50 DB connections, 200 Realtime connections, 2 GB storage
- **First bottleneck**: DB connections (hit at ~30-40 concurrent users with connection pooling)

### Starter Tier

- **Server**: Hetzner CX22 (2 vCPU, 4 GB RAM, 40 GB SSD) + Supabase Pro ($25/mo)
- **Best for**: Soft launch, early users, 100-500 concurrent
- **Limits**: 200 DB connections (PgBouncer), 2,000 Realtime, 8 GB DB storage
- **First bottleneck**: WebSocket connections for Lotify (bidding); GPS write throughput for Courio
- **Notes**: PgBouncer transaction mode required; consider connection pooling at app level

### Growth Tier

- **Server**: Hetzner CX32 (4 vCPU, 8 GB RAM, 80 GB SSD) + Supabase Pro (compute add-on)
- **Best for**: Established user base, 500-2,000 concurrent
- **Limits**: 500 DB connections, 10,000 Realtime, 50 GB storage
- **First bottleneck**: DB write throughput during Lotify auction endings; PostGIS query latency under load for Courio
- **Notes**: Consider read replicas for Lotify browsing queries; Redis cache for hot auction data

### Scale Tier

- **Server**: Hetzner CX42 (8 vCPU, 16 GB RAM, 160 GB SSD) + Supabase Team
- **Best for**: High traffic, 2,000-10,000 concurrent
- **Limits**: 1,000 DB connections, 50,000 Realtime, 100 GB storage
- **First bottleneck**: Single-server CPU during combined peak (auction ending + delivery rush); Supabase Realtime fan-out latency
- **Notes**: Must implement auction-end queue (debounce bids); GPS write batching for Courio; CDN mandatory for images

### Enterprise Tier

- **Server**: Multiple Hetzner servers (load balanced) + dedicated PostgreSQL cluster
- **Best for**: 10,000+ concurrent users
- **Limits**: Horizontally scalable
- **First bottleneck**: Architectural — requires service decomposition, event-driven patterns
- **Notes**: Dedicated DB per platform recommended; Kafka/NATS for inter-service communication; geographic distribution for delivery tracking

---

## Bottleneck Progression by Platform

### Lotify Bottleneck Order

1. **DB connections** (Free tier) — Pooling exhaustion with real-time subscriptions
2. **WebSocket connections** (Starter) — Bidding activity creates 2x user count in connections
3. **DB write throughput** (Growth) — Auction-end thundering herd saturates write capacity
4. **CPU** (Scale) — Concurrent auction endings + bid validation + real-time fan-out
5. **Architecture** (Enterprise) — Single-server model cannot scale further

### Courio Bottleneck Order

1. **DB connections** (Free tier) — GPS streaming holds connections open
2. **GPS write throughput** (Starter) — Continuous inserts from active couriers
3. **PostGIS query latency** (Growth) — Proximity searches slow under concurrent load
4. **Push notification throughput** (Scale) — Notification fan-out during peak delivery hours
5. **Architecture** (Enterprise) — GPS ingestion needs dedicated pipeline

---

## Cost Breakdown (GEL, approximate)

| Component              | Free | Starter | Growth | Scale  | Enterprise |
|------------------------|------|---------|--------|--------|------------|
| Server (Hetzner)       | 0    | ~60     | ~120   | ~250   | ~1,500+    |
| Supabase               | 0    | ~70     | ~170   | ~500   | N/A        |
| CDN / Bandwidth        | 0    | ~20     | ~60    | ~200   | ~500+      |
| Domain / SSL           | 0    | ~15     | ~15    | ~15    | ~15        |
| Monitoring             | 0    | 0       | ~30    | ~100   | ~300+      |
| Backups                | 0    | ~15     | ~30    | ~100   | ~300+      |
| Redis (if needed)      | 0    | 0       | ~50    | ~150   | ~500+      |
| **Total**              | **0**| **~200**| **~500**| **~1,500** | **~5,000+** |

*Note: GEL amounts based on approximate exchange rate. Actual costs vary with usage.*
