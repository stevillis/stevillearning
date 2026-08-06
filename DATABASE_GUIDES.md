# Database Operations & Maintenance Guide

This guide provides instructions for backing up (exporting), restoring (importing), and synchronizing the PostgreSQL database for the Stevillis Learning project.

---

## Prerequisites

- **PostgreSQL Client Tools**: Ensure `psql`, `pg_dump`, `createdb`, and `dropdb` are installed and available in your system's `PATH`.
- **Python Environment**: Activated virtual environment (`.venv`) with Django installed.
- **Connection Details**: Access to Host, Port, User, Password, and Database Name (`stevillearning`).

---

## 1. Backup (Export Data)

### From Railway

To backup the production database from Railway:

> **PowerShell**

```powershell
# Syntax: pg_dump postgresql://<USER>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME> -f <OUTPUT_FILE>

# Example:
pg_dump postgresql://postgres:PGPASSWORD@monorail.proxy.rlwy.net:51892/stevillearning -f backup-28-06-2025.sql
```

### From Supabase

To backup the database from Supabase:

> **PowerShell**

```powershell
# Syntax: $env:PGPASSWORD="<PASSWORD>"; pg_dump -U <USER> -h <HOST> -p <PORT> <DB_NAME> -f <OUTPUT_FILE>

# Example:
$env:PGPASSWORD="your_password"; pg_dump -U postgres -h aws-0-sa-east-1.pooler.supabase.com -p 6543 postgres -f backup-supabase.sql
```

### From Local (Development)

To backup your local database:

> **PowerShell**

```powershell
# Syntax: pg_dump -U <USER> -h localhost -p <PORT> <DB_NAME> -f <OUTPUT_FILE>

# Example:
pg_dump -U postgres -h localhost -p 5432 stevillearning -f backup-local.sql
```

---

## 2. Restore (Import Data)

### To Local Environment

To import a backup file into your local database:

> **PowerShell / CMD**

```powershell
# Syntax: psql -U <USER> -h localhost -p <PORT> -d <DB_NAME> -f <INPUT_FILE>

# Example:
$env:PGPASSWORD="postgres"; psql -U postgres -h localhost -p 5432 -d stevillearning -f backup-28-06-2025.sql
```

### To Supabase (Remote)

To import a backup file into Supabase:

> **PowerShell**

```powershell
# Syntax: psql -h <HOST> -U <USER> -p <PORT> -d <DB_NAME> -f <INPUT_FILE>

# Example:
psql -h aws-0-sa-east-1.pooler.supabase.com -U postgres.asdfghjklçpoiuytrewq -p 5432 -d postgres -f backup-local.sql
```

---

## 3. Django Synchronization (Post-Restore Step)

After importing a database backup into local or remote PostgreSQL, Django may report unapplied migrations (e.g., `You have 21 unapplied migration(s)...`) because the `django_migrations` table records were not populated or were skipped during restore.

If your database tables (`course`, `institution`, `certification`, etc.) are already populated from the SQL dump:

> **PowerShell**

```powershell
# Mark all app migrations as applied without executing DDL statements:
python manage.py migrate --fake

# Or specifically for learning_hub:
python manage.py migrate learning_hub --fake
```

---

## 4. Troubleshooting

### Unapplied Migrations Alert (`You have X unapplied migration(s)`)

- **Cause**: Django checks the `django_migrations` table against physical migration files in `learning_hub/migrations/`. If the SQL dump did not populate `django_migrations`, Django considers all migrations pending.
- **Solution**: Run `python manage.py migrate --fake` as documented in **Section 3**.

### Encoding Issues (Windows UTF-8)

Sometimes backups created on Windows or transferred between systems may throw `ERROR: invalid byte sequence for encoding "UTF8": 0xff`.

**Solution:**
Convert the file encoding to UTF-8 using PowerShell before importing:

> **PowerShell**

```powershell
# Syntax: Get-Content <ORIGINAL_FILE> | Out-File -Encoding utf8 <NEW_FILE>

# Example:
Get-Content backup-28-06-2025.sql | Out-File -Encoding utf8 backup-28-06-2025-utf8.sql
```

Use `backup-28-06-2025-utf8.sql` for the import command.

### TimescaleDB Circular Foreign-Key Warning

When backing up from services like Railway that include TimescaleDB by default, you may see warnings like `pg_dump: warning: there are circular foreign-key constraints on hypertable`.

**Solution:**
This is safe to ignore. To suppress these warnings, exclude internal schemas using `--exclude-schema='_timescaledb_*'`:

> **PowerShell**

```powershell
pg_dump postgresql://... --exclude-schema='_timescaledb_*' -f backup.sql
```

### Authentication Failed for User "postgres"

If you encounter `FATAL: password authentication failed for user "postgres"`:

**Solution:**
Pass the password inline using PowerShell environment variables:

> **PowerShell**

```powershell
$env:PGPASSWORD="your_password"; psql -U postgres -h localhost -p 5432 -d stevillearning -f backup.sql
```

Or force a password prompt (`-W`):

> **PowerShell**

```powershell
psql -U postgres -h localhost -p 5432 -d stevillearning -W -f backup.sql
```

### "Relation already exists" or "Multiple primary keys" Errors

**Cause:**
Importing an SQL dump into a database that already contains tables.

**Solution: Clean Import Workflow**

1. **Drop the existing database:**

   ```powershell
   dropdb -U postgres -h localhost -p 5432 stevillearning
   ```

2. **Create a fresh, empty database:**

   ```powershell
   createdb -U postgres -h localhost -p 5432 stevillearning
   ```

3. **Import your backup SQL file:**

   ```powershell
   $env:PGPASSWORD="postgres"; psql -U postgres -h localhost -p 5432 -d stevillearning -f backup-28-06-2025.sql
   ```

4. **Sync Django migration state:**

   ```powershell
   python manage.py migrate --fake
   ```
