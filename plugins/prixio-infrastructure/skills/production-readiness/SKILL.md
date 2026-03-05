---
name: production-readiness
description: >
  Audits and generates production readiness checklists for Prixio LLC services.
  Covers reliability, security, observability, performance, backup, and compliance.
  Triggers on: "production ready", "production readiness", "audit", "checklist",
  "hardening", "security check", "health check", "monitoring setup", "ready for
  launch", "go live".
allowed-tools: Bash, Read
---

# Production Readiness Skill

## Overview

This skill provides comprehensive production readiness auditing for all Prixio LLC
services — Lotify (Georgian Online Auction Platform) and Courio (Delivery Platform
for Georgia). It evaluates services across six categories: reliability, security,
observability, performance, backup, and compliance.

## How to Use

### 1. Run the Automated Audit Script

```bash
# Basic audit for a specific app
python3 scripts/readiness_audit.py --app courio-api --level basic

# Thorough audit with deeper checks
python3 scripts/readiness_audit.py --app lotify-api --level thorough
```

Supported `--app` values:
- `lotify-api` — Lotify Fastify 5 API
- `courio-api` — Courio Fastify 5 API
- `lotify-web` — Lotify Next.js consumer-facing web app
- `courio-admin` — Courio Next.js admin dashboard
- `courier-app` — Courio Expo courier mobile app
- `consumer-app` — Courio Expo consumer mobile app

Supported `--level` values:
- `basic` — quick surface-level checks (health endpoints, headers, config files)
- `thorough` — deep inspection (response times, security headers, config validation)

### 2. Consult the Checklists Manually

Review the relevant checklist for your service type:

| Service Type    | Checklist File                          |
| --------------- | --------------------------------------- |
| Fastify 5 APIs  | `checklists/fastify-production.md`      |
| Next.js Apps     | `checklists/nextjs-production.md`       |
| Supabase (DB)   | `checklists/supabase-production.md`     |
| Expo Mobile Apps | `checklists/expo-production.md`         |

### 3. Interpret the Audit Output

The audit script produces a scored report (0-100) with findings categorized as:

- **P0 (Critical)** — Must fix before launch. Security vulnerabilities, missing health checks, no graceful shutdown.
- **P1 (High)** — Should fix before launch. Missing observability, no rate limiting, missing backups.
- **P2 (Medium)** — Fix soon after launch. Performance optimizations, SEO improvements, bundle size.

## Categories Covered

1. **Reliability** — Health checks, graceful shutdown, connection pooling, retries, error boundaries, process management.
2. **Security** — Helmet, CORS, rate limiting, input validation, JWT/HMAC verification, RLS, secrets management.
3. **Observability** — Structured logging, request ID propagation, error tracking, uptime monitoring, alerting.
4. **Performance** — Compression, caching, query optimization, bundle size, Core Web Vitals, app startup time.
5. **Backup & Recovery** — PITR, pg_dump, restore testing, data retention policy.
6. **Compliance** — Georgian data regulations, Supabase RLS enforcement, SECURITY DEFINER function safety.

## Integration with CI/CD

The audit script exits with code 0 if the score is >= 70 (passing) and code 1 otherwise.
You can integrate it into your CI pipeline:

```yaml
# Example GitHub Actions step
- name: Production Readiness Check
  run: python3 plugins/prixio-infrastructure/skills/production-readiness/scripts/readiness_audit.py --app lotify-api --level basic
```
