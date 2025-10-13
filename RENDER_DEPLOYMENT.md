# Deploy Django to Render with Docker

## 🚀 Quick Deploy

### Option 1: Using render.yaml (Recommended)

1. **Push to GitHub:**
   ```bash
   git add Dockerfile .dockerignore render.yaml
   git commit -m "Add Render deployment configuration"
   git push
   ```

2. **Connect to Render:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click **New** → **Blueprint**
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml` and create services

3. **Set Environment Variables:**
   - `DATABASE_URL`: Your Supabase PostgreSQL connection string
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_API_KEY`: Your Supabase service role key
   - `SUPABASE_BUCKET`: Your storage bucket name
   - `SITE_URL`: Your Render app URL (e.g., `https://your-app.onrender.com`)
   - `NEXTJS_URL`: Your Next.js frontend URL
   - `CORS_ALLOWED_ORIGINS`: Comma-separated allowed origins

### Option 2: Manual Setup

1. **Create Web Service:**
   - Go to Render Dashboard
   - Click **New** → **Web Service**
   - Connect your repository
   - Select **Docker** as environment

2. **Configure Build:**
   - **Docker Command:** (leave empty, uses Dockerfile CMD)
   - **Region:** Oregon (or closest to you)
   - **Plan:** Starter ($7/month) or Free

3. **Add Environment Variables:**
   ```
   SECRET_KEY=<generate-with-openssl-rand-hex-32>
   DEBUG=False
   ALLOWED_HOSTS=.onrender.com
   DATABASE_URL=postgresql://postgres.[ref]:[pass]@aws-0-[region].pooler.supabase.com:6543/postgres
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_API_KEY=your-service-role-key
   SUPABASE_BUCKET=your-bucket-name
   SITE_URL=https://your-app.onrender.com
   NEXTJS_URL=https://your-frontend.vercel.app
   CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```

4. **Deploy:**
   - Click **Create Web Service**
   - Render will build and deploy automatically

---

## 🔧 Dockerfile Explained

### Multi-Stage Build

**Stage 1: Builder**
- Installs build dependencies
- Installs Python packages with `pip install --user`
- Packages stored in `/root/.local`

**Stage 2: Final**
- Copies only Python packages from builder
- Sets `PATH` and `PYTHONPATH` to find installed packages
- Runs `collectstatic` to gather static files
- Creates non-root user for security
- Runs gunicorn with 4 workers

### Key Features

✅ **Multi-stage build** - Smaller final image (300MB vs 800MB)  
✅ **Non-root user** - Security best practice  
✅ **Health check** - Automatic restart if unhealthy  
✅ **Optimized layers** - Faster rebuilds  
✅ **Production-ready** - Gunicorn with proper workers  

---

## 🗄️ Database Options

### Option 1: Supabase PostgreSQL (Recommended)
- Already configured in your project
- Free tier available
- Managed backups
- Global CDN
- Set `DATABASE_URL` to Supabase connection string

### Option 2: Render PostgreSQL
- Uncomment database section in `render.yaml`
- Render will auto-create and link database
- $7/month for Starter plan
- Automatic backups

---

## 📊 Post-Deployment

### Run Migrations
```bash
# SSH into Render shell
render shell your-service-name

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Or use Render Dashboard:
- Go to **Shell** tab
- Run commands directly

### Verify Deployment
```bash
curl https://your-app.onrender.com/api/v1/healthcheck/
curl https://your-app.onrender.com/api/v1/posts/
```

---

## 🔍 Troubleshooting

### Build Fails: "ModuleNotFoundError: No module named 'django'"
**Solution:** Already fixed in Dockerfile with proper PATH and PYTHONPATH

### Static Files Not Loading
**Solution:** 
- Ensure `collectstatic` runs in Dockerfile
- Check `STATIC_ROOT` in settings.py
- Verify Whitenoise is in MIDDLEWARE

### Database Connection Error
**Solution:**
- Verify `DATABASE_URL` format
- Check Supabase connection string
- Ensure `psycopg2-binary` in requirements.txt

### 502 Bad Gateway
**Solution:**
- Check logs in Render Dashboard
- Verify gunicorn is running
- Check health check endpoint

---

## 🚦 Health Check Endpoint

Already implemented in your project:
```python
# blog/views_seo.py
@api_view(['GET'])
def healthcheck(request):
    return Response({'status': 'healthy'})
```

Endpoint: `/api/v1/healthcheck/`

---

## 📈 Performance Tips

1. **Enable Redis Caching:**
   - Add Redis service in Render
   - Set `REDIS_URL` environment variable

2. **Use CDN:**
   - Cloudflare for static files
   - Reduces server load

3. **Scale Workers:**
   - Upgrade to higher plan
   - Increase gunicorn workers

4. **Monitor Performance:**
   - Use Render metrics
   - Add Sentry for error tracking

---

## 💰 Cost Estimate

### Free Tier
- Web Service: Free (sleeps after 15 min inactivity)
- Database: Use Supabase free tier
- **Total: $0/month**

### Production
- Web Service: $7/month (Starter)
- Database: Supabase free tier or Render $7/month
- **Total: $7-14/month**

---

## 🔐 Security Checklist

- [x] `DEBUG=False` in production
- [x] Strong `SECRET_KEY` generated
- [x] `ALLOWED_HOSTS` configured
- [x] HTTPS enabled (automatic on Render)
- [x] Non-root user in Docker
- [x] Environment variables for secrets
- [x] CORS properly configured
- [x] Rate limiting enabled

---

## 📚 Resources

- [Render Docs](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## ✅ Deployment Checklist

- [ ] Dockerfile created
- [ ] .dockerignore created
- [ ] render.yaml configured
- [ ] Environment variables set
- [ ] Database connected (Supabase)
- [ ] Pushed to GitHub
- [ ] Connected to Render
- [ ] Migrations run
- [ ] Superuser created
- [ ] API endpoints tested
- [ ] Health check working

**Your Django API is ready for production! 🎉**
