# 🚀 AWS App Runner Deployment - Execution Guide

## ✅ Status: READY TO DEPLOY

All fixes applied. All scripts created. Follow this guide step-by-step.

---

## 📋 PHASE 0: Pre-Flight Checks

### Step 1: Verify Docker
```bash
docker info
```
**Expected:** Docker info displays (no errors)  
**If fails:** Start Docker Desktop

### Step 2: Verify AWS CLI
```bash
aws sts get-caller-identity
```
**Expected:** Shows your AWS account ID  
**If fails:** Run `aws configure`

### Step 3: Verify Scripts
```bash
ls -la *.sh
```
**Expected:** All 7 scripts listed with execute permissions

### Step 4: Make Scripts Executable (if needed)
```bash
chmod +x *.sh
```

---

## 🧪 PHASE 1: Local Testing (5 minutes)

### Run Local Tests
```bash
./test_local_deployment.sh
```

### What to Look For:
- ✅ "Docker image built successfully"
- ✅ "Container started"
- ✅ "GET request successful"
- ✅ "HEAD request successful"
- ✅ "Response time is good"
- ✅ "ALL LOCAL TESTS PASSED!"

### If Tests Fail:
```bash
# Check Docker logs
docker logs $(docker ps -lq)

# Common fixes:
# - Ensure port 8080 is free
# - Check .env file has all variables
# - Restart Docker Desktop
```

**⚠️ DO NOT PROCEED IF LOCAL TESTS FAIL!**

---

## 📦 PHASE 2: Push to ECR (3 minutes)

### Run ECR Push
```bash
./push_to_ecr.sh
```

### What to Look For:
- ✅ "Successfully authenticated to ECR"
- ✅ "ECR repository exists"
- ✅ "Images tagged"
- ✅ "Pushed v3"
- ✅ "Pushed latest"
- ✅ "IMAGES PUSHED TO ECR SUCCESSFULLY!"

### If Push Fails:
```bash
# Re-authenticate
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  816709078703.dkr.ecr.us-east-1.amazonaws.com

# Retry
./push_to_ecr.sh
```

---

## 🚀 PHASE 3: Deploy to App Runner (1 minute)

### Run Deployment
```bash
./deploy_to_apprunner.sh
```

### What to Look For:
- ✅ "IAM role exists"
- ✅ "Service created" or "Service update initiated"
- ✅ "DEPLOYMENT INITIATED SUCCESSFULLY!"

### Save Service Info:
The script will display:
- Service ARN
- Service URL

**Copy these for later use!**

---

## 📊 PHASE 4: Monitor Deployment (5-7 minutes)

### Run Monitor Script
```bash
./monitor_deployment.sh
```

### Expected Progress:
```
[00:00] Status: OPERATION_IN_PROGRESS
[00:10] Status: OPERATION_IN_PROGRESS
[00:20] Status: OPERATION_IN_PROGRESS
...
[06:40] Status: RUNNING ✅
Health check test: 200 OK ✅
DEPLOYMENT SUCCESSFUL!
```

### If Stuck (>15 minutes):
```bash
# Stop monitoring (Ctrl+C)
# Run troubleshooting
./troubleshoot.sh
```

---

## ✅ PHASE 5: Verify Deployment (1 minute)

### Run Verification
```bash
./verify_deployment.sh
```

### What to Look For:
- ✅ "Service Status: RUNNING"
- ✅ "GET health check: 200 OK"
- ✅ "HEAD health check: 200 OK"
- ✅ "Response time: <500ms"
- ✅ "API endpoints accessible"
- ✅ "ALL VERIFICATIONS PASSED!"

### Manual Test (Optional):
```bash
# Get your service URL from Phase 3
curl https://YOUR-SERVICE-URL/api/v1/healthcheck/

# Expected: {"status":"healthy","service":"django-blog-api"}
```

---

## 📝 PHASE 6: Generate Report (30 seconds)

### Generate Report
```bash
./generate_deployment_report.sh
```

### What It Creates:
- `DEPLOYMENT_REPORT.md` - Complete deployment documentation

### View Report:
```bash
cat DEPLOYMENT_REPORT.md
```

---

## 🎉 SUCCESS!

If all phases completed:

### Your API is Live At:
```
https://YOUR-SERVICE-ID.us-east-1.awsapprunner.com
```

### Test Your API:
```bash
# Health check
curl https://YOUR-SERVICE-URL/api/v1/healthcheck/

# List posts
curl https://YOUR-SERVICE-URL/api/v1/posts/

# API docs
open https://YOUR-SERVICE-URL/api/v1/docs/
```

---

## 🔧 Troubleshooting

### If Any Phase Fails:

#### 1. Run Troubleshoot Script
```bash
./troubleshoot.sh
```

#### 2. Check CloudWatch Logs
```bash
aws logs tail /aws/apprunner/django-blog-api-v3 --follow --region us-east-1
```

#### 3. Common Issues:

**Health Check Failing:**
- Verify path is `/api/v1/healthcheck/`
- Check environment variables are set
- Review CloudWatch logs

**Container Won't Start:**
- Test locally again: `./test_local_deployment.sh`
- Check Dockerfile syntax
- Verify all dependencies in requirements.txt

**500 Errors:**
- Check DATABASE_URL is correct
- Verify all environment variables set
- Check for Python errors in logs

**400 Errors:**
- Verify ALLOWED_HOSTS includes `*` or `.awsapprunner.com`

---

## 📊 Quick Commands Reference

### Check Service Status
```bash
aws apprunner list-services --region us-east-1 \
  --query "ServiceSummaryList[?ServiceName=='django-blog-api-v3'].[ServiceName,Status,ServiceUrl]" \
  --output table
```

### View Logs
```bash
aws logs tail /aws/apprunner/django-blog-api-v3 --follow --region us-east-1
```

### Update Service
```bash
./deploy_to_apprunner.sh
# Choose "update" when prompted
```

### Delete Service (if needed)
```bash
aws apprunner delete-service \
  --service-arn YOUR-SERVICE-ARN \
  --region us-east-1
```

---

## 🎯 Deployment Checklist

Track your progress:

- [ ] Phase 0: Pre-flight checks completed
- [ ] Phase 1: Local tests passed
- [ ] Phase 2: Image pushed to ECR
- [ ] Phase 3: Deployment initiated
- [ ] Phase 4: Service status RUNNING
- [ ] Phase 5: Verification passed
- [ ] Phase 6: Report generated
- [ ] Service URL saved
- [ ] API tested and working

---

## 💡 Tips

1. **Keep Terminal Open:** Don't close terminal during deployment
2. **Save Service URL:** You'll need it for frontend integration
3. **Monitor First Deployment:** Watch CloudWatch logs for any issues
4. **Test Thoroughly:** Verify all endpoints work before going live
5. **Document Everything:** Keep DEPLOYMENT_REPORT.md for reference

---

## 🔄 Update Deployment

To update your deployed service:

```bash
# 1. Make code changes
# 2. Test locally
./test_local_deployment.sh

# 3. Build new image with new tag
docker build -t django-blog-api:v4 .

# 4. Push to ECR
docker tag django-blog-api:v4 \
  816709078703.dkr.ecr.us-east-1.amazonaws.com/django-blog-api:v4
docker push 816709078703.dkr.ecr.us-east-1.amazonaws.com/django-blog-api:v4

# 5. Update service
./deploy_to_apprunner.sh
# Choose "update" and specify new image tag
```

---

## 📞 Need Help?

### Resources:
- **Troubleshooting:** `./troubleshoot.sh`
- **Complete Guide:** `COMPLETE_DEPLOYMENT_FIXES.md`
- **AWS Docs:** https://docs.aws.amazon.com/apprunner/

### Common Commands:
```bash
# Verify deployment ready
python3 verify_deployment_ready.py

# Check all fixes applied
grep -r "@csrf_exempt" blog/views_simple_health.py

# Test health check locally
docker run -p 8080:8080 --env-file .env django-blog-api:test
curl http://localhost:8080/api/v1/healthcheck/
```

---

## 🎊 Next Steps After Deployment

1. **Update Frontend:**
   ```bash
   # In your Next.js .env
   NEXT_PUBLIC_API_URL=https://YOUR-SERVICE-URL
   ```

2. **Configure Custom Domain (Optional):**
   ```bash
   aws apprunner associate-custom-domain \
     --service-arn YOUR-ARN \
     --domain-name yourdomain.com \
     --region us-east-1
   ```

3. **Set Up Monitoring:**
   - CloudWatch alarms for health check failures
   - Error rate monitoring
   - Response time tracking

4. **Security Hardening:**
   - Update ALLOWED_HOSTS to specific domain
   - Enable AWS WAF
   - Configure VPC connector if needed

---

## 💰 Cost Tracking

Monitor your costs:
```bash
# View App Runner costs
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --filter file://filter.json
```

**Expected:** $10-30/month

---

## ✅ Deployment Complete!

Once all phases pass, your Django Blog API is:
- ✅ Live on AWS App Runner
- ✅ Accessible via HTTPS
- ✅ Health checks passing
- ✅ Auto-scaling enabled
- ✅ Production-ready

**Service URL:** https://YOUR-SERVICE-ID.us-east-1.awsapprunner.com

**Congratulations! 🎉**

---

**Start Deployment:** Run `./test_local_deployment.sh` to begin!
