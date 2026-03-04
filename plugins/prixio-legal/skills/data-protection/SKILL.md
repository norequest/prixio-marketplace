---
name: data-protection
description: >
  Georgian personal data protection law compliance for IT companies — GDPR-aligned
  requirements, data controller obligations, cross-border transfers, and PDPS
  enforcement. Use this skill when users ask about: data protection, GDPR,
  privacy policy, personal data, consent, data breach, DPO, cross-border data
  transfer, or Georgian data protection compliance. Also triggers for:
  "data protection", "GDPR", "personal data", "პერსონალური მონაცემები",
  "privacy", "კონფიდენციალურობა", "consent", "თანხმობა", "data breach",
  "მონაცემთა დარღვევა", "PDPS", "DPO", "privacy policy".
allowed-tools: WebSearch, WebFetch, Read
---

# Personal Data Protection in Georgia — IT Company Compliance

> **Sources**: matsne.gov.ge, pdps.ge (Personal Data Protection Service),
> KPMG Georgia Guide 2023, DataGuidance.
> **Last updated**: March 2026.

## Legal Framework

### Primary Law
**Law of Georgia on Personal Data Protection** (2023)
- Adopted: June 14, 2023
- Effective: **March 1, 2024**
- Replaces: 2011 Data Protection Law
- Model: **GDPR-aligned** (EU General Data Protection Regulation)

### Supervisory Authority
**Personal Data Protection Service (PDPS)** — pdps.ge
- Independent state authority
- Powers: investigate complaints, impose penalties, issue guidance
- Head: Data Protection Inspector (მონაცემთა დაცვის ინსპექტორი)

---

## Core Principles (Art. 4)

| Principle | Description |
|-----------|-------------|
| **Lawfulness** | Data must be collected with legal basis (consent or other) |
| **Purpose limitation** | Data used only for specified, legitimate purposes |
| **Data minimization** | Collect only what is necessary |
| **Accuracy** | Keep data accurate and up-to-date |
| **Storage limitation** | Don't keep data longer than necessary |
| **Integrity & confidentiality** | Protect against unauthorized access or loss |
| **Accountability** | Document processing activities, demonstrate compliance |

---

## Legal Bases for Processing (Art. 5)

1. **Consent** (თანხმობა) — freely given, specific, informed, unambiguous
2. **Contract performance** — necessary to fulfill a contract with data subject
3. **Legal obligation** — required by Georgian law
4. **Vital interests** — protect life of data subject
5. **Public interest** — task in public interest or official authority
6. **Legitimate interests** — controller's legitimate interest (balancing test required)

### Consent Requirements
- Must be **freely given** (no bundling with service access)
- Must be **specific** to each processing purpose
- Must be **informed** (clear language about what data, why, who)
- Must be **unambiguous** (affirmative action, no pre-ticked boxes)
- Must be **withdrawable** at any time (as easy as giving it)
- For **children**: parental consent required under age **16**; processing of data relating to minors under 16 requires parent/legal representative consent
- **Special categories** of data: written consent mandatory for processing sensitive data

---

## IT Company Obligations

### 1. Data Controller Duties

| Obligation | What It Means |
|-----------|---------------|
| **Privacy Policy** | Must publish clear, accessible policy on website |
| **Processing Records** | Maintain internal register of all processing activities |
| **Impact Assessment** | Required for high-risk processing (profiling, large-scale, sensitive data) |
| **Data Protection Officer** | Appoint DPO if: public authority, large-scale monitoring, or sensitive data. DPO provisions effective **June 1, 2024** |
| **Data Protection Impact Assessment** | Required for high-risk processing. DPIA provisions effective **June 1, 2024** |
| **Breach Notification** | Notify PDPS within **72 hours** of discovering a data breach |
| **Subject Access** | Respond to data subject requests within **15 days** |
| **Security Measures** | Implement technical and organizational measures |

### 2. Privacy Policy Requirements for IT Platforms

A Georgian IT company's privacy policy must include:
1. Identity and contact details of the controller
2. Contact details of DPO (if appointed)
3. Purposes and legal bases of processing
4. Categories of personal data collected
5. Recipients or categories of recipients
6. Cross-border transfer information (if applicable)
7. Data retention periods
8. Data subject rights (access, correction, deletion, portability)
9. Right to withdraw consent
10. Right to lodge complaint with PDPS
11. Whether providing data is mandatory or voluntary
12. Information about automated decision-making/profiling

### 3. Data Subject Rights

| Right | Description | Response Time |
|-------|-------------|---------------|
| **Access** | Know what data is collected about them | 15 days |
| **Rectification** | Correct inaccurate data | 15 days |
| **Erasure** | Delete data ("right to be forgotten") | 15 days |
| **Restriction** | Limit processing | 15 days |
| **Portability** | Receive data in machine-readable format | 15 days |
| **Object** | Object to processing based on legitimate interests | 15 days |
| **Automated decisions** | Not be subject to solely automated decisions | 15 days |

---

## Cross-Border Data Transfers

### Adequate Countries (as of January 2025)
Georgia recognizes data protection adequacy for:
- All **EU/EEA member states**
- **United Kingdom**
- **Canada**, **Japan**, **Israel**, **Argentina**
- **Australia**, **New Zealand**
- **Iceland**, **Albania**
- Full list published by PDPS

### Transfer to Non-Adequate Countries
Allowed with appropriate safeguards:
1. **Standard contractual clauses** (SCCs)
2. **Binding corporate rules** (BCRs)
3. **Explicit consent** of data subject
4. **Contract necessity** — transfer needed to perform contract
5. **Important public interest**

### Practical for IT Companies
- Using **AWS, Google Cloud, Azure** (US servers) → need safeguards
- Storing data in **EU data centers** → adequate, no extra measures
- Sharing with **US clients** → need SCCs or explicit consent
- **Georgian hosting** → no cross-border rules apply

---

## Data Breach Management

### Notification Timeline
1. **Discover breach** → internal assessment within 24 hours
2. **Notify PDPS** → within **72 hours** of discovery
3. **Notify data subjects** → without undue delay if high risk to rights
4. **Document** → maintain internal breach register regardless of notification

### What to Include in Notification
- Nature of the breach (what happened)
- Categories and approximate number of affected data subjects
- Categories and approximate number of affected personal data records
- Name and contact details of DPO or contact point
- Description of likely consequences
- Description of measures taken or proposed

### Penalties
| Violation | Fine (GEL) |
|-----------|-----------|
| Minor violation | 1,000 |
| Significant violation | 5,000 |
| Serious violation | 10,000 |
| Repeated violation | Double the previous fine |
| Criminal violation (unauthorized access) | Criminal penalties including imprisonment |

---

## Specific Guidance for Platform Companies

### Lotify (Auction Platform)
- Collects: buyer/seller names, addresses, payment info, item photos
- Legal basis: **Contract performance** (auction service)
- Must: publish privacy policy, enable account deletion, secure payment data
- Special: Payment card data → PCI DSS compliance (not just Georgian law)

### Courio (Delivery Platform)
- Collects: sender/courier names, phone numbers, addresses, GPS location
- Legal basis: **Contract performance** (delivery service)
- Must: minimize location data retention, allow GPS tracking opt-out
- Special: Real-time location = **high-risk processing** → impact assessment required

### General IT Platform Requirements
1. **Cookie consent** — inform users about cookies, obtain consent for non-essential
2. **Account deletion** — must provide mechanism to delete accounts and data
3. **Data export** — provide user data in portable format on request
4. **Third-party sharing** — disclose all third parties receiving user data
5. **Analytics** — if using Google Analytics etc., disclose and consider adequacy

---

## PDPS 2025 Inspection Plan

The PDPS actively inspects organizations. 2025 focus areas include:
- Companies with **websites and applications** (relevant for IT!)
- Medical institutions
- Educational institutions
- Hotels and restaurants
- Law enforcement agencies

### Compliance Checklist for IT Companies
- [ ] Published privacy policy on website (Georgian + English)
- [ ] Internal register of processing activities maintained
- [ ] Data Protection Impact Assessment for high-risk processing
- [ ] DPO appointed (if required by scale)
- [ ] Data breach response plan documented
- [ ] Cookie consent mechanism implemented
- [ ] User account deletion functionality available
- [ ] Employee training on data protection completed
- [ ] Contracts with data processors include required clauses
- [ ] Cross-border transfer safeguards in place
