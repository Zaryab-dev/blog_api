# Quick Start Guide - After Security Fixes

## 🚀 Get Running in 5 Minutes

### Step 1: Configure Environment (2 min)

```bash
# Copy the example file
cp .env.example .env

# Edit .env and set these REQUIRED variables:
# - SUPABASE_URL=your_url
# - SUPABASE_API_KEY=your_key
# - SUPABASE_BUCKET=your_bucket
# - SECRET_KEY=generate_new_key
# - DEBUG=True (for development only)
```

### Step 2: Verify Configuration (1 min)

```bash
# Check that everything is configured correctly
python manage.py check

# Run security verification
python test_security_fixes.py
```

### Step 3: Run Migrations (1 min)

```bash
# Apply database migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

### Step 4: Start Development Server (1 min)

```bash
# Start the server
python manage.py runserver

# Visit http://localhost:8000/admin/
# Visit http://localhost:8000/api/docs/
```

---

## ✅ Verification Checklist

After starting the server, verify:

- [ ] Admin panel loads: http://localhost:8000/admin/
- [ ] API docs load: http://localhost:8000/api/docs/
- [ ] Can login to admin
- [ ] No error messages in console
- [ ] File uploads work (test in admin)

---

## 🔧 Common Issues

### "Missing required environment variables"
**Solution:** Check your `.env` file has all required variables set.

### "CSRF verification failed"
**Solution:** For CKEditor uploads, update the configuration (see SECURITY_FIXES.md).

### "Invalid Supabase credentials"
**Solution:** Verify credentials in Supabase dashboard match your `.env` file.

---

## 📚 Full Documentation

- **Environment Setup:** `ENVIRONMENT_SETUP.md`
- **Security Fixes:** `SECURITY_FIXES.md`
- **Deployment:** `DEPLOYMENT_CHECKLIST.md`
- **Phase 1 Summary:** `PHASE1_COMPLETE.md`

---

## 🎯 Production Deployment

When ready for production:

1. Set `DEBUG=False` in `.env.production`
2. Use strong, unique `SECRET_KEY`
3. Configure production database (PostgreSQL)
4. Set up Redis for caching
5. Follow `DEPLOYMENT_CHECKLIST.md`

---

**Need Help?** Check the documentation files or run `python test_security_fixes.py`
