# Redis & Celery Integration Guide

## Overview

This project uses **Upstash Redis** for caching and **Celery** for asynchronous task processing with production-grade configuration.

## Features

✅ **Redis Caching** - High-performance distributed cache with connection pooling
✅ **Celery Tasks** - Async task processing with automatic retry and monitoring
✅ **Rate Limiting** - Built-in task rate limiting
✅ **Idempotent Tasks** - Prevent duplicate task execution
✅ **Error Handling** - Automatic retry with exponential backoff
✅ **Monitoring** - Task event logging and metrics

## Configuration

### Environment Variables

```bash
# Redis (Upstash)
REDIS_URL=rediss://default:PASSWORD@host.upstash.io:6379

# Celery (Upstash Redis)
CELERY_BROKER_URL=rediss://default:PASSWORD@host.upstash.io:6379
CELERY_RESULT_BACKEND=rediss://default:PASSWORD@host.upstash.io:6379
```

### Redis Features

- **Connection Pooling**: Max 50 connections with health checks
- **Compression**: Zlib compression for reduced memory
- **Timeouts**: 5-second connection/socket timeouts
- **Graceful Degradation**: Fails gracefully if Redis is unavailable
- **Key Prefix**: All keys prefixed with `blog:`

### Celery Features

- **Retry Logic**: Automatic retry with exponential backoff
- **Rate Limiting**: 100 tasks per minute default
- **Task Timeout**: 30-minute hard limit, 25-minute soft limit
- **Worker Management**: Auto-restart after 1000 tasks
- **Result Expiry**: Results expire after 1 hour

## Usage

### 1. Test Connection

```bash
python manage.py test_redis_celery
```

### 2. Start Celery Worker

```bash
# Development
celery -A leather_api worker -l info

# Production
celery -A leather_api worker -l info --concurrency=4 --max-tasks-per-child=1000
```

### 3. Start Celery Beat (Scheduled Tasks)

```bash
celery -A leather_api beat -l info
```

### 4. Monitor Tasks

```bash
# Flower (Web UI)
pip install flower
celery -A leather_api flower
```

## Cache Usage

### Using Cache Decorator

```python
from core.cache_utils import cache_response

@cache_response(timeout=600, key_prefix='posts')
def get_popular_posts():
    return Post.objects.filter(views_count__gt=1000)
```

### Manual Cache Operations

```python
from django.core.cache import cache

# Set
cache.set('key', 'value', timeout=300)

# Get
value = cache.get('key')

# Delete
cache.delete('key')

# Invalidate pattern (Redis only)
from core.cache_utils import invalidate_pattern
invalidate_pattern('posts:*')
```

## Celery Task Examples

### Basic Task

```python
from celery import shared_task

@shared_task
def send_email(to, subject, body):
    # Send email logic
    return f"Email sent to {to}"
```

### Using Base Task Classes

```python
from core.celery_base import BaseTask, IdempotentTask

@shared_task(base=BaseTask)
def process_data(data_id):
    # Automatic retry on failure
    pass

@shared_task(base=IdempotentTask)
def generate_report():
    # Prevents duplicate execution
    pass
```

### Scheduled Tasks

Configured in `leather_api/celery.py`:

- **Sitemap Regeneration**: Daily at 2:00 AM
- **RSS Feed Refresh**: Daily at 2:30 AM
- **Metrics Aggregation**: Daily at 1:00 AM
- **Trending Keywords**: Daily at 3:00 AM

## Monitoring

### Task Events

All tasks emit events:
- `task_prerun`: Task started
- `task_postrun`: Task completed
- `task_failure`: Task failed
- `task_retry`: Task retrying

### Logs

Check logs in:
- `logs/celery.log` - Celery task logs
- `logs/django.log` - Django application logs

### Metrics

Monitor in Flower dashboard:
- Task success/failure rates
- Task execution time
- Worker status
- Queue length

## Production Deployment

### Docker Compose

```yaml
services:
  celery_worker:
    build: .
    command: celery -A leather_api worker -l info --concurrency=4
    environment:
      - REDIS_URL=${REDIS_URL}
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
    depends_on:
      - redis

  celery_beat:
    build: .
    command: celery -A leather_api beat -l info
    environment:
      - REDIS_URL=${REDIS_URL}
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
```

### Systemd Service

```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/blog_api
ExecStart=/var/www/blog_api/venv/bin/celery -A leather_api worker -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

### Redis Connection Issues

```bash
# Test Redis connection
redis-cli --tls -u $REDIS_URL ping

# Check Django cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')
```

### Celery Not Processing Tasks

1. Check worker is running: `celery -A leather_api inspect active`
2. Check broker connection: `celery -A leather_api inspect stats`
3. Check logs: `tail -f logs/celery.log`

### Performance Issues

- Increase worker concurrency: `--concurrency=8`
- Use separate queues for different task types
- Monitor memory usage and restart workers periodically

## Best Practices

1. **Use task queues** for different priorities
2. **Set timeouts** for all tasks
3. **Monitor task failures** and set up alerts
4. **Use idempotent tasks** for critical operations
5. **Cache frequently accessed data**
6. **Invalidate cache** when data changes
7. **Use compression** for large cached objects
8. **Set appropriate TTLs** for cached data

## Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Django Redis Documentation](https://github.com/jazzband/django-redis)
- [Upstash Redis](https://upstash.com/)
