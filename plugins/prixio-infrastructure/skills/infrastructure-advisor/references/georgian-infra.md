# Georgian-Specific Infrastructure Considerations

Infrastructure planning for Prixio LLC, a Georgian company (Prixio LLC / shps priqsio, s/k 405842842) operating Lotify and Courio from Georgia.

---

## Reverse-Charge VAT (18%) on Foreign Cloud Services

### Mechanism

Under Georgian tax law, when a Georgian company purchases digital services from a foreign (non-Georgian) provider, the Georgian company must self-assess and pay **18% VAT** (reverse-charge mechanism).

**How it works:**

1. Foreign cloud provider (e.g., Railway, Vercel, Hetzner) invoices Prixio LLC without Georgian VAT.
2. Prixio LLC must declare this as an import of services on the monthly VAT return.
3. Prixio LLC pays 18% VAT on the invoice amount to the Georgian Revenue Service.
4. If Prixio were VAT-registered, it could offset this as input VAT. However, Prixio currently operates under the **Estonian model** (profit distribution tax) and is **not VAT-registered**.
5. Since Prixio is not VAT-registered, the 18% becomes a pure cost increase.

**Practical impact:**

| Monthly Cloud Spend | Without VAT | With 18% VAT | VAT Cost |
|---------------------|-------------|---------------|----------|
| $50 (~135 GEL)      | 135 GEL     | 159 GEL       | 24 GEL   |
| $200 (~540 GEL)     | 540 GEL     | 637 GEL       | 97 GEL   |
| $500 (~1,350 GEL)   | 1,350 GEL   | 1,593 GEL     | 243 GEL  |

**When VAT registration makes sense:** If Prixio starts charging customers VAT (required above 100,000 GEL annual revenue threshold), input VAT from cloud services can be offset. Until then, the 18% is an unavoidable cost adder.

### Filing Requirements

- Monthly VAT declaration even if not VAT-registered (for reverse-charge)
- Payment due by the 15th of the following month
- Declare under service code for "electronically supplied services"
- Currency conversion at the NBG (National Bank of Georgia) rate on the invoice date

---

## Datacenter Proximity to Georgia

### No Georgian Cloud Providers

Georgia does not have major cloud providers with public IaaS/PaaS offerings. The closest datacenters by latency:

| Location          | Provider(s)                    | Latency to Tbilisi | Notes                          |
|-------------------|--------------------------------|---------------------|--------------------------------|
| Helsinki, Finland | Hetzner                        | ~40ms               | Best price/latency ratio       |
| Warsaw, Poland    | fly.io, OVH                   | ~35ms               | fly.io's closest PoP           |
| Frankfurt, Germany| AWS, DO, Hetzner, Azure, GCP  | ~50-60ms            | Most providers' EU region      |
| Istanbul, Turkey  | Vercel Edge, Cloudflare        | ~15-20ms            | CDN/Edge only, no compute      |
| Bucharest, Romania| OVH, some CDNs                | ~30ms               | Limited provider options        |
| Moscow, Russia    | Yandex Cloud, VK Cloud        | ~25ms               | Not recommended (sanctions, legal risk) |

**Recommendation:** Hetzner Helsinki for compute, Cloudflare/Vercel Edge for CDN (Istanbul PoP gives lowest user-facing latency).

### Georgian Internet Backbone

- **Primary ISPs:** Magticom and Silknet provide 95%+ of consumer and business internet
- **Fiber coverage:** Extensive in Tbilisi and major cities; improving in rural areas
- **International connectivity:** Multiple submarine cable connections via Black Sea (primarily through Turkey)
- **Average speeds:** 50-200 Mbps residential, 1 Gbps business fiber available in Tbilisi
- **Peering:** Georgian IX (GIX) provides local peering; international traffic routes through Frankfurt or Istanbul

---

## Data Residency

### Legal Requirements

As of 2025-2026, Georgia does **not** have a strict data localization law equivalent to GDPR's data residency requirements. However:

- **Personal Data Protection Law** (Law of Georgia on Personal Data Protection): Requires adequate protection of personal data but does not mandate storage within Georgia.
- **Financial data:** National Bank of Georgia (NBG) regulations recommend (but do not currently require) that financial transaction data be stored within Georgian jurisdiction or in countries with adequate data protection.
- **Payment card data:** PCI DSS compliance is required for card processing, which is handled by TBC Pay (the payment processor), not by Prixio directly.

### Practical Recommendations

1. **User PII (names, addresses, phone numbers):** Store in Supabase (hosted in EU). Adequate protection under Georgia's data protection framework.
2. **Financial transactions:** Store in Supabase with encrypted columns for sensitive fields. Keep audit logs.
3. **Auction data (Lotify):** No residency requirement. Performance matters more -- keep close to users.
4. **Delivery tracking data (Courio):** GPS coordinates and route data. No residency requirement. PostGIS queries benefit from low-latency location.

---

## TBC Pay Integration Requirements

TBC Pay is Prixio's payment processor for both Lotify and Courio. Infrastructure requirements:

- **Webhook endpoints:** Must be publicly accessible HTTPS endpoints with valid TLS certificates. TBC Pay sends payment confirmation webhooks that must be acknowledged within 5 seconds.
- **Latency requirement:** TBC Bank's APIs are hosted in Georgia. Recommend compute in Helsinki (~40ms) or Frankfurt (~55ms) for lowest round-trip. US-based servers (~180ms) are acceptable but not ideal.
- **IP whitelisting:** TBC Pay may require whitelisting of Prixio's server IP for API access. Static IPs are preferable (Hetzner provides static; Railway/fly.io may require add-ons).
- **Uptime:** Payment webhook receivers must have 99.9%+ uptime. Missed webhooks mean missed payment confirmations.

---

## Georgian Language and Encoding

- **UTF-8 is sufficient.** Georgian script (Mkhedruli) is fully supported in UTF-8.
- **No special infrastructure needed** for Georgian language support. All modern cloud providers, databases, and frameworks handle UTF-8 natively.
- **PostgreSQL/Supabase:** Use `text` columns with UTF-8 encoding (default). Georgian collation (`ka_GE.UTF-8`) is available for proper alphabetical sorting.
- **Search:** PostgreSQL full-text search supports Georgian through `simple` dictionary. For advanced Georgian-language search, consider `pg_trgm` extension (available on Supabase).
- **Fonts:** Ensure CDN-delivered web fonts include Georgian glyphs (Google Fonts: Noto Sans Georgian, BPG fonts).

---

## SMS and Push Notification Infrastructure

### SMS Gateway

- **Magti SMS:** Local Georgian SMS gateway. Low cost (~0.02 GEL/SMS), direct connection to Georgian mobile networks. Requires API integration.
- **Twilio:** International alternative. Higher cost (~0.15 GEL/SMS to Georgian numbers) but better API, delivery reporting, and global reach.
- **Recommendation:** Magti for Georgian numbers (cheaper, local), Twilio as fallback for international or if Magti API is unreliable.

### Push Notifications

- **Firebase Cloud Messaging (FCM):** Used by Courio for delivery tracking push notifications. Free, reliable, works from any server location.
- **Infra requirement:** Server must be able to reach `fcm.googleapis.com`. No special Georgian considerations.

---

## Summary of Key Infrastructure Decisions

| Decision                  | Recommendation                              | Reason                                    |
|---------------------------|---------------------------------------------|-------------------------------------------|
| Primary compute region    | Hetzner Helsinki or fly.io Warsaw           | Lowest latency to Tbilisi                 |
| CDN/Edge                  | Cloudflare or Vercel Edge                   | Istanbul PoP for Georgian users           |
| Database                  | Supabase (EU region)                        | Managed, RLS, Realtime, PostGIS           |
| Payment webhook server    | Static IP in EU (Hetzner or Railway)        | TBC Pay requires reliable HTTPS endpoint  |
| SMS gateway               | Magti (primary) + Twilio (fallback)         | Cost and reliability balance              |
| Data residency            | EU is acceptable                            | No Georgian data localization law         |
| VAT impact                | +18% on all foreign cloud spend             | Budget accordingly                        |
