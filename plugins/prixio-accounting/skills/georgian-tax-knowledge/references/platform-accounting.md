# Platform Revenue Accounting — Prixio LLC

> **Sources**: matsne.gov.ge, rs.ge, bookkeeping.ge
> **Last updated**: March 2026

## Lotify (Auction Marketplace)

### Revenue Model
- Prixio charges a **commission** on each completed auction sale
- Funds are held in **escrow** until delivery is confirmed

### Accounting Treatment

```
Sale completes for 500 GEL (10% commission rate):

  Escrow received:     500.00 GEL  → Liability (not revenue!)
  Commission earned:    50.00 GEL  → Revenue
  Seller payout:       450.00 GEL  → Liability reduction

  If VAT-registered:
    VAT on commission:   9.00 GEL  → VAT liability (50 × 18%)
    Net commission:     41.00 GEL  → Net revenue
```

### Key Rules
- **Escrow funds are NOT revenue** — they are a liability to the seller
- **Only the commission is Prixio revenue**
- VAT applies to the commission amount only (once registered)
- TBC Pay processing fees (~1.5%) are a business expense

### Journal Entries

```
On sale completion:
  Dr. Bank (escrow)           500.00
    Cr. Escrow liability              450.00
    Cr. Commission revenue             50.00

On seller payout:
  Dr. Escrow liability        450.00
    Cr. Bank                          450.00
```

---

## Courio (Delivery Platform)

### Revenue Model
- Prixio charges a **15% platform fee** on each delivery
- Minimum delivery price: **4 GEL** (minimum fee: 0.60 GEL)
- Optional instant payout fee: **0.50 GEL** per payout

### Accounting Treatment

```
Delivery completed for 20 GEL:

  Payment received:     20.00 GEL  → Liability (not revenue!)
  Platform fee (15%):    3.00 GEL  → Revenue
  Courier payout:       17.00 GEL  → Liability reduction

  If VAT-registered:
    VAT on fee:          0.54 GEL  → VAT liability (3.00 × 18%)
    Net fee:             2.46 GEL  → Net revenue
```

### Key Rules
- **Courier earnings are NOT Prixio revenue** — pass-through liability
- **Only the 15% platform fee is Prixio revenue**
- Instant payout fee (0.50 GEL) is additional revenue
- Surge pricing increases base price → higher fee in absolute terms

### Journal Entries

```
On delivery completion:
  Dr. Bank (collected)         20.00
    Cr. Courier payout liability       17.00
    Cr. Platform fee revenue            3.00

On courier payout:
  Dr. Courier payout liability 17.00
    Cr. Bank                           17.00

If instant payout requested:
  Dr. Bank                      0.50
    Cr. Instant payout fee revenue      0.50
```

---

## Combined VAT Tracking

For VAT threshold purposes, Prixio revenue = Lotify commissions + Courio platform fees + instant payout fees.

**Escrow funds and courier payouts do NOT count toward the 100,000 GEL VAT threshold.**

---

## Reverse-Charge VAT on Foreign Services

Both Lotify and Courio likely use foreign SaaS tools (hosting, payment processors, analytics).

```
When Prixio pays for foreign services:
  Service cost in GEL equivalent → declare 18% reverse-charge VAT
  If VAT-registered: claim simultaneous input VAT deduction → net 0%
  If NOT VAT-registered: pay 18% with no recovery

This obligation exists REGARDLESS of VAT registration status.
Must be declared monthly by the 15th.
```

---

## Digital Platform VAT Considerations (2026)

Under recent Georgian amendments aligning with international standards:
- Non-resident digital service providers must register for VAT on B2C services
- Online marketplaces MAY be deemed suppliers for VAT purposes
- If Lotify/Courio expand to serve non-resident sellers, additional VAT obligations may apply
- Monitor rs.ge for platform-specific guidance updates

---

## Special Tax Regime Considerations for Platforms

### If Prixio obtains International Company Status (IC):
```
- CIT on distributed profits: 5% (vs 15%)
- Employee PIT: 5% (vs 20%)
- Dividend to non-resident: 0%
- Requirement: ≥98% revenue from qualifying IT activities
- Lotify/Courio revenue may qualify as IT services
```

### If Prixio obtains Virtual Zone Person (VZP) Status:
```
- CIT on export IT income: 0%
- Domestic Georgian platform revenue: standard 15% CIT
- Only useful if expanding internationally
```
