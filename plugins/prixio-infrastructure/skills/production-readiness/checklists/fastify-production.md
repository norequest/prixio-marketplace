# Fastify 5 API Production Checklist

Applies to: **Lotify API**, **Courio API**

---

## Reliability

- [ ] Health check endpoint (`/health`) returns 200 with DB connectivity check
- [ ] Graceful shutdown (SIGTERM handler, drain connections)
- [ ] Connection pooling (Supabase connection limit awareness)
- [ ] Request timeout configuration
- [ ] Retry logic for external services (TBC Pay, webhooks)
- [ ] Error boundaries — unhandled rejections don't crash server
- [ ] Process manager (PM2 or Docker restart policy)

## Security

- [ ] Helmet plugin enabled (security headers)
- [ ] CORS configured (specific origins, not wildcard)
- [ ] Rate limiting per IP and per user
- [ ] Request body size limits
- [ ] Input validation (Zod schemas on all routes)
- [ ] JWT verification on protected routes
- [ ] HMAC signature verification on webhooks
- [ ] No secrets in logs or error responses
- [ ] RLS enabled on all Supabase tables

## Observability

- [ ] Structured JSON logging (pino)
- [ ] Request ID propagation
- [ ] Error tracking (Sentry integration)
- [ ] Uptime monitoring (external ping)
- [ ] Response time metrics
- [ ] Alert on error rate spike

## Performance

- [ ] Response compression (gzip/brotli)
- [ ] Static response caching headers
- [ ] Database query optimization (indexes, N+1 prevention)
- [ ] Redis caching for hot paths
- [ ] Payload size optimization

## Deployment

- [ ] Docker multi-stage build for minimal image size
- [ ] Environment variables validated at startup (fail fast)
- [ ] Zero-downtime deployments (rolling update or blue-green)
- [ ] Rollback procedure documented and tested
- [ ] CI/CD pipeline with automated tests before deploy
