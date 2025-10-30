# Domain Configuration Summary

## Updated Configuration

### Production Domains
- **Backend API**: `https://backend.zaryableather.com`
- **Frontend**: `https://zaryableather.com` and `https://www.zaryableather.com`
- **Elastic Beanstalk**: `django-blog-api-prod.eba-uiwnbpqr.us-east-1.elasticbeanstalk.com`

### Files Updated

1. **`.env`** - Production environment variables
   - `DEBUG=False`
   - `SITE_URL=https://backend.zaryableather.com`
   - `NEXTJS_URL=https://zaryableather.com`
   - `ALLOWED_HOSTS` - Added production domains
   - `CORS_ALLOWED_ORIGINS` - Added frontend domains
   - `CSRF_TRUSTED_ORIGINS` - Added all domains
   - `USE_HTTPS=True`
   - `SECURE_PROXY_SSL_HEADER_ENABLED=True`

2. **`.env.example`** - Updated with production examples

3. **`leather_api/settings.py`**
   - Updated default `ALLOWED_HOSTS`
   - Updated default `CORS_ALLOWED_ORIGINS`
   - Changed `SECURE_SSL_REDIRECT = True`
   - Changed `USE_HTTPS` default to `True`

4. **`blog/seo_utils.py`** - Updated fallback URL to `https://backend.zaryableather.com`

5. **`blog/feeds.py`** - Updated fallback URLs to `https://backend.zaryableather.com`

### Security Settings Enabled
- ✅ SSL/HTTPS redirect enabled
- ✅ Secure proxy headers configured
- ✅ Secure cookies enabled
- ✅ CORS configured for frontend domains
- ✅ CSRF protection for all domains

### Next Steps

1. **Route 53 DNS Configuration**:
   - Point `backend.zaryableather.com` → Elastic Beanstalk endpoint
   - Point `zaryableather.com` → Frontend (Vercel/hosting)
   - Point `www.zaryableather.com` → Frontend

2. **SSL Certificates**:
   - Configure SSL certificate in Elastic Beanstalk for backend
   - Ensure frontend has SSL configured

3. **Test Deployment**:
   ```bash
   # Test health check
   curl https://backend.zaryableather.com/api/v1/healthcheck/
   
   # Test CORS
   curl -H "Origin: https://zaryableather.com" \
        -H "Access-Control-Request-Method: GET" \
        -X OPTIONS https://backend.zaryableather.com/api/v1/posts/
   ```

4. **Frontend Configuration**:
   - Update frontend API base URL to `https://backend.zaryableather.com`
   - Update environment variables in Vercel/hosting platform

### Environment Variables Checklist
Ensure these are set in Elastic Beanstalk:
- [x] `SECRET_KEY`
- [x] `DEBUG=False`
- [x] `ALLOWED_HOSTS`
- [x] `DATABASE_URL`
- [x] `SUPABASE_URL`
- [x] `SUPABASE_API_KEY`
- [x] `SUPABASE_BUCKET`
- [x] `REDIS_URL`
- [x] `SITE_URL=https://backend.zaryableather.com`
- [x] `NEXTJS_URL=https://zaryableather.com`
- [x] `CORS_ALLOWED_ORIGINS`
- [x] `CSRF_TRUSTED_ORIGINS`
- [x] `USE_HTTPS=True`
- [x] `SECURE_PROXY_SSL_HEADER_ENABLED=True`
