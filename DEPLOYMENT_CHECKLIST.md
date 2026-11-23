# ADR Stock Scanner - AWS Deployment Checklist

## 📋 Complete Pre-Deployment Checklist

Use this checklist to ensure everything is configured correctly before deploying.

---

## Phase 1: AWS Account Setup ☁️

### 1.1 AWS Account & Credentials
- [ ] AWS account created and active
- [ ] AWS CLI installed: `aws --version`
- [ ] AWS credentials configured: `aws configure`
- [ ] Can authenticate: `aws sts get-caller-identity` ✅

**Commands to verify:**
```bash
aws --version
aws sts get-caller-identity
aws iam get-user
```

### 1.2 AWS Regions & Services
- [ ] Primary region selected: `ap-south-1` (Mumbai)
- [ ] Region is accessible: `aws ec2 describe-regions --region-names ap-south-1`
- [ ] Cognito available in region
- [ ] Lambda available in region
- [ ] DynamoDB available in region
- [ ] S3 available globally ✅

---

## Phase 2: GitHub OIDC Setup 🔐

### 2.1 Create OIDC Provider
- [ ] OIDC provider created in AWS
- [ ] Provider URL: `https://token.actions.githubusercontent.com`
- [ ] Client ID: `sts.amazonaws.com`
- [ ] Thumbprint: `6938fd4d98bab03faadb97b34396831e3780aea1`

**Verification command:**
```bash
aws iam list-open-id-connect-providers
```

### 2.2 Create IAM Role
- [ ] IAM role created: `GitHubActionsADRDeployRole`
- [ ] Trust policy configured for GitHub
- [ ] Trust policy includes repo: `YOUR_USERNAME/AI-Project-ADR`
- [ ] Trust policy includes wildcard for all branches: `repo:*`

**Verification command:**
```bash
aws iam get-role --role-name GitHubActionsADRDeployRole
aws iam get-role --role-name GitHubActionsADRDeployRole \
    --query 'Role.AssumeRolePolicyDocument'
```

### 2.3 Attach Permissions
- [ ] Permissions policy attached to role
- [ ] Policy includes: CloudFormation, Lambda, DynamoDB, S3
- [ ] Policy includes: API Gateway, Cognito, IAM pass role
- [ ] Policy includes: SNS, SQS, CloudFront, CloudWatch
- [ ] Policy includes: Secrets Manager GetSecretValue

**Verification command:**
```bash
aws iam list-attached-role-policies \
    --role-name GitHubActionsADRDeployRole
```

---

## Phase 3: GitHub Configuration 🐙

### 3.1 Repository Settings
- [ ] Repository cloned/forked locally
- [ ] Repository has `.git` directory
- [ ] `.github/workflows/deploy.yml` exists
- [ ] Workflow file is updated with new version

**Verification:**
```bash
ls -la .github/workflows/deploy.yml
cat .github/workflows/deploy.yml | head -20
```

### 3.2 GitHub Secrets
- [ ] GitHub secret created: `AWS_IAM_ROLE_ARN`
- [ ] Secret value is correct: `arn:aws:iam::ACCOUNT_ID:role/GitHubActionsADRDeployRole`
- [ ] Secret accessible from Actions
- [ ] No typos in secret name

**How to verify:**
1. Go to GitHub repo
2. Settings → Secrets and variables → Actions
3. See `AWS_IAM_ROLE_ARN` listed ✅

---

## Phase 4: AWS Credentials & Secrets 🔑

### 4.1 Fyers API Credentials
- [ ] Fyers account active and verified
- [ ] Fyers API key obtained
- [ ] API key stored in AWS Secrets Manager: `fyers-api-key`
- [ ] Secret contains: `{"api_key":"YOUR_KEY"}`
- [ ] Can retrieve: `aws secretsmanager get-secret-value --secret-id fyers-api-key`

**Commands:**
```bash
# Create secret
aws secretsmanager create-secret \
    --name fyers-api-key \
    --secret-string '{"api_key":"YOUR_FYERS_KEY"}'

# Verify
aws secretsmanager get-secret-value --secret-id fyers-api-key
```

### 4.2 WhatsApp Credentials (Optional)
- [ ] WhatsApp API key obtained (or skip for now)
- [ ] WhatsApp API secret stored in AWS Secrets Manager: `whatsapp-credentials`
- [ ] Secret format: `{"api_key":"...", "api_url":"..."}`

**Command (optional):**
```bash
aws secretsmanager create-secret \
    --name whatsapp-credentials \
    --secret-string '{"api_key":"YOUR_KEY","api_url":"YOUR_URL"}'
```

---

## Phase 5: SAM Template Validation ✅

### 5.1 Template File
- [ ] `template.yaml` exists in repo root
- [ ] File is valid YAML syntax
- [ ] Template validated locally: `sam validate`
- [ ] No syntax errors reported

**Commands:**
```bash
sam validate
sam validate --template template.yaml
```

### 5.2 Template Parameters
- [ ] Stack name set: `adr-scanner-dev`
- [ ] Region set: `ap-south-1`
- [ ] Environment parameter: `dev`
- [ ] Cognito domain name unique

**Verification:**
```bash
grep -E "StackName|Region|Environment" template.yaml
```

### 5.3 CloudFormation Resources
- [ ] Lambda functions defined (6 total)
- [ ] DynamoDB tables defined (4 total)
- [ ] API Gateway defined
- [ ] Cognito User Pool defined
- [ ] S3 buckets defined
- [ ] CloudFront distribution defined

**Count resources:**
```bash
grep "Type: AWS::Serverless::" template.yaml | wc -l
grep "Type: AWS::" template.yaml | wc -l
```

---

## Phase 6: Application Code 📝

### 6.1 Backend Code
- [ ] All Lambda functions present in `backend/functions/`
- [ ] `auth/app.py` exists
- [ ] `adr_calculation/app.py` exists
- [ ] `crossing_detection/app.py` exists
- [ ] `dashboard/app.py` exists
- [ ] `ai_assistant/app.py` exists
- [ ] `whatsapp_alert/app.py` exists

**Verification:**
```bash
find backend/functions -name "app.py" | wc -l
# Should show: 6
```

### 6.2 Frontend Code
- [ ] `frontend/index.html` exists
- [ ] `frontend/css/style.css` exists
- [ ] `frontend/js/auth.js` exists
- [ ] `frontend/js/dashboard.js` exists
- [ ] `frontend/js/ai-assistant.js` exists
- [ ] No syntax errors in HTML/CSS/JS

**Verification:**
```bash
ls -la frontend/index.html
ls -la frontend/css/style.css
ls -la frontend/js/*.js
```

### 6.3 Dependencies
- [ ] `backend/requirements.txt` exists
- [ ] All required packages listed
- [ ] Python 3.11+ specified
- [ ] Can install locally: `pip install -r backend/requirements.txt`

**Verification:**
```bash
pip install -r backend/requirements.txt
pip freeze | grep -E "boto3|aws-lambda"
```

---

## Phase 7: Local Testing 🧪

### 7.1 SAM Build
- [ ] SAM CLI installed: `sam --version`
- [ ] Can build: `sam build --use-container`
- [ ] Build completes without errors
- [ ] `.aws-sam/build/` directory created

**Command:**
```bash
sam build --use-container
# Should complete in 5-10 minutes
```

### 7.2 Local API Test
- [ ] Can start local API: `sam local start-api --port 3001`
- [ ] API responds on `http://localhost:3001`
- [ ] No port conflicts (3001 available)
- [ ] Can stop API (Ctrl+C)

**Command:**
```bash
sam local start-api --port 3001 &
sleep 5
curl http://localhost:3001/
kill %1
```

### 7.3 Code Quality
- [ ] No Python syntax errors
- [ ] No undefined variables
- [ ] No import errors
- [ ] Code follows PEP 8 style (optional but recommended)

**Commands:**
```bash
python -m py_compile backend/functions/*/app.py
python -m pylint backend/functions/ --disable=all --enable=E --fail-under=10
```

---

## Phase 8: Git Setup 📦

### 8.1 Repository Status
- [ ] Git initialized: `.git/` exists
- [ ] Remote configured: `git remote -v` shows origin
- [ ] Can push to main branch
- [ ] Main branch is default branch

**Verification:**
```bash
git status
git remote -v
git branch -a
```

### 8.2 Git Configuration
- [ ] User email configured: `git config user.email`
- [ ] User name configured: `git config user.name`
- [ ] Can commit: `git commit --allow-empty -m "test"`
- [ ] Can push to GitHub

**Commands:**
```bash
git config user.email "your@email.com"
git config user.name "Your Name"
git commit --allow-empty -m "Setup test"
```

### 8.3 Files for Deployment
- [ ] `.github/workflows/deploy.yml` updated
- [ ] `template.yaml` committed
- [ ] `backend/` committed
- [ ] `frontend/` committed
- [ ] `backend/requirements.txt` committed

**Verification:**
```bash
git status
# Should show: nothing to commit, working tree clean
# (or only untracked files, which is OK)
```

---

## Phase 9: Pre-Deployment Verification ⚡

### 9.1 AWS Account Limits
- [ ] Lambda concurrent executions: at least 100
- [ ] S3 bucket quota: at least 1 available
- [ ] DynamoDB on-demand limit: sufficient
- [ ] API Gateway API limit: sufficient

**Check limits:**
```bash
# View Lambda concurrency
aws lambda get-account-settings --query 'AccountUsage'

# No easy command for others - check AWS console if concerned
```

### 9.2 Cost Estimation
- [ ] Estimated monthly cost: < $50
- [ ] Billing alerts configured (optional)
- [ ] AWS budget created (optional)
- [ ] Cost monitoring plan in place

### 9.3 Security Review
- [ ] No AWS credentials in code ✅
- [ ] No hardcoded API keys ✅
- [ ] Secrets stored in Secrets Manager ✅
- [ ] OIDC used instead of long-term credentials ✅
- [ ] IAM role has least privilege ✅

---

## Phase 10: Deployment 🚀

### 10.1 Final Checks Before Push
- [ ] All above items checked ✅
- [ ] No uncommitted changes in main branch
- [ ] Latest code committed and ready
- [ ] Nobody else pushing at same time
- [ ] Have AWS credentials ready for monitoring

**Final verification:**
```bash
git status  # Should be clean
git log -1  # View latest commit
aws sts get-caller-identity  # Verify AWS access
```

### 10.2 Push to Main
- [ ] Commit all changes: `git add . && git commit -m "..."`
- [ ] Push to main: `git push origin main`
- [ ] Verify push successful
- [ ] GitHub Actions triggered automatically

**Command:**
```bash
git add .
git commit -m "deploy: GitHub Actions workflow setup complete"
git push origin main
```

### 10.3 Monitor Deployment
- [ ] GitHub Actions workflow started (visible in Actions tab)
- [ ] Each step completes without errors
- [ ] Deployment reaches "Deploy Backend" step
- [ ] CloudFormation stack creation progresses
- [ ] Frontend deployment occurs
- [ ] Workflow completes successfully

**How to monitor:**
1. Go to GitHub repository
2. Click **Actions** tab
3. Find latest workflow run
4. Watch real-time progress
5. Check each step for errors

---

## Phase 11: Post-Deployment Verification ✨

### 11.1 CloudFormation Stack
- [ ] Stack created: `adr-scanner-dev`
- [ ] Stack status: `CREATE_COMPLETE`
- [ ] All resources created successfully
- [ ] No failed resources

**Verification:**
```bash
aws cloudformation describe-stacks \
    --stack-name adr-scanner-dev \
    --query 'Stacks[0].StackStatus'
# Should show: CREATE_COMPLETE or UPDATE_COMPLETE
```

### 11.2 Get Application URL
- [ ] CloudFront URL available
- [ ] API Gateway endpoint available
- [ ] Both accessible from outputs

**Verification:**
```bash
aws cloudformation describe-stacks \
    --stack-name adr-scanner-dev \
    --query 'Stacks[0].Outputs' \
    --output table
```

### 11.3 Test Application
- [ ] Open CloudFront URL in browser
- [ ] Page loads (may take 1-2 min first time)
- [ ] Can see login form
- [ ] Can login with Cognito credentials
- [ ] Dashboard loads after login
- [ ] Data displays (may be empty initially)

### 11.4 Check Logs
- [ ] Lambda logs available in CloudWatch
- [ ] No error messages in logs
- [ ] Execution times reasonable

**Check logs:**
```bash
aws logs tail /aws/lambda/adr-scanner-calculation-dev --follow
```

---

## 📊 Deployment Status Tracking

### Workflow Steps Timeline

| Step | Expected Time | Status |
|------|---|---|
| Checkout | 1 min | ⏳ |
| Python setup | 2 min | ⏳ |
| AWS auth | 1 min | ⏳ |
| SAM install | 3 min | ⏳ |
| Build | 10-15 min | ⏳ |
| Deploy | 10-15 min | ⏳ |
| Frontend | 2 min | ⏳ |
| **Total** | **30-40 min** | ⏳ |

---

## 🎯 Success Criteria

Deployment successful when:

```
✅ GitHub Actions workflow completes
✅ CloudFormation stack shows CREATE_COMPLETE
✅ All 6 Lambda functions deployed
✅ All 4 DynamoDB tables created
✅ API Gateway endpoint available
✅ S3 bucket has frontend files
✅ CloudFront distribution active
✅ Application accessible via URL
✅ Can login with Cognito
✅ Dashboard displays data
```

---

## ⚠️ Issues & Rollback

If deployment fails:

1. **Check GitHub Actions logs**
   - Go to Actions tab
   - Find failed run
   - Click on red ❌ step
   - Read error message

2. **Check CloudFormation events**
   ```bash
   aws cloudformation describe-stack-events \
       --stack-name adr-scanner-dev
   ```

3. **Rollback if needed**
   ```bash
   aws cloudformation delete-stack --stack-name adr-scanner-dev
   # Fix issues locally
   # Re-run deployment
   ```

---

## 📞 Getting Help

If stuck at any phase:

1. Read the specific phase guide in this doc
2. Check relevant documentation:
   - `GITHUB_ACTIONS_SETUP.md` - For phases 2-3
   - `GITHUB_ACTIONS_VALIDATION.md` - For workflow details
   - `DEPLOYMENT.md` - For AWS details
3. Review GitHub Actions logs
4. Check AWS CloudFormation events
5. Verify all prerequisites met

---

## ✅ Sign-Off

- [ ] All items above completed
- [ ] Deployment successful
- [ ] Application accessible
- [ ] Team notified of live status
- [ ] Documentation updated
- [ ] Monitoring configured

**Deployment Date**: _______________

**Deployed By**: _______________

**Notes**:
```
_____________________________________________
_____________________________________________
_____________________________________________
```

---

**🎉 Congratulations! ADR Scanner is live! 🚀**
