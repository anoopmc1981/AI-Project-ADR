# ADR Scanner - Next Steps to Deploy

## 🎯 Your Goal
Deploy the ADR Scanner application to AWS and get it running.

## ⚡ Quick Start (5 minutes)

### 1. Run the OIDC Fix Script

**Choose ONE option:**

#### Option A: Git Bash (Recommended for Windows)
```bash
cd /d/Project/Git-AI-Projects/AI-Project-ADR
bash final-oidc-fix.sh
```

#### Option B: PowerShell
```powershell
cd d:\Project\Git-AI-Projects\AI-Project-ADR
.\final-oidc-fix.ps1
```

**Output:** You'll see a **Role ARN** like:
```
arn:aws:iam::123456789012:role/GitHubActionsADRDeployRole
```

### 2. Update GitHub Secret (2 minutes)

1. Go to: https://github.com/anoopmc1981/AI-Project-ADR/settings/secrets/actions
2. Click **AWS_IAM_ROLE**
3. Replace the value with the **Role ARN** from step 1
4. Click **Update secret**

### 3. Re-run GitHub Actions Workflow (30-40 minutes)

1. Go to: https://github.com/anoopmc1981/AI-Project-ADR/actions
2. Click the **red ❌ failed workflow** (usually at the top)
3. Click **Re-run jobs** → **Re-run all jobs**
4. Watch it run

**What to expect:**
- ✅ Checkout code
- ✅ Setup Python
- ✅ **Configure AWS Credentials** ← This should now work!
- ✅ Install SAM CLI
- ✅ Build SAM application
- ✅ Deploy to AWS (~10-15 minutes)
- ✅ Deploy frontend
- ✅ Show CloudFront URL

**Deployment complete!** 🎉

---

## 📋 What Gets Deployed

### Backend (AWS)
- **6 Lambda Functions** - Core logic for ADR scanning, detection, alerts
- **4 DynamoDB Tables** - Store users, ranges, alerts, logs
- **API Gateway** - REST API for frontend
- **EventBridge** - Schedule daily range calculations
- **SNS/SQS** - Queue for WhatsApp alerts
- **Cognito** - User authentication

### Frontend (CDN)
- **S3 Bucket** - Static files storage
- **CloudFront** - Global CDN distribution
- **Dashboard** - React-based UI for monitoring ADRs

### Integrations
- **Fyers API** - Get real-time stock prices
- **WhatsApp** - Send alerts via Twilio
- **Bedrock AI** - Analyze ADR patterns

---

## 🔍 Verification Checklist

After deployment succeeds, verify:

**Step 1: Check GitHub Actions**
- [ ] Workflow shows all ✅
- [ ] Final step shows CloudFront URL

**Step 2: Check AWS Resources**
```bash
# Check CloudFormation stack
aws cloudformation describe-stacks \
  --stack-name adr-scanner-dev \
  --region ap-south-1

# Check Lambda functions
aws lambda list-functions --region ap-south-1

# Check DynamoDB tables
aws dynamodb list-tables --region ap-south-1

# Check S3 buckets
aws s3 ls
```

**Step 3: Access the Dashboard**
- [ ] Copy CloudFront URL from workflow
- [ ] Open in browser
- [ ] Should see login page
- [ ] Try logging in with Cognito user

**Step 4: Check Each Service**
- [ ] API Gateway endpoints working
- [ ] DynamoDB tables populated
- [ ] Lambda functions are running
- [ ] CloudWatch logs show no errors

---

## 🚨 If Something Goes Wrong

### Error: "Credentials could not be loaded"
1. Verify GitHub secret was updated: https://github.com/anoopmc1981/AI-Project-ADR/settings/secrets/actions
2. Make sure there are no extra spaces in the Role ARN
3. Wait 30 seconds and re-run workflow

### Error: "SAM build failed"
1. Check Python version: `python --version` (should be 3.9+)
2. Check requirements installed: `pip install -r backend/requirements.txt`
3. Check Lambda function code has no syntax errors

### Error: "Cannot access dashboard"
1. Check CloudFront distribution exists: `aws cloudfront list-distributions`
2. Check S3 bucket has frontend files: `aws s3 ls s3://adr-scanner-frontend-dev-*/`
3. Check CloudFront is enabled

### Error: "API not responding"
1. Check API Gateway exists: `aws apigateway get-rest-apis --region ap-south-1`
2. Check Lambda functions: `aws lambda list-functions --region ap-south-1`
3. Check Lambda logs: `aws logs tail /aws/lambda/AuthHandler --region ap-south-1 --follow`

---

## 📚 Documentation Files

For more details, see:

| File | Purpose |
|------|---------|
| `OIDC_FIX_INSTRUCTIONS.md` | Detailed OIDC setup (read if script doesn't work) |
| `DEPLOYMENT_CHECKLIST.md` | Pre-deployment verification checklist |
| `README.md` | Project overview |
| `DEPLOYMENT.md` | Detailed deployment guide |
| `DEVELOPMENT_SETUP.md` | Local development setup |
| `GITHUB_ACTIONS_SETUP.md` | GitHub Actions configuration |

---

## 🎓 What Happens During Deployment

```
GitHub Action Triggers
        ↓
Checks out code
        ↓
Sets up Python 3.11
        ↓
Assumes AWS IAM Role via OIDC ← FIXED!
        ↓
Builds SAM template
        ↓
Deploys to CloudFormation
        ├── Creates Lambda functions
        ├── Creates DynamoDB tables
        ├── Creates API Gateway
        └── Creates EventBridge rules
        ↓
Uploads frontend to S3
        ↓
Invalidates CloudFront
        ↓
Tests deployment
        ↓
Shows URLs ✅
```

---

## 📊 Expected Resource Costs

**First month (approximate):**
- Lambda: $0-5 (1M free requests/month)
- DynamoDB: $0-5 (25GB free storage)
- API Gateway: $1-3 (1M free requests/month)
- S3/CloudFront: $0-2 (small file sizes)
- **Total: ~$5-20/month**

---

## 🔐 Security Notes

The deployment includes:
- ✅ OIDC authentication (no static credentials)
- ✅ Cognito for user auth (not stored in GitHub)
- ✅ IAM policies with least privilege
- ✅ DynamoDB encryption
- ✅ CloudFront HTTPS
- ✅ Lambda VPC isolation (optional)

---

## ✨ Next: After Deployment

Once everything is running:

1. **Configure Fyers API credentials** - Add to Lambda environment variables
2. **Set up WhatsApp bot** - Configure Twilio account
3. **Test ADR scanning** - Trigger manual Lambda test
4. **Monitor logs** - Use CloudWatch for debugging
5. **Scale up** - Add more markets, users, or features

---

## 🚀 TL;DR - Just Run This

```bash
# 1. Fix OIDC
cd /d/Project/Git-AI-Projects/AI-Project-ADR
bash final-oidc-fix.sh

# 2. Update GitHub secret with output from above
# (Go to: https://github.com/anoopmc1981/AI-Project-ADR/settings/secrets/actions)

# 3. Re-run workflow
# (Go to: https://github.com/anoopmc1981/AI-Project-ADR/actions)

# 4. Wait for deployment
# Check logs in GitHub Actions

# 5. Access dashboard
# Use CloudFront URL from workflow output
```

---

**You're all set! Deploy now and let me know if you hit any issues. 🎉**

