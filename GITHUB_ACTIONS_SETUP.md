# GitHub Actions AWS Deployment - Complete Setup Guide

## 🎯 Overview

Your GitHub Actions workflow will automatically deploy the ADR Stock Scanner to AWS whenever you push to the `main` branch.

**What it does:**
- ✅ Builds SAM application
- ✅ Deploys backend (Lambda, DynamoDB, API Gateway, etc.)
- ✅ Uploads frontend to S3
- ✅ Invalidates CloudFront cache
- ✅ Runs tests
- ✅ Posts deployment report

## ⚙️ Step 1: Setup AWS OIDC Provider (5 minutes)

GitHub Actions uses OpenID Connect (OIDC) for secure, keyless authentication.

### 1a. Create OIDC Provider in AWS

```bash
# Step 1: Create OIDC provider
aws iam create-open-id-connect-provider \
    --url https://token.actions.githubusercontent.com \
    --client-id-list sts.amazonaws.com \
    --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# Output will show the Provider ARN - save it
# Example: arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com
```

### 1b. Create IAM Role for GitHub Actions

```bash
# Save this as trust-policy.json
# Replace YOUR_GITHUB_USERNAME and YOUR_AWS_ACCOUNT_ID
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_AWS_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_USERNAME/AI-Project-ADR:*"
        }
      }
    }
  ]
}
EOF

# Replace placeholders with your values
sed -i 's/YOUR_AWS_ACCOUNT_ID/123456789012/g' trust-policy.json
sed -i 's/YOUR_GITHUB_USERNAME/your-github-username/g' trust-policy.json

# Create the role
aws iam create-role \
    --role-name GitHubActionsADRDeployRole \
    --assume-role-policy-document file://trust-policy.json

# Output: Role ARN - save this!
# Example: arn:aws:iam::123456789012:role/GitHubActionsADRDeployRole
```

### 1c. Attach Permissions Policy

```bash
# Option A: Use AWS managed policy (easier, less restrictive)
aws iam attach-role-policy \
    --role-name GitHubActionsADRDeployRole \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Option B: Create custom policy (recommended for production)
cat > adr-deploy-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "lambda:*",
        "dynamodb:*",
        "s3:*",
        "apigateway:*",
        "cognito-idp:*",
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:PutRolePolicy",
        "iam:GetRole",
        "iam:PassRole",
        "sns:*",
        "sqs:*",
        "cloudfront:*",
        "secretsmanager:GetSecretValue",
        "logs:*",
        "cloudwatch:*",
        "events:*"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name GitHubActionsADRDeployRole \
    --policy-name GitHubActionsADRDeployPolicy \
    --policy-document file://adr-deploy-policy.json
```

## 🔑 Step 2: Create GitHub Secret (2 minutes)

### 2a. Get Your AWS Account ID and Role ARN

```bash
# Get account ID
aws sts get-caller-identity --query 'Account' --output text

# Get role ARN
aws iam get-role \
    --role-name GitHubActionsADRDeployRole \
    --query 'Role.Arn' \
    --output text
```

**You'll get something like:**
```
arn:aws:iam::123456789012:role/GitHubActionsADRDeployRole
```

### 2b. Add GitHub Secret

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `AWS_IAM_ROLE_ARN`
5. Value: `arn:aws:iam::123456789012:role/GitHubActionsADRDeployRole`
6. Click **Add secret**

✅ Now GitHub can authenticate to AWS!

## 📋 Step 3: Configure AWS Secrets (5 minutes)

The workflow deploys your application which needs API credentials.

### 3a. Store Fyers API Key

```bash
aws secretsmanager create-secret \
    --name fyers-api-key \
    --description "Fyers API credentials for ADR Scanner" \
    --secret-string '{"api_key":"YOUR_FYERS_API_KEY_HERE"}'
```

Replace `YOUR_FYERS_API_KEY_HERE` with your actual Fyers API key.

### 3b. Store WhatsApp Credentials (Optional for now)

```bash
aws secretsmanager create-secret \
    --name whatsapp-credentials \
    --description "WhatsApp API credentials" \
    --secret-string '{
        "api_key": "YOUR_WHATSAPP_API_KEY",
        "api_url": "YOUR_WHATSAPP_API_URL"
    }'
```

You can configure these later.

### 3c. Verify Secrets

```bash
# List all secrets
aws secretsmanager list-secrets | grep adr

# Test accessing a secret
aws secretsmanager get-secret-value --secret-id fyers-api-key
```

## 🚀 Step 4: Deploy! (1 minute)

### Method 1: Automatic (Push to Main)

```bash
# Make a commit and push to main
git add .
git commit -m "feat: Enable GitHub Actions deployment"
git push origin main
```

Workflow automatically triggers! ✨

### Method 2: Manual Trigger

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Deploy ADR Scanner to AWS** workflow
4. Click **Run workflow**
5. Select **main** branch
6. Click **Run workflow**

## 📊 Monitor Deployment

### In GitHub UI

1. Click **Actions** tab
2. Find the workflow run
3. Click on it to see real-time progress
4. Each step shows:
   - ✅ Completed
   - ⏳ In progress
   - ❌ Failed

### In Terminal

```bash
# List recent workflow runs
gh run list --repo YOUR_USERNAME/AI-Project-ADR

# Watch specific run (follow real-time)
gh run watch RUN_ID --repo YOUR_USERNAME/AI-Project-ADR

# View detailed logs
gh run view RUN_ID --log --repo YOUR_USERNAME/AI-Project-ADR
```

## ✅ Verify Deployment Success

After workflow completes (5-10 minutes):

### 1. Check AWS CloudFormation

```bash
# View stack status
aws cloudformation describe-stacks \
    --stack-name adr-scanner-dev \
    --query 'Stacks[0].StackStatus' \
    --output text

# Should show: CREATE_COMPLETE or UPDATE_COMPLETE
```

### 2. Get Application URL

```bash
# Get CloudFront URL
aws cloudformation describe-stacks \
    --stack-name adr-scanner-dev \
    --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontURL`].OutputValue' \
    --output text

# Should return something like:
# https://d1234abcd.cloudfront.net
```

### 3. Test Application

- Open the CloudFront URL in browser
- Login with Cognito credentials
- Verify dashboard loads
- Check that data appears

## 🔍 Troubleshooting

### "AssumeRoleUnauthorizedOperation"

**Problem**: OIDC authentication failed

**Solution**:
```bash
# Verify role exists
aws iam get-role --role-name GitHubActionsADRDeployRole

# Check trust relationship
aws iam get-role --role-name GitHubActionsADRDeployRole \
    --query 'Role.AssumeRolePolicyDocument'

# Verify GitHub secret is correct
# Go to Settings → Secrets → Check AWS_IAM_ROLE_ARN value
```

### "SAM build failed"

**Problem**: Docker not available or SAM cache issue

**Solution**:
```bash
# SAM build uses Docker - it's pre-installed on GitHub Actions
# Check workflow logs for specific error
# Usually: missing dependencies or syntax error in template.yaml

# Validate template locally
sam validate
```

### "S3 bucket not found"

**Problem**: CloudFormation stack didn't create S3 bucket

**Solution**:
```bash
# Check CloudFormation events
aws cloudformation describe-stack-events \
    --stack-name adr-scanner-dev \
    --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`]'

# View full stack details
aws cloudformation describe-stacks --stack-name adr-scanner-dev
```

### "Permission denied" on S3

**Problem**: IAM role lacks S3 permissions

**Solution**:
```bash
# Update policy
aws iam put-role-policy \
    --role-name GitHubActionsADRDeployRole \
    --policy-name GitHubActionsADRDeployPolicy \
    --policy-document file://adr-deploy-policy.json
```

### Workflow doesn't trigger

**Problem**: Trigger conditions not met

**Check**:
- [ ] Pushed to `main` branch (not develop/feature)
- [ ] `.github/workflows/deploy.yml` exists in repo
- [ ] Commit includes at least one change
- [ ] Repository settings allow Actions

**Re-trigger**:
```bash
# Make a dummy commit
git commit --allow-empty -m "trigger: Workflow test"
git push origin main
```

## 📈 Deployment Checklist

Before first deployment:

```
AWS Setup:
  ☐ AWS account with appropriate permissions
  ☐ OIDC provider created
  ☐ IAM role created for GitHub
  ☐ IAM role ARN noted

GitHub Setup:
  ☐ Repository forked/cloned
  ☐ GitHub secret AWS_IAM_ROLE_ARN set
  ☐ .github/workflows/deploy.yml exists and updated

AWS Credentials:
  ☐ Fyers API key stored in Secrets Manager
  ☐ WhatsApp credentials stored (optional)
  ☐ AWS region set to ap-south-1

Application:
  ☐ template.yaml validates without errors
  ☐ backend/requirements.txt updated
  ☐ frontend files ready for S3

Testing:
  ☐ Workflow file is valid YAML
  ☐ Code builds locally (sam build)
  ☐ No syntax errors in Lambda functions
```

## 🔄 Continuing Deployments

After first successful deployment:

### Standard Workflow

```bash
# 1. Make code changes
# 2. Commit and push to main
git add .
git commit -m "feat: Add new feature"
git push origin main

# 3. GitHub Actions automatically deploys
# 4. Check Actions tab for progress
```

### Manual Redeployment

```bash
# If you need to redeploy without code changes
gh run list --repo YOUR_USERNAME/AI-Project-ADR

# Re-run a specific workflow
gh run rerun RUN_ID --repo YOUR_USERNAME/AI-Project-ADR
```

## 🌍 Multi-Environment Setup

For staging/production, create additional workflows:

### Staging (on develop branch)

```bash
cp .github/workflows/deploy.yml .github/workflows/deploy-staging.yml

# Edit deploy-staging.yml:
# - Change trigger to: branches: [develop]
# - Change STACK_NAME: adr-scanner-staging
# - Change ENVIRONMENT: staging
```

### Production (on main branch with approval)

```bash
# deploy.yml stays as-is for production
# Already configured for main branch
```

## 📞 Getting Help

### Common Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [OIDC with GitHub Actions](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)

### Debug Steps

1. Check GitHub Actions logs (Actions tab)
2. View CloudFormation events: `aws cloudformation describe-stack-events --stack-name adr-scanner-dev`
3. Check Lambda logs: `aws logs tail /aws/lambda/adr-scanner-calculation-dev --follow`
4. Verify IAM permissions: `aws iam simulate-principal-policy ...`

## 🎉 You're Ready!

Your GitHub Actions workflow is now configured for automatic AWS deployment!

**Next steps:**
1. ✅ Complete all setup steps above
2. 🔄 Push code to main branch
3. 👀 Watch Actions tab for deployment
4. 🌐 Access your application via CloudFront URL
5. 📊 Monitor with CloudWatch logs

**Happy deploying! 🚀**
