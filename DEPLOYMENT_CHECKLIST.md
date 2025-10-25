# 🚀 Production Deployment Checklist

**Use this checklist before every production deployment**

---

## ✅ PRE-DEPLOYMENT

### Code Quality
- [ ] All tests passing: `python manage.py test`
- [ ] No linting errors: `flake8 .`
- [ ] Code formatted: `black . && isort .`
- [ ] No security vulnerabilities: `safety check`
- [ ] Dependencies updated: `pip list --outdated`

### Configuration
- [ ] Environment variables set in `.env`
- [ ] `DEBUG=False` in production
- [ ] `SECRET_KEY` is strong and unique
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] `CORS_ALLOWED_ORIGINS` set to frontend domains
- [ ] Database credentials secure
- [ ] Redis/Celery configured (if used)

### Security
- [ ] HTTPS enforced
- [ ] Security headers enabled
- [ ] CORS properly configured
- [ ] Rate limiting active
- [ ] Session timeout configured
- [ ] No secrets in code/logs

### Performance
- [ ] Static files collected: `python manage.py collectstatic`
- [ ] Database migrations ready: `python manage.py makemigrations --check`
- [ ] Caching configured
- [ ] Query optimization done
- [ ] Load test passed: `python scripts/load_test.py 50 20`

---

## ✅ DEPLOYMENT

### Build
- [ ] Docker image builds: `docker build -t blog-api .`
- [ ] Image size reasonable (<500MB)
- [ ] No build errors
- [ ] Health check works: `curl http://localhost:8080/api/v1/healthcheck/`

### Deploy
- [ ] Backup database
- [ ] Tag release in Git: `git tag v1.x.x`
- [ ] Push to ECR: `./push_to_ecr.sh`
- [ ] Deploy to App Runner: `./DEPLOY_TO_APPRUNNER.sh`
- [ ] Monitor deployment logs

### Verify
- [ ] Health check passes: `curl https://your-app/api/v1/healthcheck/`
- [ ] API endpoints work: `curl https://your-app/api/v1/posts/`
- [ ] CORS works from frontend
- [ ] Authentication works
- [ ] Database migrations applied
- [ ] Static files served correctly

---

## ✅ POST-DEPLOYMENT

### Monitoring
- [ ] Check CloudWatch logs
- [ ] Verify metrics: `curl https://your-app/api/v1/metrics/`
- [ ] Check error rates
- [ ] Monitor response times
- [ ] Verify auto-scaling works

### Testing
- [ ] Smoke tests pass: `./deploy/smoke-tests.sh`
- [ ] Critical user flows work
- [ ] Load test in production: `python scripts/load_test.py 20 10`
- [ ] No 5xx errors
- [ ] Response times < 200ms

### Documentation
- [ ] Update CHANGELOG.md
- [ ] Document any breaking changes
- [ ] Update API documentation
- [ ] Notify team of deployment

---

## 🔄 ROLLBACK PLAN

If deployment fails:

1. **Immediate Actions**
   - [ ] Revert App Runner to previous deployment
   - [ ] Check health endpoint
   - [ ] Verify database integrity

2. **Investigation**
   - [ ] Check CloudWatch logs
   - [ ] Review error messages
   - [ ] Identify root cause

3. **Communication**
   - [ ] Notify team
   - [ ] Update status page
   - [ ] Document incident

4. **Fix and Redeploy**
   - [ ] Fix issue locally
   - [ ] Test thoroughly
   - [ ] Deploy again

---

## 📊 SUCCESS CRITERIA

Deployment is successful when:

- ✅ Health check returns 200
- ✅ Error rate < 0.1%
- ✅ Response time < 200ms
- ✅ All critical endpoints working
- ✅ No database errors
- ✅ Monitoring dashboards green
- ✅ Load test passes

---

## 🎯 QUICK COMMANDS

```bash
# Pre-deployment
python manage.py test
python scripts/load_test.py 10 10
./verify_critical_fixes.sh

# Deployment
docker build -t blog-api .
./push_to_ecr.sh
./DEPLOY_TO_APPRUNNER.sh

# Post-deployment
curl https://your-app/api/v1/healthcheck/
curl https://your-app/api/v1/metrics/
./deploy/smoke-tests.sh

# Rollback
# Use AWS Console to revert to previous deployment
```

---

**Last Updated:** January 2025  
**Version:** 1.0
