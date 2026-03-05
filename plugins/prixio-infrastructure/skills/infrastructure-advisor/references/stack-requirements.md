# Stack Requirements: Lotify + Courio

What Lotify and Courio specifically need from infrastructure, organized by project and shared requirements.

---

## Lotify (Georgian Online Auction Platform)

### Compute Requirements

- **Fastify 5 API server:** Long-running Node.js process. Requires Docker or native Node.js hosting. Cannot run on serverless-only platforms (rules out Vercel for API).
- **WebSocket support:** Critical for real-time auction bidding. Server must maintain persistent WebSocket connections. Supabase Realtime handles most of this, but the API server needs to broadcast bid updates and manage auction state.
- **Image processing:** Lotify uses Gemini Vision API for auction item image analysis (condition assessment, category detection). The API calls go to Google's servers, but image upload/preprocessing requires adequate CPU and memory on the API server.
- **SSR (Server-Side Rendering):** Next.js 15 with App Router. Vercel is the optimal host for SSR due to first-party support, Edge Runtime, and ISR (Incremental Static Regeneration).

### Database Requirements

- **Supabase (PostgreSQL):** Primary database with Row-Level Security (RLS) on all tables.
- **Supabase Realtime:** Powers real-time auction bidding UI updates. Clients subscribe to auction channels via Supabase Realtime. Requires stable WebSocket connections from client to Supabase.
- **Supabase Auth:** User authentication (email, phone, social). Hosted by Supabase, no infra requirement from Prixio beyond API key configuration.
- **Upstash Redis:** Used for caching auction data, rate limiting, and session management. Serverless Redis -- accessed over HTTPS, no persistent connection needed.

### Traffic Patterns

- **Spike-driven:** Auction endings cause traffic spikes (final 30 seconds of bidding). Infrastructure must handle 10-50x normal traffic for short bursts.
- **Image-heavy:** Auction listings include multiple high-resolution images. CDN is essential for image delivery.
- **Read-heavy:** Most users browse auctions (read). Write operations (bids, listings) are a small fraction of total requests.

### Specific Infrastructure Needs

| Requirement              | Solution                          | Provider Dependency          |
|--------------------------|-----------------------------------|------------------------------|
| WebSocket (bidding)      | Supabase Realtime + Fastify WS   | Supabase + API host          |
| Image CDN                | Supabase Storage + Cloudflare    | Supabase + CDN               |
| SSR / Edge rendering     | Next.js 15 on Vercel             | Vercel                       |
| Image analysis           | Gemini Vision API                | Google Cloud (API only)      |
| Caching / Rate limiting  | Upstash Redis                    | Upstash                      |
| Payment processing       | TBC Pay                          | TBC Bank (Georgian)          |
| Search                   | PostgreSQL full-text + pg_trgm   | Supabase                     |
| Email notifications      | Resend or similar                | Email provider               |

---

## Courio (Delivery Platform for Georgia)

### Compute Requirements

- **Fastify 5 API server:** Long-running process handling order management, driver tracking, and partner integrations. Already deployed on Railway.
- **Real-time GPS tracking:** Drivers send GPS coordinates every 5-15 seconds. API must handle high-frequency writes from potentially hundreds of concurrent drivers.
- **Webhook processing:** Receives webhooks from partners (Lotify) and sends status update webhooks back. HMAC-SHA256 signed. Must process within 5-second timeout.
- **Background jobs:** Order assignment algorithms, route optimization, notification dispatching. Need reliable background task execution.

### Database Requirements

- **Supabase (PostgreSQL) with PostGIS:** Critical for geospatial queries -- finding nearest available driver, calculating delivery distances, geo-fencing delivery zones.
- **PostGIS functions:** `ST_Distance`, `ST_DWithin`, `ST_MakePoint`, `ST_Transform`. These are CPU-intensive and benefit from fast storage (NVMe).
- **Supabase Realtime:** Powers real-time tracking UI (customer sees driver location update in real-time).
- **Dead letter queue:** Failed webhook deliveries are stored for retry. PostgreSQL-based queue with exponential backoff.

### Traffic Patterns

- **Sustained throughput:** Unlike Lotify's spiky auction traffic, Courio has more consistent traffic during business hours (9am-10pm Georgian time).
- **Write-heavy:** GPS tracking generates continuous writes. Order status updates are frequent.
- **Geospatial query-heavy:** Every order assignment requires spatial queries against available drivers.

### Specific Infrastructure Needs

| Requirement              | Solution                          | Provider Dependency          |
|--------------------------|-----------------------------------|------------------------------|
| GPS tracking ingestion   | Fastify 5 API + Supabase         | Railway + Supabase           |
| PostGIS geospatial       | Supabase PostgreSQL + PostGIS    | Supabase                     |
| Real-time tracking UI    | Supabase Realtime                | Supabase                     |
| Maps / Routing           | Mapbox or Google Maps API        | Mapbox/Google (API only)     |
| Push notifications       | Firebase Cloud Messaging (FCM)   | Google (API only)            |
| SMS notifications        | Magti SMS / Twilio               | Magti / Twilio               |
| Partner webhooks         | HMAC-SHA256 signed endpoints     | API host (Railway)           |
| Payment processing       | TBC Pay                          | TBC Bank (Georgian)          |
| Background jobs          | BullMQ or pg-boss on Fastify     | API host                     |

---

## Shared Requirements (Both Projects)

### Authentication and Security

- **Supabase Auth:** Both projects use Supabase Auth for user authentication. No additional auth infrastructure needed.
- **RLS (Row-Level Security):** All tables in both projects use RLS. Enforced at the database level by Supabase.
- **SECURITY DEFINER functions:** All PostgreSQL functions use `SECURITY DEFINER` with `SET search_path = ''` for security. This is a Supabase-side configuration.
- **HTTPS everywhere:** All API endpoints must be HTTPS with valid TLS certificates. All modern hosting providers handle this automatically.

### Payment Processing

- **TBC Pay:** Both projects use TBC Pay for payment processing.
- **Webhook requirements:** Public HTTPS endpoint with static IP (preferred). Must respond within 5 seconds. HMAC signature verification on incoming webhooks.
- **Low latency to TBC:** TBC Bank APIs are hosted in Georgia. European hosting (Hetzner Helsinki ~40ms, Frankfurt ~55ms) provides acceptable latency.

### Build and Deployment

- **pnpm monorepo + Turborepo:** Both projects use pnpm workspaces with Turborepo for build orchestration.
- **Build requirements:**
  - Node.js 20+ (ESM support required)
  - pnpm 9+ (workspace protocol)
  - Turborepo for cached builds
  - TypeScript 5.x compilation
- **Docker support:** API servers (Fastify 5) are deployed as Docker containers. Dockerfile must support pnpm workspace pruning.
- **CI/CD:** GitHub Actions for testing and building. Deployment triggered by push to main branch.

### Internationalization

- **Languages:** Georgian (ka) + English (en) for both projects.
- **Currency:** GEL (Georgian Lari, symbol: lari). All prices stored as integers (tetri, 1/100 GEL) in the database.
- **Encoding:** UTF-8 for Georgian script (Mkhedruli). No special infrastructure requirements.

### Monitoring and Observability

- **Logging:** Structured JSON logs from Fastify 5. Need centralized log aggregation.
- **Options:**
  - Vercel Analytics (for Next.js frontend)
  - Railway metrics (for API on Railway)
  - Better Stack (Logtail) -- free tier available
  - Sentry for error tracking (free tier: 5k events/mo)
- **Uptime monitoring:** Essential for payment webhook endpoints. Recommend Better Uptime or UptimeRobot (free tier).

---

## Infrastructure Architecture Overview

```
                        Georgian Users
                             |
                      [Cloudflare CDN]
                        /          \
              [Vercel Edge]    [API Server(s)]
              Next.js SSR      Fastify 5
              Lotify Web       Lotify API + Courio API
                    \              /
                   [Supabase Cloud]
                   PostgreSQL + PostGIS
                   Auth, Realtime, Storage
                        |
                  [External APIs]
                  TBC Pay, Gemini Vision,
                  Mapbox, FCM, Magti SMS
```

### Minimum Viable Infrastructure

| Component           | Service          | Monthly Cost |
|---------------------|------------------|--------------|
| Lotify Frontend     | Vercel Free      | 0 GEL        |
| Lotify API          | Railway Trial    | 0 GEL        |
| Courio API          | Railway Trial    | 0 GEL        |
| Database (both)     | Supabase Free x2 | 0 GEL       |
| Cache               | Upstash Free     | 0 GEL        |
| CDN                 | Cloudflare Free  | 0 GEL        |
| Error Tracking      | Sentry Free      | 0 GEL        |
| Uptime Monitoring   | UptimeRobot Free | 0 GEL        |
| **Total MVP**       |                  | **0 GEL**    |

### Production Infrastructure (Growth Stage)

| Component           | Service          | Monthly Cost  |
|---------------------|------------------|---------------|
| Lotify Frontend     | Vercel Pro       | ~55 GEL       |
| Lotify API          | Railway Pro      | ~40 GEL       |
| Courio API          | Railway Pro      | ~40 GEL       |
| Database (both)     | Supabase Pro x2  | ~136 GEL      |
| Cache               | Upstash Pro      | ~20 GEL       |
| CDN                 | Cloudflare Free  | 0 GEL         |
| Error Tracking      | Sentry Team      | ~70 GEL       |
| Uptime Monitoring   | Better Stack     | 0-27 GEL      |
| **Total Growth**    |                  | **~360-390 GEL** |
| **+ 18% VAT**       |                  | **~425-460 GEL** |
