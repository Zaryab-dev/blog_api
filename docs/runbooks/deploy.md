# Deployment Runbook

## Pre-Deployment Checklist

- [ ] All tests passing in CI
- [ ] Code reviewed and approved
- [ ] Database migrations reviewed (no destructive changes)
- [ ] Environment variables updated in Secrets Manager
- [ ] Backup completed within last 24 hours
- [ ] Stakeholders notified of deployment window

## Deployment Steps

### 1. Automated Deployment (Recommended)

**Trigger:** Merge to `main` branch

```bash
# CI/CD will automatically:
# 1. Run tests
# 2. Build Docker image
# 3. Push to ECR
# 4. Run migrations
# 5. Deploy to ECS
# 6. Run smoke tests
# 7. Rollback on failure
```

**Monitor:** GitHub Actions workflow

### 2. Manual Deployment (Emergency)

```bash
# 1. Build and push image
docker build -t leather-api:$(git rev-parse --short HEAD) .
docker tag leather-api:$(git rev-parse --short HEAD) $ECR_REGISTRY/leather-api:latest
docker push $ECR_REGISTRY/leather-api:latest

# 2. Run migrations
aws ecs run-task \
  --cluster leather-api-cluster \
  --task-definition leather-api-task \
  --launch-type FARGATE \
  --overrides '{"containerOverrides":[{"name":"django","command":["python","manage.py","migrate"]}]}'

# 3. Update ECS service
aws ecs update-service \
  --cluster leather-api-cluster \
  --service leather-api-service \
  --force-new-deployment

# 4. Wait for deployment
aws ecs wait services-stable \
  --cluster leather-api-cluster \
  --services leather-api-service

# 5. Run smoke tests
./deploy/smoke-tests.sh
```

## Post-Deployment

### Verification

```bash
# 1. Check health
curl https://api.zaryableather.com/api/v1/healthcheck/

# 2. Check logs
aws logs tail /ecs/leather-api --follow

# 3. Check metrics
# Visit CloudWatch dashboard

# 4. Test critical paths
curl https://api.zaryableather.com/api/v1/posts/
curl https://api.zaryableather.com/api/v1/trending/
```

### Monitoring (First 30 minutes)

- [ ] Error rate < 1%
- [ ] Response time p95 < 500ms
- [ ] CPU usage < 70%
- [ ] Memory usage < 80%
- [ ] No 5xx errors
- [ ] Celery tasks processing

## Rollback Procedure

### Automatic Rollback

If smoke tests fail, CI/CD automatically rolls back to previous task definition.

### Manual Rollback

```bash
# 1. Get previous task definition
PREVIOUS_TASK=$(aws ecs describe-services \
  --cluster leather-api-cluster \
  --services leather-api-service \
  --query 'services[0].deployments[1].taskDefinition' \
  --output text)

# 2. Update service
aws ecs update-service \
  --cluster leather-api-cluster \
  --service leather-api-service \
  --task-definition $PREVIOUS_TASK \
  --force-new-deployment

# 3. Verify rollback
aws ecs wait services-stable \
  --cluster leather-api-cluster \
  --services leather-api-service

# 4. Run smoke tests
./deploy/smoke-tests.sh
```

## Database Migrations

### Safe Migration Strategy

**Two-Phase Deployment:**

**Phase 1: Additive Changes**
```python
# Add new column (nullable)
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='post',
            name='new_field',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
```

Deploy → Backfill data → Deploy Phase 2

**Phase 2: Make Required**
```python
# Make column non-nullable
class Migration(migrations.Migration):
    operations = [
        migrations.AlterField(
            model_name='post',
            name='new_field',
            field=models.CharField(max_length=100),
        ),
    ]
```

### Risky Migrations

**Avoid in single deployment:**
- Dropping columns
- Renaming columns
- Changing column types
- Adding non-nullable columns without defaults

**Instead:** Use two-phase approach with feature flags

## Troubleshooting

### Deployment Stuck

```bash
# Check ECS events
aws ecs describe-services \
  --cluster leather-api-cluster \
  --services leather-api-service \
  --query 'services[0].events[:5]'

# Check task status
aws ecs list-tasks \
  --cluster leather-api-cluster \
  --service-name leather-api-service

# Check task logs
aws logs tail /ecs/leather-api --follow
```

### High Error Rate

```bash
# Check application logs
aws logs filter-pattern '"ERROR"' /ecs/leather-api

# Check Sentry
# Visit Sentry dashboard

# Rollback if critical
./scripts/rollback.sh
```

### Database Connection Issues

```bash
# Check RDS status
aws rds describe-db-instances \
  --db-instance-identifier leather-api-db

# Check security groups
aws ec2 describe-security-groups \
  --group-ids sg-xxx

# Test connection from ECS task
aws ecs execute-command \
  --cluster leather-api-cluster \
  --task <task-id> \
  --container django \
  --command "python manage.py dbshell"
```

## Emergency Contacts

- **On-Call Engineer:** PagerDuty rotation
- **DevOps Lead:** devops@zaryableather.com
- **CTO:** cto@zaryableather.com
- **Slack:** #incidents

## SLA Targets

- **Deployment Time:** < 10 minutes
- **Rollback Time:** < 5 minutes
- **Downtime:** 0 (rolling deployment)
- **Error Rate:** < 0.1% during deployment
