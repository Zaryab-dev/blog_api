# ✅ Deployment Checklist - SEO Enhancements

Quick checklist for deploying to AWS Elastic Beanstalk.

## 📋 Pre-Deployment

- [ ] All code committed to Git
- [ ] Migrations created (0015, 0016)
- [ ] Tests passing locally
- [ ] `.env` file configured

## 🚀 Deployment

```bash
# 1. Set environment
eb use django-blog-api-prod

# 2. Deploy
eb deploy --timeout 15

# 3. SSH and migrate
eb ssh
cd /var/app/current
source /var/app/venv/*/bin/activate
python manage.py migrate blog
python manage.py populate_leather_keywords
python manage.py fix_blog_urls
exit
```

## ✅ Verification

- [ ] Health status: Green
- [ ] API returns `keywords` field
- [ ] API returns `excerpt` field
- [ ] API returns `reading_time_minutes` field
- [ ] API returns `ebay_product_url` field
- [ ] URLs don't have `/blog/` prefix
- [ ] Schema.org includes keywords
- [ ] Admin shows new fields

## 🧪 Quick Test

```bash
curl https://backend.zaryableather.com/api/v1/posts/ | jq '.[0] | {keywords, excerpt, reading_time_minutes, frontend_url}'
```

**Expected:**
```json
{
  "keywords": ["leather", "care"],
  "excerpt": "Learn how to...",
  "reading_time_minutes": 5,
  "frontend_url": "https://zaryableather.com/post-slug"
}
```

## 🎯 Success

✅ All checks passed → Deployment successful!

See `DEPLOY_ENHANCEMENTS_TO_EB.md` for detailed guide.
