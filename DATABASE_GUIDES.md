# Database Operations & Maintenance Guide - Stévillis Learning Hub

This guide provides instructions for backing up (exporting), restoring (importing), and synchronizing the PostgreSQL database for the Stévillis Learning Hub project, considering a production environment hosted on **Neon** / **Supabase** / **Railway** and local development.

---

## Prerequisites

- **PostgreSQL Client Tools**: Ensure `psql`, `pg_dump`, `createdb`, and `dropdb` are installed and available in your system's `PATH`.
- **Python Environment**: `uv` installed with the virtual environment (`.venv`) initialized (`uv sync`).
- **Connection Details**: Access to Host, Port, User, Password, and Database Name (`stevillearning` for local, or your cloud PostgreSQL connection URI).

---

## 1. Backup (Export Data)

### From Production / Cloud (Neon, Supabase, Railway)

To backup the production database from your cloud provider:

> **PowerShell**

```powershell
# Syntax using connection URI:
pg_dump "postgresql://<USER>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>?sslmode=require" -f <OUTPUT_FILE>

# Example - Neon (Direct Endpoint):
pg_dump "postgresql://neondb_owner:npg_xxxx@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require" -f backup-stevillearning-$(Get-Date -Format "yyyy-MM-dd-HH-mm-ss").sql

# Example - Supabase (Direct Connection):
pg_dump "postgresql://postgres:your_password@db.xxxx.supabase.co:5432/postgres?sslmode=require" -f backup-stevillearning-$(Get-Date -Format "yyyy-MM-dd-HH-mm-ss").sql

# Example - Railway:
pg_dump "postgresql://postgres:your_password@monorail.proxy.rlwy.net:51892/stevillearning" --exclude-schema='_timescaledb_*' -f backup-stevillearning-$(Get-Date -Format "yyyy-MM-dd-HH-mm-ss").sql
```

Alternatively, pass the password via environment variable:

> **PowerShell**

```powershell
# Syntax:
$env:PGPASSWORD="<PASSWORD>"; pg_dump -h <HOST> -U <USER> -p <PORT> -d <DB_NAME> -f <OUTPUT_FILE>

# Example:
$env:PGPASSWORD="your_password"; pg_dump -h ep-cool-name-123456.us-east-2.aws.neon.tech -U neondb_owner -p 5432 neondb -f backup-stevillearning-$(Get-Date -Format "yyyy-MM-dd-HH-mm-ss").sql
```

*Note: For `pg_dump`, using the **Direct endpoint** rather than a Pooled endpoint (`pooler`) is recommended to ensure full compatibility with dump utilities and schema locks.*

#### If encountering Server Version Mismatch (e.g., Server Postgres 18 vs local pg_dump 17)

Run `pg_dump` via Docker with a matching PostgreSQL container image:

> **PowerShell**

```powershell
docker run --rm -v "${PWD}:/backup" postgres:18-alpine pg_dump "postgresql://<USER>:<PASSWORD>@<HOST>/<DB_NAME>?sslmode=require" -f /backup/backup-stevillearning-$(Get-Date -Format "yyyy-MM-dd-HH-mm-ss").sql
```

---

### From Local (Development)

To backup your local PostgreSQL database:

> **PowerShell**

```powershell
# Syntax: pg_dump -U <USER> -h localhost -p <PORT> <DB_NAME> -f <OUTPUT_FILE>

# Example:
$env:PGPASSWORD="postgres"; pg_dump -U postgres -h localhost -p 5432 stevillearning -f backup-local-$(Get-Date -Format "yyyy-MM-dd-HH-mm-ss").sql
```

---

## 2. Restore (Import Data)

### To Local Environment

To import a backup file (from production or another local backup) into your local database:

> **PowerShell**

```powershell
# Syntax: psql -U <USER> -h localhost -p <PORT> -d <DB_NAME> -f <INPUT_FILE>

# Example:
$env:PGPASSWORD="postgres"; psql -U postgres -h localhost -p 5432 -d stevillearning -f backup-stevillearning.sql
```

### To Remote / Production Environment

To import a backup file into your remote PostgreSQL database:

> **PowerShell**

```powershell
# Syntax using connection URI:
psql "postgresql://<USER>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>?sslmode=require" -f <INPUT_FILE>

# Example:
psql "postgresql://neondb_owner:npg_xxxx@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require" -f backup-local.sql
```

---

## 3. Django Synchronization & Post-Restore Setup

After importing a database backup into local or remote PostgreSQL, Django may report unapplied migrations (`You have X unapplied migration(s)...`) because the `django_migrations` table records were either not populated or skipped during restore.

### Synchronizing Migration State

If your database tables (`category`, `institution`, `course`, `certification`, `accounts_*`, etc.) are already populated from the SQL dump:

> **PowerShell / Local Terminal**

```powershell
# Mark all migrations as applied without executing DDL statements:
uv run python manage.py migrate --fake
```

> **On VPS (Docker Container)**

```bash
docker compose exec web python manage.py migrate --fake
```

### Creating Administrative Superuser (If Required)

Because routes in Learning Hub are protected by `@login_required`, ensure you have an administrator user:

> **PowerShell / Local Terminal**

```powershell
uv run python manage.py createsuperuser
```

> **On VPS (Docker Container)**

```bash
docker compose exec web python manage.py createsuperuser
```

### Portfolio RAG Webhook Sync

If courses and certifications were restored or bulk-imported into Learning Hub, they can be synchronized into the portfolio's vector store (`stevillis.com.br`) via webhook or manual sync:

- Changes saved in Learning Hub are automatically broadcasted to `STEVILLIS_WEBHOOK_URL` if configured.
- Alternatively, run `python manage.py sync_learning_hub` from the `stevillis.com.br` project to fetch the latest courses and certifications via REST API.

---

## 4. Troubleshooting

### SSL Requirement (`sslmode=require`)

- **Cause**: Cloud providers like Neon and Supabase require TLS/SSL connections by default.
- **Solution**: Always append `?sslmode=require` to connection URIs (`DATABASE_URL` or `pg_dump` / `psql` connection strings).

### Server Version Mismatch (`pg_dump: error: aborting because of server version mismatch`)

- **Cause**: PostgreSQL client utilities (`pg_dump`) must be of the same or newer major version as the target database server.
- **Solution 1 (Using Docker - Recommended)**:
  Run `pg_dump` using a PostgreSQL container matching the server version:

  > **PowerShell**

  ```powershell
  docker run --rm -v "${PWD}:/backup" postgres:18-alpine pg_dump "postgresql://<USER>:<PASSWORD>@<HOST>/<DB_NAME>?sslmode=require" -f /backup/backup-stevillearning-$(Get-Date -Format "yyyy-MM-dd-HH-mm-ss").sql
  ```

- **Solution 2 (Upgrade local PostgreSQL Client)**:
  Install or upgrade PostgreSQL client binaries on your host machine to match or exceed the remote server version.

### Connection Pooling vs Direct Endpoint

- **Direct Endpoint** (`ep-name.region.aws.neon.tech` or Supabase direct port `5432`): Recommended for schema operations, `pg_dump`, and running Django migrations.
- **Pooled Endpoint** (`ep-name-pooler...` or Supabase port `6543`): Recommended for high-concurrency web application runtime connections (`DATABASE_URL`).

### TimescaleDB Circular Foreign-Key Warning

When backing up from cloud services that include TimescaleDB (such as Railway), you may encounter `pg_dump: warning: there are circular foreign-key constraints on hypertable`.

**Solution:**
Pass `--exclude-schema='_timescaledb_*'` to exclude internal schemas:

> **PowerShell**

```powershell
pg_dump "postgresql://<USER>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>" --exclude-schema='_timescaledb_*' -f backup.sql
```

### Unapplied Migrations Alert (`You have X unapplied migration(s)`)

- **Cause**: Django checks the `django_migrations` table against physical migration files in `learning_hub/migrations/` and `accounts/migrations/`.
- **Solution**: Run `uv run python manage.py migrate --fake` as documented in **Section 3**.

### Encoding Issues (Windows UTF-8)

Backups created on Windows or transferred between systems may throw `ERROR: invalid byte sequence for encoding "UTF8": 0xff`.

**Solution:**
Convert the file encoding to UTF-8 using PowerShell before importing:

> **PowerShell**

```powershell
# Convert file to UTF-8
Get-Content backup-stevillearning.sql | Out-File -Encoding utf8 backup-stevillearning-utf8.sql
```

Use `backup-stevillearning-utf8.sql` for the import command.

### Authentication Failed for User "postgres" or Cloud DB Owner

If password authentication fails:

**Solution:**
Pass the password inline using PowerShell environment variables:

> **PowerShell**

```powershell
$env:PGPASSWORD="your_password"; psql -U postgres -h localhost -p 5432 -d stevillearning -f backup.sql
```

Or pass the full connection URI enclosed in double quotes:

> **PowerShell**

```powershell
psql "postgresql://user:password@host:port/dbname?sslmode=require" -f backup.sql
```

### "Relation already exists" or "Multiple primary keys" Errors

**Cause:**
Importing an SQL dump into a database that already contains existing tables.

**Solution: Clean Import Workflow**

1. **Drop the existing local database:**

   ```powershell
   dropdb -U postgres -h localhost -p 5432 stevillearning
   ```

1. **Create a fresh, empty database:**

   ```powershell
   createdb -U postgres -h localhost -p 5432 stevillearning
   ```

1. **Import your backup SQL file:**

   ```powershell
   $env:PGPASSWORD="postgres"; psql -U postgres -h localhost -p 5432 -d stevillearning -f backup.sql
   ```

1. **Sync Django migration state:**

   ```powershell
   uv run python manage.py migrate --fake
   ```
