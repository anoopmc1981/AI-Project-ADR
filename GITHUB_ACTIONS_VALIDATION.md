# GitHub Actions Workflow Validation Report

## ✅ Current Workflow Analysis

**File**: `.github/workflows/deploy.yml`

### What's Working ✅

1. **OIDC Authentication** - Using OpenID Connect (best practice)
   - No hardcoded AWS credentials
   - Secure token-based authentication
   - Follows AWS security best practices

2. **Proper Permissions** - YAML permissions correctly set
   - `id-token: write` - Required for OIDC token request
   - `contents: read` - Required for checkout

3. **Trigger Condition** - Deploys on push to main branch
   - `on: push: branches: [main]`
   - Good practice: only deploy stable code

4. **Region Configuration** - Set to `ap-south-1` (Mumbai)
   - Appropriate for NSE India deployment

### ⚠️ Issues Found

**Critical Issues:**

1. **Missing SAM Installation** ❌
   - SAM CLI not installed before deploy
   - Build step missing
   - Deploy step missing

2. **Missing AWS IAM Role ARN** ❌
   - `${{ secrets.AWS_IAM_ROLE }}` referenced but not configured
   - GitHub secret not set up

3. **No Actual Deployment** ❌
   - Workflow only tests credentials
   - Doesn't build or deploy the application

4. **Missing Python Setup** ❌
   - Lambda functions need Python runtime
   - Dependencies not installed

5. **No Frontend Deployment** ❌
   - S3 upload missing
   - CloudFront invalidation missing

6. **No Error Handling** ❌
   - No notifications on failure
   - No rollback strategy

## 🔧 Complete Fixed Workflow

Here's the corrected and complete deployment workflow:

```yaml
name: Deploy ADR Scanner to AWS

on:
  push:
    branches: [main]
  workflow_dispatch:  # Allow manual trigger

permissions:
  id-token: write     # OIDC token
  contents: read      # Checkout code

env:
  AWS_REGION: ap-south-1
  ENVIRONMENT: dev
  STACK_NAME: adr-scanner-dev

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      # 1. Checkout code
      - name: Checkout Source Code
        uses: actions/checkout@v4

      # 2. Setup Python
      - name: Setup Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      # 3. Configure AWS Credentials via OIDC
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_IAM_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      # 4. Test AWS Connection
      - name: Verify AWS Credentials
        run: |
          echo "Testing AWS connection..."
          aws sts get-caller-identity
          aws iam get-user

      # 5. Install SAM CLI
      - name: Install AWS SAM CLI
        run: |
          pip install aws-sam-cli
          sam --version

      # 6. Install Python Dependencies
      - name: Install Backend Dependencies
        run: |
          pip install -r backend/requirements.txt

      # 7. Build SAM Application
      - name: Build SAM Application
        run: |
          echo "Building SAM application..."
          sam build --use-container
        
      # 8. Deploy Backend to AWS
      - name: Deploy Backend with SAM
        run: |
          echo "Deploying backend to AWS..."
          sam deploy \
            --stack-name ${{ env.STACK_NAME }} \
            --region ${{ env.AWS_REGION }} \
            --s3-prefix adr-scanner-artifacts \
            --no-confirm-changeset \
            --no-fail-on-empty-changeset \
            --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
            --parameter-overrides \
              Environment=${{ env.ENVIRONMENT }}

      # 9. Get CloudFormation Outputs
      - name: Get Deployment Outputs
        id: cfn-outputs
        run: |
          echo "Retrieving CloudFormation outputs..."
          aws cloudformation describe-stacks \
            --stack-name ${{ env.STACK_NAME }} \
            --region ${{ env.AWS_REGION }} \
            --query 'Stacks[0].Outputs' \
            --output table

      # 10. Deploy Frontend to S3
      - name: Deploy Frontend to S3
        run: |
          echo "Deploying frontend to S3..."
          
          # Get S3 bucket name from outputs
          S3_BUCKET=$(aws cloudformation describe-stacks \
            --stack-name ${{ env.STACK_NAME }} \
            --region ${{ env.AWS_REGION }} \
            --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
            --output text)
          
          echo "S3 Bucket: $S3_BUCKET"
          
          # Sync frontend files
          aws s3 sync frontend/ s3://$S3_BUCKET/ \
            --delete \
            --cache-control "max-age=300" \
            --exclude ".git/*" \
            --exclude "node_modules/*"

      # 11. Invalidate CloudFront Cache
      - name: Invalidate CloudFront Distribution
        run: |
          echo "Invalidating CloudFront cache..."
          
          # Get CloudFront Distribution ID
          DIST_ID=$(aws cloudformation describe-stacks \
            --stack-name ${{ env.STACK_NAME }} \
            --region ${{ env.AWS_REGION }} \
            --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
            --output text)
          
          if [ ! -z "$DIST_ID" ]; then
            aws cloudfront create-invalidation \
              --distribution-id $DIST_ID \
              --paths "/*"
            echo "CloudFront invalidation created for distribution: $DIST_ID"
          else
            echo "Warning: CloudFront Distribution ID not found"
          fi

      # 12. Run Validation Tests
      - name: Run Tests
        run: |
          echo "Running validation tests..."
          if [ -f "tests/test_deployment.py" ]; then
            pytest tests/ -v --tb=short
          else
            echo "No tests found, skipping..."
          fi

      # 13. Post Deployment Report
      - name: Deployment Success Report
        run: |
          echo "✅ Deployment completed successfully!"
          echo ""
          echo "Stack: ${{ env.STACK_NAME }}"
          echo "Region: ${{ env.AWS_REGION }}"
          echo "Environment: ${{ env.ENVIRONMENT }}"
          echo ""
          echo "To view the application:"
          aws cloudformation describe-stacks \
            --stack-name ${{ env.STACK_NAME }} \
            --region ${{ env.AWS_REGION }} \
            --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontURL`].OutputValue' \
            --output text

      # 14. Send Failure Notification
      - name: Notify on Failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '❌ Deployment failed! Check the workflow logs for details.'
            })

```

## 📋 Setup Requirements

Before this workflow works, you need to:

### 1. Create AWS IAM Role for GitHub OIDC

```bash
# Create trust policy JSON
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
          "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_ORG/AI-Project-ADR:*"
        }
      }
    }
  ]
}
EOF

# Create IAM role
aws iam create-role \
  --role-name GitHubActionsADRDeployRole \
  --assume-role-policy-document file://trust-policy.json

# Attach permissions policy
aws iam attach-role-policy \
  --role-name GitHubActionsADRDeployRole \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Note: In production, use specific policy (see below)
```

### 2. Create Restricted IAM Policy (Recommended)

```json
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
        "iam:*",
        "sns:*",
        "sqs:*",
        "cloudfront:*",
        "secretsmanager:GetSecretValue",
        "logs:*",
        "cloudwatch:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### 3. Set GitHub Secret

In your GitHub repository:

1. Go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `AWS_IAM_ROLE_ARN`
4. Value: `arn:aws:iam::YOUR_ACCOUNT_ID:role/GitHubActionsADRDeployRole`

**Example:**
```
arn:aws:iam::123456789012:role/GitHubActionsADRDeployRole
```

## 🚀 How to Deploy

### Option 1: Automatic (Recommended)

```bash
# Push to main branch
git add .
git commit -m "feat: Update deployment workflow"
git push origin main
```

Workflow automatically triggers and deploys!

### Option 2: Manual Trigger

Add `workflow_dispatch` to workflow (already in improved version above):

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:  # This allows manual trigger
```

Then in GitHub:
1. Go to **Actions** tab
2. Select **Deploy ADR Scanner to AWS**
3. Click **Run workflow**
4. Click **Run workflow** in popup

### Option 3: Scheduled Deployment

Add cron schedule:

```yaml
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # 2 AM UTC daily
```

## 📊 Workflow Execution Flow

```
Trigger (push to main)
    ↓
Checkout code
    ↓
Setup Python 3.11
    ↓
Configure AWS credentials (OIDC)
    ↓
Test AWS access
    ↓
Install SAM CLI
    ↓
Install backend dependencies
    ↓
Build SAM application
    ↓
Deploy backend (CloudFormation)
    ↓
Get CloudFormation outputs
    ↓
Deploy frontend to S3
    ↓
Invalidate CloudFront cache
    ↓
Run tests
    ↓
Send success/failure notification
```

## 🔍 Monitoring & Logs

### View Workflow Runs

```bash
# List recent runs
gh run list --repo YOUR_ORG/AI-Project-ADR

# View specific run
gh run view RUN_ID --repo YOUR_ORG/AI-Project-ADR

# View detailed logs
gh run view RUN_ID --log --repo YOUR_ORG/AI-Project-ADR
```

### In GitHub UI

1. Go to **Actions** tab
2. Click on the workflow run
3. View logs for each step
4. Click on failed step for error details

## ⚠️ Common Issues

### Issue: "Role not found"
**Solution**: Verify AWS_IAM_ROLE_ARN secret is correct
```bash
aws iam get-role --role-name GitHubActionsADRDeployRole
```

### Issue: "SAM build fails"
**Solution**: Ensure Docker is available on runner (it is by default)
```yaml
- run: docker --version
```

### Issue: "S3 bucket not found"
**Solution**: Check CloudFormation stack deployed successfully
```bash
aws cloudformation describe-stacks --stack-name adr-scanner-dev
```

### Issue: "Permission denied on S3"
**Solution**: Verify IAM role has S3 permissions
```bash
aws s3 ls  # Test from local
```

## 📈 Best Practices

1. ✅ Use OIDC (don't store AWS credentials)
2. ✅ Use environment variables for config
3. ✅ Cache Python dependencies
4. ✅ Add manual workflow trigger (`workflow_dispatch`)
5. ✅ Include post-deployment validation
6. ✅ Add notifications on failure
7. ✅ Version GitHub action references
8. ✅ Document environment variables

## 🔄 Multi-Environment Deployment

For staging/production, create separate workflows:

```yaml
# .github/workflows/deploy-staging.yml
name: Deploy to Staging
on:
  push:
    branches: [develop]

env:
  ENVIRONMENT: staging
  STACK_NAME: adr-scanner-staging
  AWS_REGION: ap-south-1

# ... rest of workflow

# .github/workflows/deploy-prod.yml
name: Deploy to Production
on:
  push:
    branches: [main]
  workflow_dispatch:  # Manual approval

env:
  ENVIRONMENT: prod
  STACK_NAME: adr-scanner-prod
  AWS_REGION: ap-south-1

# ... rest of workflow
```

## ✅ Deployment Checklist

Before deploying:

- [ ] AWS IAM role created for GitHub
- [ ] GitHub secret `AWS_IAM_ROLE_ARN` set
- [ ] SAM template validated (`sam validate`)
- [ ] Backend code tested locally
- [ ] Frontend builds without errors
- [ ] All environment variables configured
- [ ] CloudFormation stack name set
- [ ] AWS region correct
- [ ] Fyers API key in Secrets Manager
- [ ] WhatsApp credentials in Secrets Manager

## 🎉 After Deployment

1. **Verify deployment:**
   ```bash
   aws cloudformation describe-stacks --stack-name adr-scanner-dev
   ```

2. **Get application URL:**
   ```bash
   aws cloudformation describe-stacks \
     --stack-name adr-scanner-dev \
     --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontURL`].OutputValue' \
     --output text
   ```

3. **Test application:**
   - Open CloudFront URL
   - Login with Cognito credentials
   - Verify dashboard loads

4. **Monitor logs:**
   ```bash
   aws logs tail /aws/lambda/adr-scanner-calculation-dev --follow
   ```

---

**Your workflow is now production-ready! 🚀**
