# ADR Scanner - Troubleshooting Guide

This guide helps you fix issues that might occur during OIDC setup or deployment.

---

## 🔴 OIDC Authentication Errors

### Error: "Credentials could not be loaded"

**Location:** GitHub Actions, "Configure AWS Credentials" step  
**Root Cause:** GitHub cannot load credentials from AWS - trust policy is wrong or secret is not updated

**Solutions (try in order):**

1. **Check GitHub Secret**
   - Go to: https://github.com/anoopmc1981/AI-Project-ADR/settings/secrets/actions
   - Click `AWS_IAM_ROLE`
   - Verify value looks like: `arn:aws:iam::123456789012:role/GitHubActionsADRDeployRole`
   - Check there are NO extra spaces before or after
   - Click "Update secret"

2. **Wait for GitHub to sync secret** (1 minute)
   - GitHub sometimes takes a moment to propagate secrets
   - Wait 60 seconds

3. **Run OIDC fix script again**
   ```bash
   bash final-oidc-fix.sh
   ```
   - Copy the new Role ARN
   - Update the GitHub secret with the new ARN
   - Re-run the workflow

4. **Check AWS IAM role exists**
   ```bash
   aws iam get-role --role-name GitHubActionsADRDeployRole
   ```
   - If you get an error "NoSuchEntity", run the fix script again

---

### Error: "Not authorized to perform sts:AssumeRoleWithWebIdentity"

**Location:** GitHub Actions, "Configure AWS Credentials" step  
**Root Cause:** Trust policy is misconfigured or OIDC provider is wrong

**Solutions:**

1. **Run OIDC fix script again**
   ```bash
   bash final-oidc-fix.sh
   ```
   - This fixes all OIDC configuration issues

2. **Verify OIDC provider exists**
   ```bash
   ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   aws iam get-open-id-connect-provider --open-id-connect-provider-arn "arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
   ```
   - If you get an error, the OIDC provider is missing
   - Run the fix script to create it

3. **Check trust policy is correct**
   ```bash
   aws iam get-role --role-name GitHubActionsADRDeployRole --query 'Role.AssumeRolePolicyDocument'
   ```
   - Should show:
     ```json
     {
       "Principal": {
         "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
       },
       "Condition": {
         "StringLike": {
           "token.actions.githubusercontent.com:sub": "repo:anoopmc1981/AI-Project-ADR:*"
         }
       }
     }
     ```

4. **Check role has permissions**
   ```bash
   aws iam list-attached-role-policies --role-name GitHubActionsADRDeployRole
   ```
   - Should show `AdministratorAccess` policy attached
   - If not, run the fix script to attach it

---

### Error: "Could not assume role with OIDC"

**Location:** GitHub Actions, "Configure AWS Credentials" step  
**Root Cause:** Similar to above - configuration issue

**Solution:**
- Run OIDC fix script: `bash final-oidc-fix.sh`
- Delete and recreate the role manually:
  ```bash
  aws iam delete-role --role-name GitHubActionsADRDeployRole 2>/dev/null || true
  sleep 2
  bash final-oidc-fix.sh
  ```

---

## 🔴 OIDC Fix Script Errors

### Error: "Could not get AWS Account ID"

**Root Cause:** AWS credentials not configured or not working

**Solutions:**

1. **Configure AWS credentials**
   ```bash
   aws configure
   ```
   - You'll be prompted for:
     - AWS Access Key ID: [your key]
     - AWS Secret Access Key: [your secret]
     - Default region: ap-south-1
     - Default output format: json

2. **Test credentials**
   ```bash
   aws sts get-caller-identity
   ```
   - Should show your Account ID, User ARN, Account (again)

3. **Check credentials file**
   - Windows: `C:\Users\WIIS\.aws\credentials`
   - Mac/Linux: `~/.aws/credentials`
   - Should have `aws_access_key_id` and `aws_secret_access_key`

---

### Error: "Cannot create role" or "AccessDenied"

**Root Cause:** Your AWS user doesn't have IAM permissions

**Solutions:**

1. **Check your AWS permissions**
   - Go to: https://console.aws.amazon.com/iam/
   - Click "Users" → Your username
   - Look for policies attached
   - Should have `AdministratorAccess` or at least `IAMFullAccess`

2. **Ask your AWS admin** to give you:
   - `iam:CreateRole`
   - `iam:DeleteRole`
   - `iam:AttachRolePolicy`
   - `iam:DetachRolePolicy`
   - `iam:CreateOpenIDConnectProvider`
   - `iam:GetOpenIDConnectProvider`
   - `iam:GetRole`

---

## 🔴 GitHub Actions Workflow Errors

### Error: "SAM build failed"

**Location:** GitHub Actions, "Build SAM Application" step  
**Root Cause:** Python dependencies or syntax errors

**Solutions:**

1. **Check Python version**
   ```bash
   python --version
   ```
   - Should be 3.9 or higher
   - Workflow uses 3.11

2. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```
   - Try installing locally to see specific errors

3. **Check for syntax errors**
   ```bash
   python -m py_compile backend/functions/*.py
   ```
   - Should complete without errors

4. **Check requirements.txt exists**
   ```bash
   ls -la backend/requirements.txt
   ```

---

### Error: "Stack already exists"

**Location:** GitHub Actions, "Deploy Backend with SAM" step  
**Root Cause:** You already deployed once, SAM is trying to update

**Solutions:**

1. **This is actually expected** - Just wait for the update to complete
   - Check progress in CloudFormation console

2. **Or delete the stack and redeploy**
   ```bash
   aws cloudformation delete-stack --stack-name adr-scanner-dev --region ap-south-1
   ```
   - Wait for deletion to complete (you'll see DELETE_COMPLETE)
   - Re-run the workflow

---

### Error: "Lambda function not found" (after deployment)

**Location:** GitHub Actions, "Deploy Frontend" or "Invalidate CloudFront" step  
**Root Cause:** CloudFormation still creating resources

**Solutions:**

1. **This is usually temporary** - Wait 1-2 minutes and re-run the step

2. **Check CloudFormation stack**
   ```bash
   aws cloudformation describe-stacks --stack-name adr-scanner-dev --region ap-south-1
   ```
   - Look for `StackStatus`
   - Should be `CREATE_COMPLETE` or `UPDATE_COMPLETE`

3. **If it's still creating**, the deployment is still in progress
   - Wait for it to complete

---

## 🔴 Deployment Verification Errors

### Error: "Cannot access dashboard" (404 or timeout)

**Location:** Try accessing CloudFront URL from browser  
**Root Cause:** Frontend not deployed, CloudFront not ready, or domain not configured

**Solutions:**

1. **Wait for CloudFront propagation** (1-5 minutes)
   - CloudFront takes time to distribute content globally
   - Try again in 2 minutes

2. **Check CloudFront distribution**
   ```bash
   aws cloudfront list-distributions --region ap-south-1
   ```
   - Look for the ADR Scanner distribution
   - Check status is "Deployed"
   - Get the DomainName (looks like: d123456.cloudfront.net)

3. **Check S3 bucket has frontend files**
   ```bash
   BUCKET=$(aws s3 ls | grep adr-scanner-frontend | awk '{print $3}')
   aws s3 ls s3://$BUCKET/
   ```
   - Should show index.html, css/, js/

4. **Check CloudFront cache**
   - Try opening in incognito/private window
   - Or clear browser cache and try again

---

### Error: "API not responding" (502/503)

**Location:** Dashboard, trying to call API  
**Root Cause:** Lambda functions not deployed or API Gateway not configured

**Solutions:**

1. **Check Lambda functions exist**
   ```bash
   aws lambda list-functions --region ap-south-1
   ```
   - Should show 6 functions
   - Each should start with "adr-scanner-dev" or "AuthHandler", "DashboardHandler", etc.

2. **Check API Gateway**
   ```bash
   aws apigateway get-rest-apis --region ap-south-1
   ```
   - Should show the ADR Scanner API
   - Note the ID

3. **Check Lambda logs**
   ```bash
   aws logs tail /aws/lambda/AuthHandler --region ap-south-1 --follow
   ```
   - Look for error messages
   - Check function is timing out or crashing

4. **Check IAM permissions**
   - Lambda functions need permissions to access DynamoDB, Cognito, etc.
   - Check the SAM template for policy definitions

---

### Error: "Cannot log in" (Cognito error)

**Location:** Dashboard login page  
**Root Cause:** Cognito not configured or no users created

**Solutions:**

1. **Check Cognito user pool exists**
   ```bash
   aws cognito-idp list-user-pools --max-results 10 --region ap-south-1
   ```

2. **Create a test user**
   ```bash
   POOL_ID=$(aws cognito-idp list-user-pools --max-results 10 --region ap-south-1 --query 'UserPools[0].Id' --output text)
   aws cognito-idp admin-create-user \
     --user-pool-id $POOL_ID \
     --username testuser@example.com \
     --temporary-password "TempPassword123!" \
     --region ap-south-1
   ```

3. **Check Cognito app client exists**
   - Needed for the dashboard to authenticate
   - Should be created by SAM template

---

## 🟡 Performance Issues

### Application is slow

**Solutions:**

1. **Check CloudFront**
   - May need more cache time
   - Try opening directly from S3 to compare

2. **Check Lambda cold starts**
   - First invocation takes longer
   - Try again immediately after first request

3. **Check DynamoDB capacity**
   - On-demand should auto-scale
   - Check CloudWatch metrics for throttling

4. **Check network latency**
   - You're in India, so ap-south-1 region is best
   - Check you don't have VPN/proxy slowing things down

---

## 🟡 Data Issues

### "No data showing" in dashboard

**Solutions:**

1. **Check DynamoDB tables have data**
   ```bash
   TABLES=$(aws dynamodb list-tables --region ap-south-1 --query 'TableNames' --output text)
   echo "Tables: $TABLES"
   
   # Scan a table
   aws dynamodb scan --table-name ADRScannerRanges --region ap-south-1
   ```

2. **Run ADR calculation manually**
   - Go to Lambda console
   - Find ADRCalculationHandler function
   - Click "Test"
   - Create test event and run

3. **Check Fyers API credentials**
   - Lambda needs access to Fyers API
   - Check environment variables in Lambda function
   - Verify API key is correct

---

## 🆘 Still Not Working?

### Step-by-step debugging

1. **Check GitHub Actions logs**
   - Go to: https://github.com/anoopmc1981/AI-Project-ADR/actions
   - Click the failed run
   - Click each step to see detailed logs
   - Look for the specific error message

2. **Check AWS CloudFormation events**
   - Go to: https://console.aws.amazon.com/cloudformation
   - Click the adr-scanner-dev stack
   - Look at "Events" tab
   - Find the resource that failed

3. **Check AWS Lambda logs**
   - Go to: https://console.aws.amazon.com/lambda
   - Click the function that failed
   - Click "CloudWatch Logs"
   - Look for error messages

4. **Check AWS API Gateway logs**
   - Go to: https://console.aws.amazon.com/apigateway
   - Click the ADR Scanner API
   - Look at logs and metrics

5. **Run verification script**
   ```bash
   bash VERIFY_SETUP.sh
   ```
   - This checks all components

---

## 📋 Debugging Checklist

If something fails, check these in order:

- [ ] AWS credentials work: `aws sts get-caller-identity`
- [ ] OIDC provider exists: `aws iam get-open-id-connect-provider ...`
- [ ] IAM role exists: `aws iam get-role --role-name GitHubActionsADRDeployRole`
- [ ] Role has trust policy: Check output from above
- [ ] Role has permissions: `aws iam list-attached-role-policies ...`
- [ ] GitHub secret updated: https://github.com/anoopmc1981/AI-Project-ADR/settings/secrets/actions
- [ ] Workflow re-run: https://github.com/anoopmc1981/AI-Project-ADR/actions
- [ ] CloudFormation stack created: `aws cloudformation describe-stacks ...`
- [ ] Lambda functions deployed: `aws lambda list-functions ...`
- [ ] DynamoDB tables created: `aws dynamodb list-tables ...`
- [ ] S3 bucket created: `aws s3 ls`
- [ ] CloudFront distribution created: `aws cloudfront list-distributions`
- [ ] Can access dashboard: Open CloudFront URL in browser

---

## 🆘 Get Help

If you're still stuck:

1. **Re-read the main guides:**
   - QUICK_START.txt
   - NEXT_STEPS.md
   - OIDC_FIX_INSTRUCTIONS.md

2. **Run the fix script again:**
   ```bash
   bash final-oidc-fix.sh
   ```

3. **Check AWS IAM permissions:**
   - You need at least: IAMFullAccess, AdministratorAccess
   - Or granular permissions for OIDC, IAM, Lambda, DynamoDB, S3, CloudFront, Cognito

4. **Check GitHub repository:**
   - Is it public?
   - Is Actions enabled?
   - Is secrets configured correctly?

5. **Check your AWS account:**
   - Are you in ap-south-1 region?
   - Do you have resources available?
   - Are you hitting any service limits?

---

**Most issues are solved by running the OIDC fix script again or updating the GitHub secret. Try that first! 🎯**

