# Migrate Django from SQLite3 to Supabase PostgreSQL

## Step 1: Get Supabase PostgreSQL Connection String

1. Go to your Supabase project: https://supabase.com/dashboard
2. Click on **Project Settings** (gear icon)
3. Go to **Database** section
4. Find **Connection string** → **URI** format
5. Copy the connection string (it looks like):
   ```
   postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```

## Step 2: Install PostgreSQL Adapter

```bash
pip install psycopg2-binary dj-database-url
```

Add to `requirements.txt`:
```
psycopg2-binary==2.9.9
dj-database-url==2.1.0
```

## Step 3: Update .env File

Update your `.env` file with the Supabase PostgreSQL connection string:

```bash
# Replace with your actual Supabase PostgreSQL connection string
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

**Important:** The connection string format should be:
```
postgresql://postgres.[project-ref]:[YOUR_PASSWORD]@[host]:6543/postgres
```

## Step 4: Verify settings.py Configuration

Your `settings.py` already has the correct configuration:

```python
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}
```

This uses `django-environ` which automatically parses the `DATABASE_URL` from `.env`.

## Step 5: Backup SQLite Data (Optional)

If you have existing data in SQLite that you want to migrate:

```bash
# Dump data from SQLite
python3 manage.py dumpdata --natural-foreign --natural-primary \
  --exclude contenttypes --exclude auth.permission \
  --exclude admin.logentry --exclude sessions.session \
  > backup_data.json
```

## Step 6: Test PostgreSQL Connection

```bash
# Test connection
python3 manage.py check --database default

# Show database info
python3 manage.py shell -c "from django.db import connection; print('Database:', connection.settings_dict['NAME']); print('Engine:', connection.settings_dict['ENGINE'])"
```

## Step 7: Run Migrations on PostgreSQL

```bash
# Create all tables in PostgreSQL
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser
```

## Step 8: Load Data (If You Backed Up)

```bash
# Load data into PostgreSQL
python3 manage.py loaddata backup_data.json
```

## Step 9: Verify Everything Works

```bash
# Start server
python3 manage.py runserver

# Test endpoints
curl http://localhost:8000/api/v1/posts/
curl http://localhost:8000/api/v1/categories/
curl http://localhost:8000/api/v1/settings/
```

## Step 10: Update .gitignore

Ensure SQLite database is ignored:

```
# .gitignore
db.sqlite3
*.sqlite3
backup_data.json
```

## Step 11: Clean Up (Optional)

After verifying everything works:

```bash
# Remove SQLite database
rm db.sqlite3

# Remove backup file
rm backup_data.json
```

---

## Troubleshooting

### Connection Error: "could not connect to server"

**Solution:** Check your Supabase connection string format:
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

### SSL Error

Add `?sslmode=require` to your connection string:
```
DATABASE_URL=postgresql://user:pass@host:6543/postgres?sslmode=require
```

### Migration Errors

If you get migration conflicts:
```bash
# Reset migrations (CAUTION: Only for fresh setup)
python3 manage.py migrate --fake-initial
```

### Check Current Database

```bash
python3 manage.py shell
>>> from django.db import connection
>>> print(connection.settings_dict['ENGINE'])
>>> print(connection.settings_dict['NAME'])
```

---

## Benefits of PostgreSQL over SQLite

✅ **Full-text search** with ranking (already implemented in `blog/search.py`)  
✅ **GIN indexes** for better search performance  
✅ **Concurrent writes** without locking  
✅ **JSON field support** with queries  
✅ **Production-ready** for deployment  
✅ **Managed backups** via Supabase  

---

## Production Deployment

For Render deployment, add to environment variables:
```
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

Render will automatically use this instead of creating its own PostgreSQL instance.

---

## Verification Checklist

- [ ] PostgreSQL connection string added to `.env`
- [ ] `psycopg2-binary` installed
- [ ] Migrations run successfully
- [ ] Superuser created
- [ ] API endpoints working
- [ ] Search API using PostgreSQL full-text search
- [ ] Admin panel accessible
- [ ] SQLite database removed (optional)

---

## Next Steps

1. Test all API endpoints
2. Verify search functionality (now uses PostgreSQL full-text search)
3. Check admin panel
4. Deploy to production with Supabase PostgreSQL
