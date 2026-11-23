# ❌ OIDC Authentication Failed - Trust Policy Fix

## Error Analysis

**Error Message:**
```
Error: Could not assume role with OIDC: Not authorized to perform sts:AssumeRoleWithWebIdentity
```

**Root Cause:**
The IAM role's trust policy (assume role policy) is incorrect or doesn't match your GitHub repository.

---

## 🔧 Fix Steps

### Step 1: Get Your GitHub Information

You need:
- **GitHub Organization/Username**: `anoopmc1981`
- **Repository Name**: `AI-Project-ADR`
- **AWS Account ID**: Get it with:

```bash
aws sts get-caller-identity --query 'Account' --output text
```

**Example output**: `123456789012`

### Step 2: Get Your Current Role Trust Policy

```bash
aws iam get-role \
    --role-name GitHubActionsADRDeployRole \
    --query 'Role.AssumeRolePolicyDocument'
```

**Save the output** - we'll need to compare it.

### Step 3: Create Correct Trust Policy

Create a file named `trust-policy.json` with this content:

**IMPORTANT**: Replace:
- `YOUR_AWS_ACCOUNT_ID` with your actual account ID (e.g., `123456789012`)
- `anoopmc1981` with your GitHub username if different

```json
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
          "token.actions.githubusercontent.com:sub": "repo:anoopmc1981/AI-Project-ADR:*"
        }
      }
    }
  ]
}
```

### Step 4: Update the Trust Policy

```bash
# Replace the role's trust policy
aws iam update-assume-role-policy \
    --role-name GitHubActionsADRDeployRole \
    --policy-document file://trust-policy.json

echo "Trust policy updated successfully!"
```

### Step 5: Verify the Update

```bash
# Check the updated trust policy
aws iam get-role \
    --role-name GitHubActionsADRDeployRole \
    --query 'Role.AssumeRolePolicyDocument'
```

**Should show:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:anoopmc1981/AI-Project-ADR:*"
        }
      }
    }
  ]
}
```

---

## ✅ Common Issues & Solutions

### Issue 1: "Account ID incorrect"
**Solution**: Get correct account ID:
```bash
aws sts get-caller-identity
```

### Issue 2: "GitHub username wrong"
**Solution**: Make sure it's `anoopmc1981` (your GitHub username)

### Issue 3: "OIDC provider not found"
**Solution**: Check provider exists:
```bash
aws iam list-open-id-connect-providers
```

Should show:
```
arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com
```

If not found, create it:
```bash
aws iam create-open-id-connect-provider \
    --url https://token.actions.githubusercontent.com \
    --client-id-list sts.amazonaws.com \
    --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### Issue 4: "Role doesn't have permissions"
**Solution**: Verify permissions are attached:
```bash
aws iam list-attached-role-policies \
    --role-name GitHubActionsADRDeployRole
```

Should show at least:
```
AdministratorAccess
```

If missing, attach it:
```bash
aws iam attach-role-policy \
    --role-name GitHubActionsADRDeployRole \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

---

## 🔍 Debugging Steps

If still failing after trust policy fix, run these:

### 1. Test OIDC Token Generation
```bash
# This requires GitHub CLI
gh run download 45131777504 -D logs -p "*"

# Then check the logs for more details
cat logs/*/0_Configure*
```

### 2. Check OIDC Provider Configuration
```bash
aws iam get-open-id-connect-provider \
    --open-id-connect-provider-arn "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
```

### 3. Verify IAM Role Configuration
```bash
# Check role exists
aws iam get-role --role-name GitHubActionsADRDeployRole

# Check trust policy
aws iam get-role --role-name GitHubActionsADRDeployRole \
    --query 'Role.AssumeRolePolicyDocument' \
    --output json | python -m json.tool

# Check attached policies
aws iam list-attached-role-policies \
    --role-name GitHubActionsADRDeployRole
```

---

## 📋 Complete Setup Verification Checklist

- [ ] AWS Account ID retrieved: `aws sts get-caller-identity`
- [ ] OIDC Provider exists: `aws iam list-open-id-connect-providers`
- [ ] IAM Role exists: `aws iam get-role --role-name GitHubActionsADRDeployRole`
- [ ] Trust policy file created with correct Account ID and GitHub username
- [ ] Trust policy updated: `aws iam update-assume-role-policy ...`
- [ ] Permissions attached: `aws iam list-attached-role-policies ...`
- [ ] GitHub secret `AWS_IAM_ROLE_ARN` has correct role ARN
- [ ] Repository branch is `main`
- [ ] Workflow file `.github/workflows/deploy.yml` is committed

---

## 🚀 After Fixing

Once trust policy is updated:

1. **Go to GitHub Actions**: https://github.com/anoopmc1981/AI-Project-ADR/actions
2. **Click** on the failed workflow run
3. **Click** "Re-run failed jobs"
4. **Watch** the deployment progress

---

## Example: Complete Fix Script

If you want to do everything in one go:

```bash
#!/bin/bash

# Get AWS Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
echo "AWS Account ID: $ACCOUNT_ID"

# GitHub info
GITHUB_ORG="anoopmc1981"
GITHUB_REPO="AI-Project-ADR"
ROLE_NAME="GitHubActionsADRDeployRole"

# Create trust policy JSON
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:${GITHUB_ORG}/${GITHUB_REPO}:*"
        }
      }
    }
  ]
}
EOF

echo "Trust policy file created:"
cat trust-policy.json

# Update the role
echo "Updating IAM role trust policy..."
aws iam update-assume-role-policy \
    --role-name $ROLE_NAME \
    --policy-document file://trust-policy.json

echo "✅ Trust policy updated!"

# Verify
echo "Verifying trust policy..."
aws iam get-role \
    --role-name $ROLE_NAME \
    --query 'Role.AssumeRolePolicyDocument' \
    --output json | python -m json.tool

echo "✅ All set! You can now retry the deployment."
```

**Save as**: `fix-oidc-trust.sh`

**Run**:
```bash
chmod +x fix-oidc-trust.sh
./fix-oidc-trust.sh
```

---

## 🎯 Next Steps

1. **Fix the trust policy** using steps above
2. **Verify** all checks pass
3. **Go to GitHub Actions**
4. **Re-run the failed workflow**
5. **Monitor** deployment progress

---

## 📞 Still Not Working?

If still getting OIDC errors, try these:

### Option 1: Delete and Recreate Role
```bash
# Delete the role (this will also delete trust policy)
aws iam delete-role --role-name GitHubActionsADRDeployRole

# Wait a moment
sleep 2

# Recreate with correct trust policy
aws iam create-role \
    --role-name GitHubActionsADRDeployRole \
    --assume-role-policy-document file://trust-policy.json

# Attach permissions
aws iam attach-role-policy \
    --role-name GitHubActionsADRDeployRole \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

### Option 2: Use Alternative IAM Credentials (Temporary)
If OIDC continues failing, as a workaround you can:
1. Create IAM user with AWS keys
2. Store keys as GitHub secrets
3. Use those for authentication

**But OIDC is better** - it's more secure and doesn't require credentials rotation.

---

## 🔐 Security Best Practices

**Your trust policy should:**
- ✅ Specify the OIDC provider ARN
- ✅ Restrict to your GitHub organization: `repo:anoopmc1981/AI-Project-ADR:*`
- ✅ Use `sts:AssumeRoleWithWebIdentity` action
- ✅ Require specific audience: `sts.amazonaws.com`

**Don't:**
- ❌ Use wildcards for all repos: `repo:*`
- ❌ Use wildcards for all organizations: `repo:*:*`
- ❌ Allow any principal

---

**After fixing the trust policy, your deployment should work! 🚀**
