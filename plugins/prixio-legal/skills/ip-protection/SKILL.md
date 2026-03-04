---
name: ip-protection
description: >
  Intellectual property protection for software and IT products in Georgia —
  copyright, patents, trademarks, trade secrets, and work-for-hire provisions.
  Use this skill when users ask about: software copyright, patent registration,
  trademark filing, IP protection, Sakpatenti, work for hire, code ownership,
  or protecting tech intellectual property. Also triggers for:
  "copyright", "საავტორო", "patent", "პატენტი", "trademark", "სასაქონლო ნიშანი",
  "IP", "intellectual property", "Sakpatenti", "work for hire", "code ownership",
  "open source", "license", "trade secret", "NDA".
allowed-tools: WebSearch, WebFetch, Read
---

# Intellectual Property Protection for IT Companies in Georgia

> **Sources**: matsne.gov.ge, sakpatenti.gov.ge, WIPO, Berne Convention.
> **Last updated**: March 2026.

## Legal Framework Overview

| IP Type | Georgian Law | Protection | Registration |
|---------|-------------|------------|-------------|
| **Copyright** | Law on Copyright and Neighboring Rights (1999) | Automatic | Optional (Sakpatenti) |
| **Patents** | Patent Law of Georgia (1999) | 20 years | Required (Sakpatenti) |
| **Trademarks** | Law on Trademarks (2010) | 10 years (renewable) | Required (Sakpatenti) |
| **Trade Secrets** | Civil Code + Law on Unfair Competition | Unlimited | No registration |
| **IC Topographies** | Law on Topographies of Integrated Circuits | 10 years | Required |

---

## 1. Software Copyright Protection

### Automatic Protection
- Software (computer programs) are protected as **literary works** under Art. 6(1)
- Protection is **automatic** — no registration required
- Protection lasts: **life of author + 70 years** (or 70 years from creation for corporate works)
- Georgia is a member of the **Berne Convention** — protection is international

### What Is Protected
- Source code and object code
- Software architecture and design documents (if sufficiently original)
- Database structure (under sui generis database right)
- User interfaces (if sufficiently creative)
- Documentation and technical manuals

### What Is NOT Protected
- Algorithms and mathematical methods (abstract ideas)
- Programming languages
- Functional specifications (the idea, not the expression)
- APIs (debated — trend toward non-protectability)

### Optional Copyright Registration
- Available at **Sakpatenti** (National Intellectual Property Center)
- Provides **official certificate** useful for enforcement
- Helps establish creation date and authorship
- Fee: approximately 50-100 GEL
- Website: sakpatenti.gov.ge

---

## 2. Work-for-Hire (სამსახურეობრივი ნაშრომი)

### General Rule (Art. 16, Copyright Law)
- The **author** is the original copyright holder
- Exception: **work for hire** — employer may own economic rights

### Employer Ownership Conditions
1. Work must be created **within the scope of employment duties**
2. Employment contract should **explicitly address** IP ownership
3. Employer acquires **economic rights** (reproduction, distribution, etc.)
4. Author retains **moral rights** (attribution, integrity) — non-transferable

### Best Practices for IT Companies
1. **Include IP assignment clause** in every employment contract:
   - Explicitly state that all code created during employment belongs to the company
   - Cover inventions, designs, and any creative works
   - Address after-hours and personal project policies
2. **Contractor agreements** must include:
   - Explicit IP assignment (contractors are NOT employees — work-for-hire may not apply)
   - Signed **IP Assignment Agreement** (ინტელექტუალური საკუთრების გადაცემა)
   - Specification of deliverables and ownership transfer
3. **Open source contributions**:
   - Define company policy on open source use and contribution
   - Ensure compliance with open source licenses (GPL, MIT, Apache, etc.)
   - Employee contributions to FOSS should be governed by written policy

---

## 3. Patent Protection

### Software Patents in Georgia
- Pure software is generally **NOT patentable** (similar to EU approach)
- Software combined with **technical effect** may be patentable
- Examples: novel algorithm + specific hardware, software controlling industrial process

### Patent Registration (Sakpatenti)
- **Duration**: 20 years from filing date
- **Cost**: Filing fee ~400 GEL + maintenance fees
- **Process**: Application → Formal exam → Substantive exam → Grant
- **Timeline**: 18-24 months typical
- **International**: Georgia is member of PCT (Patent Cooperation Treaty)
- **Fee reductions**: 70% discount for academic institutions; 90% for students/retirees
- **Electronic filing**: 20% reduction on fees
- **Non-residents**: Must appoint a local patent attorney to represent them before Sakpatenti
- **New fees effective May 30, 2025** (Government Resolution No. 174)

---

## 4. Trademark Protection

### Why IT Companies Need Trademarks
- Protect product names (Lotify, Courio, etc.)
- Protect logos and visual branding
- Prevent domain squatting
- Build enforceable brand identity

### Registration Process
1. **Search** existing trademarks at Sakpatenti database
2. **File application** at Sakpatenti (online or in person)
3. **Examination**: Formal (1-2 months) + Substantive (3-6 months)
4. **Publication**: 3 months opposition period
5. **Registration**: Certificate issued
6. **Duration**: **10 years**, renewable indefinitely in 10-year periods

### Costs
| Service | Fee (GEL) | Notes |
|---------|-----------|-------|
| Filing (1 class) | ~400 | Standard trademark registration for one class ~420 USD |
| Each additional class | ~100 | ~50 USD per additional class |
| Accelerated formal exam | ~200 USD | Expedited processing |
| Accelerated substantive exam | ~300 USD | Expedited processing |
| Registration fee | 400 | Upon successful examination |
| Renewal (10 years) | 400 | Renewable indefinitely |
| International (Madrid Protocol) | From $653 (WIPO) | Designating Georgia |

**Fee reductions**: 20% discount for electronic filing; 70% for academic institutions; 90% for students/retirees.

### International Protection
- Georgia is a member of the **Madrid Protocol** — file one international application
- Also member of **Nice Classification** system
- Protection in 130+ countries through single WIPO application
- Non-resident applicants must appoint a **local patent attorney** for Sakpatenti proceedings

---

## 5. Trade Secrets Protection

### Legal Basis
- Civil Code of Georgia (general contract law)
- Law on Unfair Competition (unfair use of trade secrets)

### Protection Measures for IT Companies
1. **NDAs (Non-Disclosure Agreements)**:
   - Enforceable in Georgian courts
   - Should specify: scope, duration, exceptions, penalties
   - Recommended with: employees, contractors, investors, partners
2. **Access controls**:
   - Limit code repository access
   - Use role-based permissions
   - Implement audit logging
3. **Contractual measures**:
   - Non-compete clauses (enforceable but must be reasonable — see Employment Law skill)
   - Confidentiality clauses in employment contracts
   - Exit interview procedures

---

## 6. Open Source Compliance

### Key License Types and Obligations

| License | Can Use in Commercial? | Must Open Source Derived Work? | Attribution Required? |
|---------|----------------------|-------------------------------|----------------------|
| MIT | Yes | No | Yes |
| Apache 2.0 | Yes | No | Yes + patent grant |
| BSD | Yes | No | Yes |
| GPL v3 | Yes | Yes (if distributed) | Yes |
| LGPL | Yes | Only for library changes | Yes |
| AGPL | Yes | Yes (including SaaS) | Yes |

### Georgia-Specific Considerations
- No specific Georgian law on open source
- General copyright and contract law applies
- GPL/AGPL obligations are enforceable under copyright law
- **AGPL warning**: SaaS platforms (like Lotify/Courio) using AGPL code must provide source

---

## 7. IP Enforcement in Georgia

### Available Remedies
1. **Civil claims**: Injunctions, damages, account of profits
2. **Criminal prosecution**: For willful copyright infringement (up to 5 years imprisonment)
3. **Administrative measures**: Border seizure of counterfeit goods
4. **Mediation/arbitration**: Through WIPO or Georgian arbitration centers

### Court System
- First instance: City/District courts
- Appeals: Court of Appeals
- Final: Supreme Court of Georgia
- IP specialized: No dedicated IP court, but Tbilisi City Court handles most cases

### Practical Tips
1. Register copyright at Sakpatenti (even though optional) — simplifies enforcement
2. Keep timestamped development records (git logs serve as evidence)
3. Use digital timestamps/blockchain for critical IP documentation
4. Include arbitration clauses in contracts (faster than courts)
