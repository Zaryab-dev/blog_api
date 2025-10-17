# Production Deployment Checklist

## Pre-Deployment

### Environment Configuration
- [ ] Copy `.env.example` to `.env.production`
- [ ] Set `DEBUG=False`
- [ ] Set strong `SECRET_KEY` (generate new one)
- [ ] Configure `ALLOWED_HOSTS` with production domain
- [ ] Set `SUPABASE_URL` (production instance)
- [ ] Set `SUPABASE_API_KEY` (production key)
- [ ] Set `SUPABASE_BUCKET` (production bucket)
- [ ] Configure `DATABASE_URL` (PostgreSQL recommended)
- [ ] Set `REDIS_URL` for caching
- [ ] Configure email settings (SMTP)
- [ ] Set `SITE_URL` to production domain
- [ ] Set `NEXTJS_URL` to frontend domain
- [ ] Configure `CORS_ALLOWED_ORIGINS`
- [ ] Configure `CSRF_TRUSTED_ORIGINS`
- [ ] Set `SENTRY_DSN` for error tracking (optional)

### Security Checks
- [ ] Verify `DEBUG=False`
- [ ] Confirm no hardcoded secrets in code
- [ ] Check `.env` is in `.gitignore`
- [ ] Verify CSRF protection is enabled
- [ ] Test SSL/TLS certificates
- [ ] Enable `SECURE_SSL_REDIRECT=True`
- [ ] Set secure cookie flags
- [ ] Configure HSTS headers
- [ ] Review CORS settings
- [ ] Test rate limiting

### Database
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Verify database backups are configured
- [ ] Test database connection pooling
- [ ] Check query performance

### Static Files
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Verify static files are served correctly
- [ ] Configure CDN (if using)
- [ ] Test image uploads to Supabase

### Testing
- [ ] Run test suite: `python manage.py test`
- [ ] Test API endpoints manually
- [ ] Verify CKEditor uploads work with CSRF
- [ ] Test error pages (404, 500)
- [ ] Check logging is working
- [ ] Test rate limiting
- [ ] Verify caching is working

## Deployment

### Application Server
- [ ] Deploy code to production server
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Set environment variables
- [ ] Start application server (Gunicorn/uWSGI)
- [ ] Configure process manager (systemd/supervisor)
- [ ] Set up auto-restart on failure

### Web Server
- [ ] Configure Nginx/Apache
- [ ] Set up SSL certificates (Let's Encrypt)
- [ ] Configure reverse proxy
- [ ] Set up static file serving
- [ ] Configure request timeouts
- [ ] Enable gzip compression

### Background Tasks
- [ ] Start Celery workers
- [ ] Start Celery beat (scheduler)
- [ ] Verify Redis is running
- [ ] Test async tasks

### Monitoring
- [ ] Set up application monitoring (Sentry)
- [ ] Configure log aggregation
- [ ] Set up uptime monitoring
- [ ] Configure alerts for errors
- [ ] Set up performance monitoring

## Post-Deployment

### Verification
- [ ] Test homepage loads
- [ ] Test API endpoints
- [ ] Test admin panel login
- [ ] Test file uploads
- [ ] Verify HTTPS is working
- [ ] Check error pages
- [ ] Test search functionality
- [ ] Verify caching is working

### Performance
- [ ] Run load tests
- [ ] Check API response times (<100ms target)
- [ ] Verify database query counts
- [ ] Test CDN performance
- [ ] Check memory usage
- [ ] Monitor CPU usage

### Security
- [ ] Run security scan: `python manage.py check --deploy`
- [ ] Test CSRF protection
- [ ] Verify rate limiting
- [ ] Check for exposed secrets
- [ ] Test authentication
- [ ] Review access logs

### Documentation
- [ ] Update API documentation
- [ ] Document deployment process
- [ ] Create runbook for common issues
- [ ] Document rollback procedure

## Rollback Plan

If issues are detected:

1. **Immediate Actions:**
   ```bash
   # Revert to previous version
   git checkout <previous-tag>
   
   # Restart services
   sudo systemctl restart gunicorn
   sudo systemctl restart celery
   ```

2. **Database Rollback:**
   ```bash
   # If migrations were run
   python manage.py migrate <app> <previous_migration>
   ```

3. **Verify Rollback:**
   - Test critical endpoints
   - Check error logs
   - Verify database integrity

## Emergency Contacts

- **DevOps Lead:** [Contact Info]
- **Database Admin:** [Contact Info]
- **Security Team:** [Contact Info]
- **On-Call Engineer:** [Contact Info]

## Monitoring URLs

- **Application:** https://yourdomain.com
- **Admin Panel:** https://yourdomain.com/admin/
- **API Docs:** https://yourdomain.com/api/docs/
- **Health Check:** https://yourdomain.com/health/
- **Sentry:** https://sentry.io/your-project/
- **Uptime Monitor:** [Your monitoring service]

## Success Criteria

- [ ] All API endpoints responding
- [ ] Response times <100ms
- [ ] Error rate <0.1%
- [ ] Uptime >99.9%
- [ ] No security vulnerabilities
- [ ] All tests passing
- [ ] Monitoring active
- [ ] Backups configured

---

**Last Updated:** [Date]
**Deployed By:** [Name]
**Version:** [Version Number]
