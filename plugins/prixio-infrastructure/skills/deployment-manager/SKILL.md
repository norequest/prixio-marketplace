---
name: deployment-manager
description: >
  Generates deployment configs, CI/CD pipelines, and manages deployments for
  Prixio LLC (Lotify + Courio). Supports Docker, GitHub Actions, Vercel, Railway,
  Hetzner, Coolify, and EAS. Triggers on: "deploy", "deployment", "Dockerfile",
  "docker-compose", "CI/CD", "GitHub Actions", "pipeline", "rollback",
  "zero-downtime", "build", "release".
allowed-tools: Bash, Read, Write, Edit
---

# Deployment Manager Skill

## Usage

Generate deployment configurations using the templates in `templates/`. Run
`scripts/deploy_check.py` for pre-deployment validation before pushing to any
environment.

```bash
# Generate a config from template
claude "generate a Dockerfile for lotify-api"

# Validate deployment readiness
python3 scripts/deploy_check.py --app lotify-api --env production

# Full deploy workflow
python3 scripts/deploy_check.py --app lotify-api --env staging && echo "Ready to deploy"
```

## Supported Platforms

| Platform       | Used For                  | Deploy Method              |
|----------------|---------------------------|----------------------------|
| Vercel         | Lotify web, Lotify admin  | Git push / Vercel CLI      |
| Railway        | Courio API                | Git push / Railway CLI     |
| Hetzner+Coolify| Self-hosted services      | Docker + Coolify dashboard |
| EAS            | Courio mobile (Expo)      | eas build / eas submit     |

## Deployment Strategies

- **Rolling (default):** Gradually replace old instances. Used for web frontends.
- **Blue-Green (for API):** Spin up new version alongside old, switch traffic after
  health checks pass. Used for lotify-api and courio-api to achieve zero-downtime.
- **Preview Deployments:** Automatic per-PR preview URLs on Vercel. Useful for
  design review and QA before merging.

## Environment Management

All services follow a three-stage promotion pipeline:

```
dev --> staging --> production
```

- **dev:** Local development with Docker Compose or direct `pnpm dev`.
- **staging:** Mirrors production config. Deployed on every push to `develop` branch.
  Uses staging Supabase project and test payment keys.
- **production:** Deployed on push to `main` branch (after CI passes). Uses
  production Supabase, live TBC Pay keys, real DNS.

### Environment Variable Conventions

- All env vars are prefixed per app: `LOTIFY_`, `COURIO_`, or shared `PRIXIO_`.
- Secrets are stored in GitHub Actions secrets and Coolify environment manager.
- Never commit `.env` files. Use `.env.example` as a template.

## Templates

| Template                        | Description                              |
|---------------------------------|------------------------------------------|
| `Dockerfile.fastify`            | Fastify 5 API (pnpm + Turborepo)        |
| `Dockerfile.nextjs`             | Next.js 15 app (pnpm + Turborepo)       |
| `docker-compose.prod.yml`       | Self-hosted production stack             |
| `github-actions-monorepo.yml`   | CI/CD pipeline for monorepo              |
| `coolify-setup.md`              | Hetzner + Coolify setup guide            |

## Pre-Deployment Checklist

The `deploy_check.py` script validates:

1. Required environment variables are present
2. Dockerfile exists and has valid syntax
3. Health endpoint responds (if service is running)
4. Git working tree is clean (no uncommitted changes)
5. Database migrations are up to date

Run it before every production deploy.
