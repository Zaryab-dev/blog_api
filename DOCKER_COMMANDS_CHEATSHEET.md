# 🐳 Docker Commands Cheatsheet

Quick reference for managing your Django Blog API Docker container.

---

## 🚀 Quick Start

```bash
# Build image
docker build -t django-blog-api .

# Run container
docker run -d -p 8000:8000 --env-file .env --name django-blog-api-test django-blog-api

# View logs
docker logs -f django-blog-api-test

# Test
curl http://localhost:8000/api/v1/healthcheck/
```

---

## 🔨 Build Commands

```bash
# Build image
docker build -t django-blog-api .

# Build without cache
docker build --no-cache -t django-blog-api .

# Build and tag for ECR
docker build -t django-blog-api -t $ECR_URI:latest .

# View images
docker images django-blog-api
```

---

## ▶️ Run Commands

```bash
# Run in background
docker run -d -p 8000:8000 --env-file .env --name django-blog-api-test django-blog-api

# Run with specific env vars
docker run -d -p 8000:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=your-key \
  -e DATABASE_URL=postgresql://... \
  --name django-blog-api-test \
  django-blog-api

# Run in foreground (see logs)
docker run -p 8000:8000 --env-file .env --name django-blog-api-test django-blog-api

# Run with volume mount (for development)
docker run -d -p 8000:8000 --env-file .env -v $(pwd):/app --name django-blog-api-test django-blog-api
```

---

## 📋 Container Management

```bash
# List running containers
docker ps

# List all containers
docker ps -a

# Stop container
docker stop django-blog-api-test

# Start container
docker start django-blog-api-test

# Restart container
docker restart django-blog-api-test

# Remove container
docker rm django-blog-api-test

# Force remove running container
docker rm -f django-blog-api-test
```

---

## 📊 Logs & Monitoring

```bash
# View logs
docker logs django-blog-api-test

# Follow logs (live)
docker logs -f django-blog-api-test

# Last 50 lines
docker logs --tail 50 django-blog-api-test

# Logs since 10 minutes ago
docker logs --since 10m django-blog-api-test

# Container stats
docker stats django-blog-api-test

# Inspect container
docker inspect django-blog-api-test

# Check health
docker inspect --format='{{.State.Health.Status}}' django-blog-api-test
```

---

## 🔧 Execute Commands

```bash
# Run Django management commands
docker exec django-blog-api-test python manage.py migrate
docker exec django-blog-api-test python manage.py collectstatic --noinput
docker exec django-blog-api-test python manage.py createsuperuser

# Interactive shell
docker exec -it django-blog-api-test bash
docker exec -it django-blog-api-test python manage.py shell

# Check Python packages
docker exec django-blog-api-test pip list

# Check Django version
docker exec django-blog-api-test python -c "import django; print(django.get_version())"

# Run tests
docker exec django-blog-api-test python manage.py test
```

---

## 🧹 Cleanup Commands

```bash
# Stop and remove container
docker stop django-blog-api-test && docker rm django-blog-api-test

# Remove image
docker rmi django-blog-api

# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove everything (careful!)
docker system prune -a
```

---

## 🔄 Rebuild Workflow

```bash
# Complete rebuild
docker stop django-blog-api-test 2>/dev/null
docker rm django-blog-api-test 2>/dev/null
docker build -t django-blog-api .
docker run -d -p 8000:8000 --env-file .env --name django-blog-api-test django-blog-api
docker logs -f django-blog-api-test
```

---

## 🧪 Testing Commands

```bash
# Health check
curl http://localhost:8000/api/v1/healthcheck/

# Landing page
curl http://localhost:8000/

# API endpoints
curl http://localhost:8000/api/v1/posts/
curl http://localhost:8000/api/v1/categories/
curl http://localhost:8000/api/v1/tags/
curl http://localhost:8000/api/v1/authors/

# Search
curl http://localhost:8000/api/v1/search/?q=jacket

# Admin (should redirect to login)
curl -I http://localhost:8000/admin/
```

---

## 🌐 Docker Compose

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f
docker-compose logs -f web

# Execute commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild and start
docker-compose up --build
```

---

## 📦 AWS ECR Commands

```bash
# Create repository
aws ecr create-repository --repository-name django-blog-api

# Get repository URI
ECR_URI=$(aws ecr describe-repositories --repository-names django-blog-api --query 'repositories[0].repositoryUri' --output text)

# Login to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URI

# Tag image
docker tag django-blog-api:latest $ECR_URI:latest

# Push to ECR
docker push $ECR_URI:latest

# Pull from ECR
docker pull $ECR_URI:latest
```

---

## 🔍 Debugging Commands

```bash
# Check if container is running
docker ps --filter name=django-blog-api-test

# Check container health
docker inspect --format='{{json .State.Health}}' django-blog-api-test | jq

# View environment variables
docker exec django-blog-api-test env

# Check disk usage
docker exec django-blog-api-test df -h

# Check processes
docker exec django-blog-api-test ps aux

# Network inspection
docker network inspect bridge

# Port mapping
docker port django-blog-api-test
```

---

## 💾 Backup & Export

```bash
# Export container as image
docker commit django-blog-api-test django-blog-api-backup

# Save image to file
docker save django-blog-api > django-blog-api.tar

# Load image from file
docker load < django-blog-api.tar

# Export container filesystem
docker export django-blog-api-test > container-backup.tar
```

---

## 🎯 One-Liner Commands

```bash
# Quick rebuild and run
docker stop django-blog-api-test; docker rm django-blog-api-test; docker build -t django-blog-api . && docker run -d -p 8000:8000 --env-file .env --name django-blog-api-test django-blog-api

# Check if healthy
docker inspect --format='{{.State.Health.Status}}' django-blog-api-test

# Get container IP
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' django-blog-api-test

# View resource usage
docker stats --no-stream django-blog-api-test

# Count running containers
docker ps -q | wc -l
```

---

## 📝 Useful Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Docker aliases
alias dps='docker ps'
alias dpsa='docker ps -a'
alias di='docker images'
alias dlog='docker logs -f'
alias dexec='docker exec -it'
alias dstop='docker stop'
alias drm='docker rm'
alias drmi='docker rmi'

# Django Blog API specific
alias blog-build='docker build -t django-blog-api .'
alias blog-run='docker run -d -p 8000:8000 --env-file .env --name django-blog-api-test django-blog-api'
alias blog-logs='docker logs -f django-blog-api-test'
alias blog-stop='docker stop django-blog-api-test && docker rm django-blog-api-test'
alias blog-shell='docker exec -it django-blog-api-test bash'
alias blog-test='curl http://localhost:8000/api/v1/healthcheck/'
```

---

## 🆘 Common Issues

### Container won't start
```bash
# Check logs
docker logs django-blog-api-test

# Check if port is in use
lsof -i :8000

# Try different port
docker run -d -p 8001:8000 --env-file .env --name django-blog-api-test django-blog-api
```

### Can't connect to database
```bash
# Check DATABASE_URL
docker exec django-blog-api-test env | grep DATABASE_URL

# Test database connection
docker exec django-blog-api-test python manage.py check --database default
```

### Static files not loading
```bash
# Check if collectstatic ran
docker logs django-blog-api-test | grep "static files"

# Manually run collectstatic
docker exec django-blog-api-test python manage.py collectstatic --noinput

# Check static files directory
docker exec django-blog-api-test ls -la /app/staticfiles/
```

---

## ✨ Pro Tips

1. **Use .dockerignore** - Speeds up builds
2. **Layer caching** - Order Dockerfile commands by change frequency
3. **Multi-stage builds** - Smaller final images
4. **Health checks** - Automatic monitoring
5. **Named volumes** - Persist data
6. **Docker Compose** - Easier local development
7. **Environment files** - Manage configs easily
8. **Logs** - Always check logs first when debugging

---

## 📚 Resources

- **Docker Docs**: https://docs.docker.com/
- **Django Deployment**: https://docs.djangoproject.com/en/4.2/howto/deployment/
- **Gunicorn**: https://docs.gunicorn.org/
- **WhiteNoise**: http://whitenoise.evans.io/

---

**Current Status**: ✅ Container running and healthy
**Quick Test**: `curl http://localhost:8000/api/v1/healthcheck/`
