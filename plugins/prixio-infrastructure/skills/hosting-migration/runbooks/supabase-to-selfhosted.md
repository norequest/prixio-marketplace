# Supabase Cloud to Self-Hosted Migration Runbook

**Applicable to:** All Prixio projects using Supabase (Lotify, Courio)
**Estimated downtime:** 1-4 hours (database migration + verification)
**Difficulty:** HIGH -- This is a major migration
**Cost impact:** Supabase Pro $25/mo -> Self-hosted on Hetzner ~EUR 10-20/mo (but significantly more maintenance)

---

## RISK ASSESSMENT

This is the highest-risk migration in the Prixio infrastructure portfolio. Before proceeding, understand the following.

### What You Gain
- Full control over PostgreSQL configuration (custom extensions, tuning)
- PostGIS customization for Courio's delivery routing
- No vendor lock-in on database tier
- Potentially lower cost at scale
- Data residency control (host in specific country/region)

### What You Lose
- Managed backups and point-in-time recovery
- Supabase Auth (managed auth service)
- Supabase Realtime (managed WebSocket server)
- Supabase Storage (managed file storage with CDN)
- Supabase Dashboard (SQL editor, table viewer, logs)
- Automatic security updates
- One-click compute scaling
- Supabase client libraries (partially -- REST/realtime won't work the same)

### When to Consider This Migration
- Supabase costs exceed $100/mo and growing
- Need PostGIS extensions not available on Supabase (most are available now)
- Regulatory requirement for on-premises data
- Need PostgreSQL extensions Supabase doesn't support
- Supabase service reliability issues affecting production

### When NOT to Do This
- Just to save $25/mo (your time maintaining it costs more)
- If you rely heavily on Supabase Auth (migration is complex)
- If you use Supabase Realtime extensively
- If you don't have ops experience managing PostgreSQL in production

---

## Prerequisites

- [ ] Hetzner VPS provisioned (CX32 minimum, CX42 recommended for database)
- [ ] At least 3x current database size in free disk space on target
- [ ] PostgreSQL 15+ experience (tuning, backup, monitoring)
- [ ] Full understanding of current Supabase features in use (Auth, Realtime, Storage, RLS)
- [ ] Maintenance window scheduled (1-4 hours, ideally during lowest traffic)
- [ ] Rollback plan reviewed and tested
- [ ] Current Supabase project will remain active for 30 days post-migration

---

## Phase 1: Audit Current Supabase Usage

### 1.1 Identify all Supabase features in use

```sql
-- List all tables
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename))
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'supabase_migrations', 'extensions', 'graphql', 'graphql_public', 'vault', 'pgsodium')
ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC;

-- List all extensions
SELECT extname, extversion FROM pg_extension ORDER BY extname;

-- List all RLS policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- List all functions
SELECT routine_schema, routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
ORDER BY routine_name;

-- List all triggers
SELECT trigger_schema, trigger_name, event_object_table, action_timing, event_manipulation
FROM information_schema.triggers
WHERE trigger_schema = 'public';

-- Check storage buckets
SELECT * FROM storage.buckets;

-- Check auth users count
SELECT count(*) FROM auth.users;
```

### 1.2 Document integration points

| Feature | Used By | Migration Path |
|---------|---------|---------------|
| Auth (email/password) | Lotify, Courio | Self-hosted GoTrue or custom auth |
| Auth (OAuth - Google) | Lotify | GoTrue with OAuth config |
| Realtime | Lotify (auction updates) | Self-hosted Realtime server |
| Storage | Lotify (product images) | MinIO or local filesystem |
| RLS | Both | PostgreSQL native RLS (same syntax) |
| PostGIS | Courio | Full PostGIS on self-hosted (better) |
| Edge Functions | Neither (currently) | N/A |

---

## Phase 2: Set Up Self-Hosted Infrastructure

### 2.1 Option A: Self-Hosted Supabase (Docker)

This maintains API compatibility with Supabase client libraries.

```bash
ssh root@$HETZNER_IP

# Clone Supabase Docker setup
git clone --depth 1 https://github.com/supabase/supabase /opt/supabase
cd /opt/supabase/docker

# Copy example env
cp .env.example .env
```

Edit `.env` with secure values:

```bash
# Generate secure secrets
openssl rand -base64 32  # For POSTGRES_PASSWORD
openssl rand -base64 32  # For JWT_SECRET
# Generate JWT tokens at https://supabase.com/docs/guides/self-hosting#api-keys

# Key settings in .env:
POSTGRES_PASSWORD=<generated-secure-password>
JWT_SECRET=<generated-jwt-secret>
ANON_KEY=<generated-anon-jwt>
SERVICE_ROLE_KEY=<generated-service-role-jwt>
SITE_URL=https://lotify.ge
API_EXTERNAL_URL=https://db.lotify.ge
```

```bash
# Start Supabase
docker compose up -d

# Verify all services are running
docker compose ps
```

### 2.2 Option B: Bare PostgreSQL + Individual Services

For maximum control but most maintenance work.

```bash
ssh root@$HETZNER_IP

# Install PostgreSQL 16
apt install -y postgresql-16 postgresql-16-postgis-3

# Configure PostgreSQL
cat >> /etc/postgresql/16/main/postgresql.conf << 'EOF'
# Connection settings
listen_addresses = 'localhost'
max_connections = 200
superuser_reserved_connections = 3

# Memory (for CX32: 8GB RAM)
shared_buffers = 2GB
effective_cache_size = 6GB
work_mem = 32MB
maintenance_work_mem = 512MB

# WAL
wal_buffers = 64MB
checkpoint_completion_target = 0.9
max_wal_size = 2GB

# Query planning
random_page_cost = 1.1
effective_io_concurrency = 200
default_statistics_target = 100

# Logging
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
EOF

systemctl restart postgresql
```

### 2.3 Install Required Extensions

```sql
-- Connect to the target database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "postgis";        -- For Courio
CREATE EXTENSION IF NOT EXISTS "postgis_topology"; -- For Courio
CREATE EXTENSION IF NOT EXISTS "pgjwt";           -- For JWT verification in RLS
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"; -- For monitoring
```

---

## Phase 3: Database Migration

### 3.1 Export from Supabase

```bash
# Get the direct connection string from Supabase Dashboard
# Project Settings -> Database -> Connection String -> URI (direct)

export SOURCE_DB="postgresql://postgres.[ref]:[password]@db.[ref].supabase.co:5432/postgres"

# Full dump including schema, data, and extensions
pg_dump "$SOURCE_DB" \
  --verbose \
  --format=custom \
  --no-owner \
  --no-privileges \
  --exclude-schema='supabase_*' \
  --exclude-schema='_supabase_*' \
  --exclude-schema='extensions' \
  --exclude-schema='graphql*' \
  --exclude-schema='vault' \
  --exclude-schema='pgsodium*' \
  --exclude-schema='_realtime' \
  --file=supabase-export-$(date +%Y%m%d-%H%M%S).dump

# Also dump auth.users if migrating auth
pg_dump "$SOURCE_DB" \
  --verbose \
  --format=custom \
  --no-owner \
  --no-privileges \
  --schema='auth' \
  --file=supabase-auth-export-$(date +%Y%m%d-%H%M%S).dump

# Dump storage metadata
pg_dump "$SOURCE_DB" \
  --verbose \
  --format=custom \
  --no-owner \
  --no-privileges \
  --schema='storage' \
  --file=supabase-storage-export-$(date +%Y%m%d-%H%M%S).dump
```

### 3.2 Transfer dump to target server

```bash
scp supabase-export-*.dump root@$HETZNER_IP:/opt/
scp supabase-auth-export-*.dump root@$HETZNER_IP:/opt/
scp supabase-storage-export-*.dump root@$HETZNER_IP:/opt/
```

### 3.3 Restore on target

```bash
ssh root@$HETZNER_IP

# For self-hosted Supabase (Option A):
export TARGET_DB="postgresql://postgres:<password>@localhost:5432/postgres"

# For bare PostgreSQL (Option B):
export TARGET_DB="postgresql://postgres:<password>@localhost:5432/prixio"

# Restore main database
pg_restore \
  --verbose \
  --no-owner \
  --no-privileges \
  --dbname="$TARGET_DB" \
  /opt/supabase-export-*.dump

# Restore auth (only for self-hosted Supabase option)
pg_restore \
  --verbose \
  --no-owner \
  --no-privileges \
  --dbname="$TARGET_DB" \
  /opt/supabase-auth-export-*.dump
```

### 3.4 Verify data integrity

```sql
-- Compare row counts for critical tables
-- Run on both source and target, compare results

SELECT 'orders' as table_name, count(*) FROM public.orders
UNION ALL
SELECT 'users', count(*) FROM public.profiles
UNION ALL
SELECT 'shipments', count(*) FROM public.shipments
UNION ALL
SELECT 'payments', count(*) FROM public.payments
UNION ALL
SELECT 'products', count(*) FROM public.products;

-- Verify PostGIS data (Courio)
SELECT count(*) FROM public.delivery_zones WHERE zone_geometry IS NOT NULL;

-- Verify RLS policies exist
SELECT count(*) FROM pg_policies WHERE schemaname = 'public';
```

---

## Phase 4: Auth Migration

### If using self-hosted Supabase (Option A):
Auth data is restored with the dump. Update the JWT secret in `.env` to match your new secret, then all existing sessions will be invalidated (users must re-login).

### If using bare PostgreSQL (Option B):
You need an alternative auth solution:

#### Option B1: Self-hosted GoTrue (Supabase's auth server)

```bash
docker run -d \
  --name gotrue \
  -p 9999:9999 \
  -e GOTRUE_DB_DATABASE_URL="postgresql://postgres:<password>@host.docker.internal:5432/prixio" \
  -e GOTRUE_JWT_SECRET="<your-jwt-secret>" \
  -e GOTRUE_JWT_EXP=3600 \
  -e GOTRUE_SITE_URL="https://lotify.ge" \
  -e GOTRUE_URI_ALLOW_LIST="https://lotify.ge,https://courio.ge" \
  -e GOTRUE_EXTERNAL_GOOGLE_ENABLED=true \
  -e GOTRUE_EXTERNAL_GOOGLE_CLIENT_ID="<google-client-id>" \
  -e GOTRUE_EXTERNAL_GOOGLE_SECRET="<google-client-secret>" \
  supabase/gotrue
```

#### Option B2: Migrate to a different auth (Lucia, Auth.js, etc.)
This is a significant code change and should be its own project, not part of this migration.

---

## Phase 5: Realtime Server Setup

### If using self-hosted Supabase (Option A):
Realtime is included in the Docker setup. Verify it works:

```bash
# Check realtime container
docker compose logs realtime
```

### If using bare PostgreSQL (Option B):

```bash
# Self-hosted Supabase Realtime
docker run -d \
  --name realtime \
  -p 4000:4000 \
  -e DB_HOST="host.docker.internal" \
  -e DB_PORT=5432 \
  -e DB_NAME="prixio" \
  -e DB_USER="postgres" \
  -e DB_PASSWORD="<password>" \
  -e PORT=4000 \
  -e JWT_SECRET="<your-jwt-secret>" \
  -e REPLICATION_MODE="RLS" \
  -e SECURE_CHANNELS=true \
  supabase/realtime
```

### Verify Realtime works

```typescript
// Quick test script
import { createClient } from '@supabase/supabase-js';

const supabase = createClient('https://db.lotify.ge', '<anon-key>');
const channel = supabase.channel('test');
channel
  .on('broadcast', { event: 'test' }, (payload) => console.log(payload))
  .subscribe((status) => console.log('Status:', status));
```

---

## Phase 6: Storage Migration

### If using self-hosted Supabase (Option A):
Storage metadata is restored from the dump. You need to migrate the actual files.

```bash
# Download all files from Supabase Storage
# Use the Supabase JS client or API

# For each bucket, download files
node -e "
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const supabase = createClient('$SUPABASE_URL', '$SERVICE_ROLE_KEY');

async function downloadAll() {
  const { data: buckets } = await supabase.storage.listBuckets();
  for (const bucket of buckets) {
    const { data: files } = await supabase.storage.from(bucket.name).list();
    for (const file of files) {
      const { data } = await supabase.storage.from(bucket.name).download(file.name);
      // Save to local filesystem
      fs.writeFileSync('/opt/storage/' + bucket.name + '/' + file.name, Buffer.from(await data.arrayBuffer()));
    }
  }
}
downloadAll();
"

# Upload to self-hosted storage (volume mount)
# Copy files to the Docker volume for supabase-storage
docker cp /opt/storage/. supabase-storage:/var/lib/storage/
```

### If using bare PostgreSQL (Option B):
Set up MinIO as an S3-compatible storage:

```bash
docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -v /opt/minio-data:/data \
  -e MINIO_ROOT_USER=prixio \
  -e MINIO_ROOT_PASSWORD=<secure-password> \
  minio/minio server /data --console-address ":9001"
```

> This requires code changes to use MinIO SDK instead of Supabase Storage SDK.

---

## Phase 7: RLS Policies Verification

RLS policies are PostgreSQL-native and should work identically on self-hosted.

```sql
-- Verify all policies are in place
SELECT schemaname, tablename, policyname, permissive, cmd
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Test a policy (as an authenticated user)
SET request.jwt.claims = '{"sub": "user-uuid-here", "role": "authenticated"}';
SET ROLE authenticated;

-- Try to select from a table with RLS
SELECT * FROM public.orders LIMIT 1;

-- Reset
RESET ROLE;
RESET request.jwt.claims;
```

### Common RLS issues after migration:
- `auth.uid()` function must exist (included in self-hosted Supabase, must be created manually for bare PG)
- `auth.jwt()` function must exist
- `SECURITY DEFINER` functions with `SET search_path = ''` should work as-is

---

## Phase 8: Application Configuration Changes

### Update connection strings

```bash
# Old (Supabase Cloud)
SUPABASE_URL=https://abc123.supabase.co
DATABASE_URL=postgresql://postgres.abc123:password@aws-0-eu-central-1.pooler.supabase.com:6543/postgres

# New (Self-hosted Supabase)
SUPABASE_URL=https://db.lotify.ge
DATABASE_URL=postgresql://postgres:password@localhost:5432/postgres

# New (Bare PostgreSQL)
DATABASE_URL=postgresql://postgres:password@localhost:5432/prixio
# No SUPABASE_URL -- you'd need to update client code
```

### Update Supabase client initialization

```typescript
// If using self-hosted Supabase, only URL changes
const supabase = createClient(
  'https://db.lotify.ge',  // Changed from abc123.supabase.co
  '<new-anon-key>',        // Generated during self-hosted setup
);

// If using bare PostgreSQL, significant code changes needed
// Replace Supabase client with direct PostgreSQL client (drizzle, kysely, etc.)
```

---

## Phase 9: Cutover

### 9.1 Pre-cutover checklist

- [ ] All data migrated and verified (row counts match)
- [ ] Auth working on new system
- [ ] Realtime working on new system
- [ ] Storage files migrated
- [ ] RLS policies verified
- [ ] Application tested against new database
- [ ] Monitoring set up on new system
- [ ] Backup configured on new system

### 9.2 Cutover procedure

```bash
# 1. Put application in maintenance mode
# Update your app to show maintenance page

# 2. Take final snapshot from Supabase (capture any last-minute data)
pg_dump "$SOURCE_DB" \
  --format=custom \
  --no-owner \
  --no-privileges \
  --exclude-schema='supabase_*' \
  --file=supabase-final-export.dump

# 3. Restore final snapshot
pg_restore --verbose --no-owner --no-privileges --clean --if-exists \
  --dbname="$TARGET_DB" supabase-final-export.dump

# 4. Update application environment variables to point to new database

# 5. Restart application
docker compose restart  # or your restart command

# 6. Remove maintenance mode

# 7. Verify everything works
```

### 9.3 Monitor

```bash
# Watch application logs for errors
docker compose logs -f

# Monitor PostgreSQL
psql -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
psql -c "SELECT * FROM pg_stat_user_tables ORDER BY n_live_tup DESC;"
```

---

## Rollback Plan

**Critical:** Keep the Supabase Cloud project active for at least 30 days after migration.

### Immediate rollback (during cutover)

1. Stop the application
2. Revert environment variables to Supabase Cloud URLs
3. Restart the application
4. Verify Supabase Cloud is serving traffic

### Post-cutover rollback (within 30 days)

1. Stop the application
2. Export any new data from self-hosted to Supabase:
   ```bash
   # Dump only data created after migration
   pg_dump "$TARGET_DB" --data-only --file=new-data.sql
   # Manually apply to Supabase (careful with conflicts)
   ```
3. Revert environment variables
4. Restart the application

### After 30 days

If stable, you can:
1. Pause the Supabase project (keeps data but stops compute)
2. Eventually delete the Supabase project (irreversible)

---

## Backup Strategy for Self-Hosted

Set up automated backups immediately:

```bash
# Create backup script
cat > /opt/scripts/backup-postgres.sh << 'SCRIPT'
#!/bin/bash
set -euo pipefail

BACKUP_DIR="/opt/backups/postgres"
RETENTION_DAYS=14
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p "$BACKUP_DIR"

# Full dump
pg_dump -U postgres -Fc postgres > "$BACKUP_DIR/postgres-$DATE.dump"

# Compress
gzip "$BACKUP_DIR/postgres-$DATE.dump"

# Remove old backups
find "$BACKUP_DIR" -name "*.dump.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: postgres-$DATE.dump.gz"
SCRIPT

chmod +x /opt/scripts/backup-postgres.sh

# Add to cron (daily at 3 AM)
echo "0 3 * * * /opt/scripts/backup-postgres.sh >> /var/log/postgres-backup.log 2>&1" | crontab -
```

### Off-site backup (recommended)

```bash
# Sync backups to Hetzner Storage Box or S3
# Add to the backup script:
rclone sync /opt/backups/postgres remote:prixio-backups/postgres/
```

---

## Post-Migration Checklist

- [ ] All tables present with correct row counts
- [ ] All RLS policies working
- [ ] Auth (login, signup, OAuth) working
- [ ] Realtime subscriptions working
- [ ] Storage (file upload, download) working
- [ ] PostGIS queries working (Courio)
- [ ] TBC Pay webhook processing working
- [ ] Lotify-Courio webhook integration working
- [ ] Automated backups configured and tested
- [ ] Monitoring and alerting set up
- [ ] Connection pooling configured
- [ ] PostgreSQL tuned for workload
- [ ] SSL/TLS on database connections
- [ ] Supabase Cloud project kept active (30-day safety net)
- [ ] Documentation updated
- [ ] Team briefed on new ops procedures
