# Quick Supabase PostgreSQL Setup

## 🚀 5-Minute Setup

### 1. Get Connection String
Go to: **Supabase Dashboard → Project Settings → Database → Connection string (URI)**

Copy the connection string that looks like:
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

### 2. Update .env
```bash
DATABASE_URL=postgresql://postgres.[project-ref]:[YOUR_PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
```

### 3. Backup SQLite Data (Optional)
```bash
python3 manage.py dumpdata --natural-foreign --natural-primary \
  --exclude contenttypes --exclude auth.permission \
  --exclude admin.logentry --exclude sessions.session \
  > backup_data.json
```

### 4. Run Migrations
```bash
python3 manage.py migrate
python3 manage.py createsuperuser
```

### 5. Load Data (If Backed Up)
```bash
python3 manage.py loaddata backup_data.json
```

### 6. Test
```bash
python3 manage.py runserver
curl http://localhost:8000/api/v1/posts/
```

## ✅ Done!

Your Django app now uses Supabase PostgreSQL with:
- Full-text search with ranking
- GIN indexes for performance
- Production-ready database
- Managed backups

## 🔍 Verify Database
```bash
python3 manage.py shell -c "from django.db import connection; print('Engine:', connection.settings_dict['ENGINE']); print('Host:', connection.settings_dict['HOST'])"
```

Expected output:
```
Engine: django.db.backends.postgresql
Host: aws-0-[region].pooler.supabase.com
```

## 📚 Full Guide
See `MIGRATE_TO_SUPABASE_POSTGRES.md` for detailed instructions.
