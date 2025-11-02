# 🚀 Deploy Enhancements to AWS Elastic Beanstalk

Quick guide to deploy the new SEO enhancements and eBay product URL field to your existing EB environment.

## 📋 What's Being Deployed

### New Features
- ✅ 10 enhanced SEO fields (keywords, excerpt, reading_time_minutes, etc.)
- ✅ eBay product URL field
- ✅ Full SEO automation
- ✅ URL structure fixes (removed /blog/ prefix)
- ✅ Schema.org improvements
- ✅ ISR revalidation support

### Database Changes
- ✅ Migration 0015: SEO enhancements
- ✅ Migration 0016: eBay product URL

---

## 🔧 Pre-Deployment Steps

### 1. Verify Local Changes

```bash
# Check migrations
python manage.py showmigrations blog

# Expected output:
# [X] 0015_add_seo_enhancements
# [X] 0016_add_ebay_product_url
```

### 2. Test Locally

```bash
# Run tests
python test_seo_enhancements.py

# Expected: ✅ ALL TESTS PASSED
```

### 3. Commit Changes

```bash
git add .
git commit -m "Add SEO enhancements and eBay product URL field"
git push origin main
```

---

## 🚀 Deployment Steps

### Step 1: Set Environment

```bash
eb use django-blog-api-prod
```

### Step 2: Check Current Status

```bash
eb status
```

**Expected:**
```
Environment details for: django-blog-api-prod
  Application name: django-blog-api
  Region: us-east-1
  Status: Ready
  Health: Green
```

### Step 3: Deploy

```bash
eb deploy --timeout 15
```

**Expected Output:**
```
Creating application version archive "app-XXXXX".
Uploading blog_api/app-XXXXX.zip to S3...
Environment update is starting.
...
INFO: Successfully launched environment: django-blog-api-prod
```

### Step 4: Run Migrations

```bash
# SSH into instance
eb ssh

# Run migrations
cd /var/app/current
source /var/app/venv/*/bin/activate
python manage.py migrate blog

# Expected output:
# Running migrations:
#   Applying blog.0015_add_seo_enhancements... OK
#   Applying blog.0016_add_ebay_product_url... OK

# Exit SSH
exit
```

### Step 5: Populate Data

```bash
# SSH back in
eb ssh

cd /var/app/current
source /var/app/venv/*/bin/activate

# Populate keywords
python manage.py populate_leather_keywords

# Fix URLs
python manage.py fix_blog_urls

# Exit
exit
```

---

## ✅ Verification

### 1. Check Health

```bash
eb health
```

**Expected:** Green ✅

### 2. Test API

```bash
# Test enhanced fields
curl https://backend.zaryableather.com/api/v1/posts/ | jq '.[0] | {
  keywords,
  excerpt,
  reading_time_minutes,
  frontend_url,
  canonical_url,
  ebay_product_url,
  structured_data_valid,
  main_image_alt_text,
  revalidate_path
}'
```

**Expected Response:**
```json
{
  "keywords": ["leather", "care"],
  "excerpt": "Learn how to...",
  "reading_time_minutes": 5,
  "frontend_url": "https://zaryableather.com/post-slug",
  "canonical_url": "https://zaryableather.com/post-slug",
  "ebay_product_url": "",
  "structured_data_valid": true,
  "main_image_alt_text": "Leather products",
  "revalidate_path": "/post-slug"
}
```

### 3. Test Single Post

```bash
curl https://backend.zaryableather.com/api/v1/posts/mcm-cognac-leather-puffer-jacket-fur-collar/ | jq '{
  title,
  keywords,
  excerpt,
  reading_time_minutes,
  frontend_url,
  schema_org: .schema_org.keywords
}'
```

### 4. Check Admin

Visit: https://backend.zaryableather.com/admin/blog/post/

Verify:
- ✅ New fields visible
- ✅ Keywords populated
- ✅ eBay URL field present
- ✅ URLs correct (no /blog/ prefix)

---

## 🔄 Alternative: Deploy Without SSH

If you can't SSH, use Django management commands via EB config:

### Create `.ebextensions/03_migrations.config`

```yaml
container_commands:
  01_migrate:
    command: "source /var/app/venv/*/bin/activate && python manage.py migrate --noinput"
    leader_only: true
  02_populate_keywords:
    command: "source /var/app/venv/*/bin/activate && python manage.py populate_leather_keywords"
    leader_only: true
  03_fix_urls:
    command: "source /var/app/venv/*/bin/activate && python manage.py fix_blog_urls"
    leader_only: true
```

Then deploy:
```bash
eb deploy --timeout 15
```

---

## 📊 Post-Deployment Checklist

- [ ] Migrations applied successfully
- [ ] Keywords populated for all posts
- [ ] URLs fixed (no /blog/ prefix)
- [ ] Health check passing
- [ ] API returns new fields
- [ ] Admin shows new fields
- [ ] Schema.org valid
- [ ] Frontend URLs correct

---

## 🐛 Troubleshooting

### Issue: Migrations Not Applied

```bash
eb ssh
cd /var/app/current
source /var/app/venv/*/bin/activate
python manage.py migrate blog --fake-initial
```

### Issue: Keywords Not Populated

```bash
eb ssh
cd /var/app/current
source /var/app/venv/*/bin/activate
python manage.py populate_leather_keywords
```

### Issue: URLs Still Have /blog/

```bash
eb ssh
cd /var/app/current
source /var/app/venv/*/bin/activate
python manage.py fix_blog_urls
```

### Issue: 500 Errors

```bash
# Check logs
eb logs

# Look for migration errors or missing fields
```

---

## 📝 Environment Variables

No new environment variables needed! All enhancements use existing settings:

```bash
NEXTJS_URL=https://zaryableather.com  # Already set ✅
SITE_URL=https://backend.zaryableather.com  # Already set ✅
```

---

## 🔄 Rollback Plan

If something goes wrong:

```bash
# Rollback to previous version
eb deploy --version app-294f-251101_003205905962

# Or rollback migrations
eb ssh
cd /var/app/current
source /var/app/venv/*/bin/activate
python manage.py migrate blog 0014_remove_comment_comment_post_idx_and_more
```

---

## 📊 Expected Results

### Before Deployment
```json
{
  "title": "Post Title",
  "slug": "post-slug",
  "canonical_url": "https://zaryableather.com/blog/post-slug/"
}
```

### After Deployment
```json
{
  "title": "Post Title",
  "slug": "post-slug",
  "excerpt": "Short preview...",
  "keywords": ["leather", "care"],
  "reading_time_minutes": 5,
  "frontend_url": "https://zaryableather.com/post-slug",
  "canonical_url": "https://zaryableather.com/post-slug",
  "ebay_product_url": "",
  "structured_data_valid": true,
  "main_image_alt_text": "Leather products",
  "revalidate_path": "/post-slug",
  "schema_org": {
    "@type": "BlogPosting",
    "keywords": "leather, care",
    "url": "https://zaryableather.com/post-slug"
  }
}
```

---

## 🎯 Quick Deploy Commands

```bash
# Full deployment in 5 commands
eb use django-blog-api-prod
eb deploy --timeout 15
eb ssh
# Inside SSH:
cd /var/app/current && source /var/app/venv/*/bin/activate
python manage.py migrate blog
python manage.py populate_leather_keywords
python manage.py fix_blog_urls
exit
# Verify:
curl https://backend.zaryableather.com/api/v1/posts/ | jq '.[0].keywords'
```

---

## ✅ Success Criteria

Deployment is successful when:

1. ✅ Health status is Green
2. ✅ API returns all new fields
3. ✅ Keywords populated for posts
4. ✅ URLs don't have /blog/ prefix
5. ✅ Schema.org includes keywords
6. ✅ Admin shows new fields
7. ✅ No 500 errors in logs

---

## 📚 Related Documentation

- `SEO_AUTOMATION_COMPLETE.md` - Full automation guide
- `EBAY_PRODUCT_URL_FIELD.md` - eBay field documentation
- `URL_STRUCTURE_FIX.md` - URL changes explained
- `ENHANCED_FIELDS_INTEGRATION.md` - Next.js integration

---

**Ready to deploy!** 🚀

Run: `eb deploy --timeout 15`
