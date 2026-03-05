# Platform Load Profiles

Traffic patterns, intensity characteristics, and key metrics for each Prixio platform.

---

## Lotify (Auction Platform)

### Traffic Distribution

| Segment   | % of Traffic | Intensity | Description                                        |
|-----------|--------------|-----------|----------------------------------------------------|
| Browsing  | 80%          | Low       | Catalog pages, search, item details, image loading |
| Bidding   | 15%          | HIGH      | WebSocket connections, real-time updates, rapid DB writes |
| Admin/Seller | 5%       | Low       | Listing management, dashboard, analytics           |

### Peak Patterns

- **Auction endings create thundering herd behavior** — the last 30 seconds of a
  popular auction can generate 10-50x the normal write rate as bidders compete.
- Peak hours: evenings (19:00-23:00 Tbilisi time), weekends see 2-3x weekday traffic.
- Flash auctions and promotional events can cause unpredictable spikes.

### Typical User Session

- **Browsing phase**: 5-15 minutes — catalog navigation, search, viewing item details
- **Bidding burst**: 1-3 minutes — rapid bid placement, watching real-time price updates
- **Post-auction**: 1-2 minutes — payment flow, confirmation

### Key Metrics to Monitor

| Metric                        | Why It Matters                                         |
|-------------------------------|--------------------------------------------------------|
| WebSocket connections         | Each bidder holds a persistent connection; 2x concurrent users typical |
| DB writes/sec during bidding  | Bid placement + bid history + price updates; 10x burst at auction end |
| Supabase Realtime channels    | One channel per active auction; fan-out to all watchers |
| Image CDN bandwidth           | Auction item images dominate bandwidth                 |
| Auth token refreshes/min      | Session keepalive during long browsing sessions        |

### Capacity Multipliers

- **WebSocket factor**: 2x concurrent users (each bidder subscribes to multiple auctions)
- **DB write burst**: 10x normal rate during auction endings (last 30 seconds)
- **Realtime fan-out**: Each bid update broadcasts to all auction watchers (N watchers per auction)

---

## Courio (Delivery Platform)

### Traffic Distribution

| Segment          | % of Traffic | Intensity  | Description                                       |
|------------------|--------------|------------|---------------------------------------------------|
| Consumer ordering| 40%          | Moderate   | Order placement, restaurant/store browsing, tracking page |
| Courier tracking | 30%          | Continuous | GPS updates every 5-15 seconds per active courier |
| Partner/merchant | 20%          | Low-Moderate | Order management, menu updates, analytics        |
| Admin operations | 10%          | Low        | Dispatch, support, system management              |

### Peak Patterns

- **Lunch rush**: 12:00-14:00 Tbilisi time — 2-3x baseline traffic
- **Evening peak**: 18:00-21:00 Tbilisi time — 3-4x baseline traffic (highest)
- **Weekend patterns**: Slightly higher baseline, flatter peaks
- **Weather events**: Rain/snow increases order volume by 30-50%

### Typical Flows

- **Consumer**: Browse (3-5 min) -> Order (1-2 min) -> Track (10-45 min, mostly idle with periodic checks)
- **Courier**: Continuous GPS streaming while active (4-8 hour shifts)
- **Merchant**: Order notification -> Preparation update -> Ready confirmation

### Key Metrics to Monitor

| Metric                    | Why It Matters                                          |
|---------------------------|---------------------------------------------------------|
| GPS writes/sec            | Active couriers * update frequency (every 5-15 sec)    |
| PostGIS queries/sec       | Proximity searches, route calculations, geofencing      |
| Push notifications/min    | Order updates, courier assignments, delivery alerts     |
| Map tile requests/sec     | Consumer tracking page, courier navigation              |
| Webhook deliveries/min    | Courio -> Lotify status updates (HMAC-SHA256 signed)    |

### Capacity Multipliers

- **GPS write factor**: active_couriers * (60 / update_interval_seconds) writes per minute
- **PostGIS query factor**: 2-3x GPS writes (each update triggers proximity checks)
- **Push notification burst**: Order state changes generate 2-3 notifications (customer + courier + merchant)

---

## Shared Load (Both Platforms)

### Supabase Auth

- Both platforms share a single Supabase Auth instance
- Token refresh every 60 minutes per active session
- Login/signup bursts during promotional events
- Estimated: 1 auth request per user per minute (token refresh + session validation)

### TBC Pay (Payment Processing)

- Lotify: Payment burst at auction end (winner pays immediately)
- Courio: Payment at order placement + courier payout batch
- Webhook processing: TBC Pay -> Platform confirmation
- Peak: Auction endings can trigger 10-50 simultaneous payment initiations

### Inter-Platform Webhooks

- Courio -> Lotify: Shipping status updates (HMAC-SHA256 signed)
- Frequency: 3-5 webhook calls per shipment lifecycle
- Dead letter queue handles failures with exponential backoff
- Volume scales linearly with order count
