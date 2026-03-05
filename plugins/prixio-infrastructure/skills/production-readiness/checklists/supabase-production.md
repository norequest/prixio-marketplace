# Supabase Production Checklist

Applies to: **Lotify Database**, **Courio Database**

---

## Database

- [ ] RLS enabled on ALL tables (zero exceptions)
- [ ] SECURITY DEFINER functions use `SET search_path = ''`
- [ ] Connection pooling configured (Supavisor)
- [ ] Regular VACUUM/ANALYZE (auto or scheduled)
- [ ] Indexes on all foreign keys and frequently queried columns
- [ ] PostGIS indexes for Courio geospatial queries (GIST)
- [ ] No public schema exposure beyond what RLS permits
- [ ] Database migrations versioned and reproducible

## Auth

- [ ] Email confirmation enabled
- [ ] Password policy (min length, complexity)
- [ ] Rate limiting on auth endpoints
- [ ] Session management (token refresh, expiry)
- [ ] OAuth providers configured securely (if used)
- [ ] User roles mapped correctly to RLS policies

## Backup & Recovery

- [ ] Point-in-time recovery enabled (Pro plan)
- [ ] Regular pg_dump backups to separate storage
- [ ] Tested restore procedure
- [ ] Data retention policy
- [ ] Backup encryption at rest
- [ ] Cross-region backup replication (if applicable)

## Monitoring

- [ ] Database size monitoring
- [ ] Connection count monitoring (alert at 80% capacity)
- [ ] Slow query logging enabled
- [ ] Storage usage monitoring
- [ ] Realtime subscription count monitoring
- [ ] Edge function invocation monitoring

## Security Hardening

- [ ] Service role key never exposed to client
- [ ] Anon key permissions audited (minimal access)
- [ ] Database webhooks use HTTPS only
- [ ] Network restrictions (IP allowlist if supported)
- [ ] Audit logging for sensitive operations (admin actions, deletions)

## Realtime

- [ ] Realtime enabled only on tables that need it
- [ ] Broadcast and Presence configured with auth checks
- [ ] Connection limits understood and monitored
- [ ] Fallback behavior when Realtime is unavailable
