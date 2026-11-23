# ✅ Final Deployment Steps - Ready to Deploy!

## 🎯 Current Status

✅ OIDC Provider created in AWS  
✅ IAM Role created in AWS  
✅ Policy assigned to role  
✅ GitHub secret created  
✅ Workflow file updated  
⏳ **Ready to deploy!**

---

## ⚠️ Important: GitHub Secret Name Check

Your GitHub secret is named: `AWS_IAM_ROLE`

The workflow expects: `AWS_IAM_ROLE_ARN`

### Fix This (2 Options)

#### Option A: Rename GitHub Secret (Recommended)
1. Go to: https://github.com/anoopmc1981/AI-Project-ADR/settings/secrets/actions
2. Find secret: `AWS_IAM_ROLE`
3. Click the **three dots (⋯)** → **Edit**
4. Change name from `AWS_IAM_ROLE` to `AWS_IAM_ROLE_ARN`
5. Click **Update secret**
6. Done! ✅

#### Option B: Update Workflow (Alternative)
If you want to keep the secret name as `AWS_IAM_ROLE`, edit the workflow file:

**File**: `.github/workflows/deploy.yml`

**Line 42**: Change this:
```yaml
role-to-assume: ${{ secrets.AWS_IAM_ROLE_ARN }}
```

To this:
```yaml
role-to-assume: ${{ secrets.AWS_IAM_ROLE }}
```

**Recommendation**: Use Option A (rename secret) - it follows best practices.

---

## 📋 Pre-Deployment Checklist

Before deploying, verify:

- [ ] GitHub secret name is **`AWS_IAM_ROLE_ARN`** or workflow updated
- [ ] Secret value is correct (IAM role ARN)
- [ ] AWS OIDC provider exists
- [ ] IAM role created with correct trust policy
- [ ] IAM role has permissions attached
- [ ] Fyers API key stored in AWS Secrets Manager: `fyers-api-key`
- [ ] WhatsApp credentials stored (optional): `whatsapp-credentials`
- [ ] Repository is on GitHub: `anoopmc1981/AI-Project-ADR`
- [ ] Code committed and ready to push

---

## 🚀 Deploy to AWS (3 Steps)

### Step 1: Verify Code is Committed
```bash
cd D:\Project\Git-AI-Projects\AI-Project-ADR
git status
# Should show: nothing to commit, working tree clean
```

### Step 2: Verify Secret Name in GitHub
Go to: https://github.com/anoopmc1981/AI-Project-ADR/settings/secrets/actions

✅ See `AWS_IAM_ROLE_ARN` or update workflow if using `AWS_IAM_ROLE`

### Step 3: Push to Main Branch
```bash
git add .
git commit -m "deploy: Ready for AWS deployment"
git push origin main
```

---

## 📊 Watch Deployment Progress

### Method 1: GitHub UI (Easiest)
1. Go to: https://github.com/anoopmc1981/AI-Project-ADR/actions
2. Find the latest workflow run
3. Click to open it
4. Watch real-time progress
5. Each step shows:
   - ✅ Passed
   - ⏳ In progress
   - ❌ Failed

### Method 2: Local Terminal
```bash
# Install GitHub CLI if needed
# https://cli.github.com

# Watch workflow in real-time
gh run watch --repo anoopmc1981/AI-Project-ADR

# Or view recent runs
gh run list --repo anoopmc1981/AI-Project-ADR
```

---

## ⏱️ Deployment Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| **Trigger** | Immediate | ⏳ Workflow starts |
| **Setup** | 5 min | Python, SAM installed |
| **Build** | 10-15 min | Lambda functions compiled |
| **Deploy Backend** | 10-15 min | CloudFormation creates resources |
| **Deploy Frontend** | 2-5 min | S3 upload, CloudFront invalidation |
| **Validation** | 1-2 min | Tests & reports |
| **TOTAL** | **~30-40 min** | ✅ Application Live! |

---

## ✨ What Gets Created in AWS

When deployment completes successfully, you'll have:

```
✅ Lambda Functions
   ├─ adr-scanner-auth-dev
   ├─ adr-scanner-calculation-dev
   ├─ adr-scanner-crossing-dev
   ├─ adr-scanner-dashboard-dev
   ├─ adr-scanner-ai-dev
   └─ adr-scanner-whatsapp-dev

✅ DynamoDB Tables
   ├─ adr-scanner-levels-dev
   ├─ adr-scanner-crossings-dev
   ├─ adr-scanner-history-dev
   └─ adr-scanner-user-settings-dev

✅ API Gateway (REST API)
✅ Cognito User Pool
✅ S3 Buckets (Frontend + Data)
✅ CloudFront Distribution
✅ EventBridge Scheduler
✅ SNS Topics
✅ SQS Queues
✅ CloudWatch Logs
```

---

## 🔍 Verify Deployment Success

After workflow completes (30-40 minutes):

### 1. Check GitHub Actions
- ✅ All 16 steps show green checkmarks
- ✅ No red X marks
- ✅ Final step shows success message

### 2. Check AWS CloudFormation
```bash
aws cloudformation describe-stacks \
    --stack-name adr-scanner-dev \
    --region ap-south-1 \
    --query 'Stacks[0].StackStatus'

# Expected: CREATE_COMPLETE or UPDATE_COMPLETE
```

### 3. Get Application URL
```bash
aws cloudformation describe-stacks \
    --stack-name adr-scanner-dev \
    --region ap-south-1 \
    --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontURL`].OutputValue' \
    --output text

# Example output: https://d1234abcd.cloudfront.net
```

### 4. Test in Browser
- Open the CloudFront URL
- Should see login page
- Login with Cognito credentials
- Dashboard should load with data

---

## 🐛 If Deployment Fails

### Check GitHub Actions Logs
1. Go to: https://github.com/anoopmc1981/AI-Project-ADR/actions
2. Find the failed run
3. Click on the red ❌ step
4. Read the error message
5. Common errors:

| Error | Solution |
|-------|----------|
| "Role not found" | Check GitHub secret name is `AWS_IAM_ROLE_ARN` |
| "AssumeRoleUnauthorizedOperation" | Verify OIDC provider, trust policy, IAM role |
| "SAM build failed" | Check Docker available, see detailed logs |
| "S3 bucket not found" | Likely first deploy - check CloudFormation events |
| "Access Denied" | Verify IAM role has CloudFormation, S3, IAM permissions |

### Check AWS CloudFormation Events
```bash
aws cloudformation describe-stack-events \
    --stack-name adr-scanner-dev \
    --region ap-south-1 \
    --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`]'
```

### Retry Deployment
```bash
# If you want to retry manually
sam build --use-container
sam deploy \
    --stack-name adr-scanner-dev \
    --region ap-south-1 \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM
```

---

## 📞 Quick Reference

### Useful Commands
```bash
# Check CloudFormation stack
aws cloudformation describe-stacks --stack-name adr-scanner-dev --region ap-south-1

# Get all outputs (URL, API endpoint, etc.)
aws cloudformation describe-stacks \
    --stack-name adr-scanner-dev \
    --region ap-south-1 \
    --query 'Stacks[0].Outputs'

# Check Lambda functions
aws lambda list-functions --region ap-south-1 | grep adr-scanner

# View CloudWatch logs
aws logs tail /aws/lambda/adr-scanner-calculation-dev --region ap-south-1 --follow

# Delete stack (if needed)
aws cloudformation delete-stack --stack-name adr-scanner-dev --region ap-south-1
```

### GitHub Links
- **Actions Tab**: https://github.com/anoopmc1981/AI-Project-ADR/actions
- **Settings/Secrets**: https://github.com/anoopmc1981/AI-Project-ADR/settings/secrets/actions
- **Workflow File**: https://github.com/anoopmc1981/AI-Project-ADR/blob/main/.github/workflows/deploy.yml

### AWS Links
- **CloudFormation**: https://console.aws.amazon.com/cloudformation/home?region=ap-south-1
- **Lambda**: https://console.aws.amazon.com/lambda/home?region=ap-south-1
- **DynamoDB**: https://console.aws.amazon.com/dynamodb/home?region=ap-south-1
- **API Gateway**: https://console.aws.amazon.com/apigateway/home?region=ap-south-1
- **CloudWatch Logs**: https://console.aws.amazon.com/logs/home?region=ap-south-1

---

## ✅ You're Ready to Deploy!

**Everything is configured. Just:**

1. ✅ Fix GitHub secret name (or update workflow)
2. ✅ Push to main branch
3. ✅ Watch GitHub Actions tab
4. ✅ Access your application in 30-40 minutes!

---

## 🎉 After Successful Deployment

Your ADR Scanner will be live with:

✅ **Dashboard**: Interactive real-time stock scanning interface  
✅ **API**: RESTful API for programmatic access  
✅ **AI Assistant**: Natural language query processing  
✅ **Alerts**: WhatsApp notifications for ADR crossings  
✅ **Authentication**: Secure Cognito-based login  
✅ **Monitoring**: CloudWatch logs and metrics  

---

## 🚀 Next Steps After Deployment

1. **Create Cognito User**
   ```bash
   aws cognito-idp admin-create-user \
       --user-pool-id YOUR_POOL_ID \
       --username user@example.com \
       --temporary-password TempPass123! \
       --message-action SUPPRESS
   ```

2. **Set Permanent Password**
   ```bash
   aws cognito-idp admin-set-user-password \
       --user-pool-id YOUR_POOL_ID \
       --username user@example.com \
       --password FinalPass123! \
       --permanent
   ```

3. **Login to Dashboard**
   - Open CloudFront URL
   - Login with credentials above
   - Start scanning for ADR crossings!

4. **Configure WhatsApp Alerts** (optional)
   - Update WhatsApp credentials in AWS Secrets Manager
   - Add user phone number in user settings
   - Enable WhatsApp alerts

5. **Monitor Logs**
   ```bash
   aws logs tail /aws/lambda/adr-scanner-calculation-dev --follow
   ```

---

**Everything is ready! Deploy now by pushing to main branch! 🚀**
