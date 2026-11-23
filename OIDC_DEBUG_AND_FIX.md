# 🔍 OIDC Debug & Complete Fix Guide

## Status

Your OIDC trust policy is **still not working**. Let's debug and fix it step by step.

---

## Step 1: Debug Current Configuration

Run these commands in Git Bash to see what's currently configured:

### 1a. Get Your AWS Account ID
```bash
aws sts get-caller-identity
```

**Save the output** - you'll need the Account ID (looks like `123456789012`)

### 1b. Check if IAM Role Exists
```bash
aws iam get-role --role-name GitHubActionsADRDeployRole
```

**Expected output**: Should show role details with ARN

**If error "NoSuchEntity"**: Role doesn't exist - go to Step 3

### 1c. View Current Trust Policy
```bash
aws iam get-role \
    --role-name GitHubActionsADRDeployRole \
    --query 'Role.AssumeRolePolicyDocument' \
    --output json > current-trust-policy.json

cat current-trust-policy.json
```

**Save this output** - we need to compare it

### 1d. Check OIDC Provider
```bash
aws iam list-open-id-connect-providers
```

**Expected output**: Should show:
```
arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com
```

---

## Step 2: Create CORRECT Trust Policy

The trust policy **MUST** have:
1. Correct AWS Account ID (from Step 1a)
2. Correct GitHub org: `anoopmc1981`
3. Correct GitHub repo: `AI-Project-ADR`
4. Wildcard for all branches: `:*`

### Create the JSON file

In Git Bash, run:

```bash
# Replace YOUR_ACCOUNT_ID with actual ID from Step 1a
# Example: 123456789012

cat > trust-policy-correct.json << 'EOF'
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
EOF
```

### View the file to verify
```bash
cat trust-policy-correct.json
```

**Check for:**
- ✅ `YOUR_ACCOUNT_ID` replaced with actual ID
- ✅ `anoopmc1981` is correct
- ✅ `AI-Project-ADR` is correct
- ✅ Ends with `:*` (wildcard)

---

## Step 3: Delete Old Role & Create New One

### 3a. Delete the existing role
```bash
# First, detach all policies
aws iam list-attached-role-policies \
    --role-name GitHubActionsADRDeployRole \
    --query 'AttachedPolicies[*].PolicyArn' \
    --output text | xargs -I {} aws iam detach-role-policy \
    --role-name GitHubActionsADRDeployRole \
    --policy-arn {}

# Then delete the role
aws iam delete-role --role-name GitHubActionsADRDeployRole

echo "Role deleted successfully"
```

### 3b. Create brand new role with correct trust policy
```bash
# Create the role with the correct trust policy
aws iam create-role \
    --role-name GitHubActionsADRDeployRole \
    --assume-role-policy-document file://trust-policy-correct.json

echo "Role created successfully"
```

### 3c. Attach permissions
```bash
aws iam attach-role-policy \
    --role-name GitHubActionsADRDeployRole \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

echo "Permissions attached"
```

---

## Step 4: Verify Everything

### 4a. Get Role ARN
```bash
ROLE_ARN=$(aws iam get-role \
    --role-name GitHubActionsADRDeployRole \
    --query 'Role.Arn' \
    --output text)

echo "Role ARN: $ROLE_ARN"
```

**Copy this ARN** - you need it for GitHub secret!

### 4b. Verify Trust Policy
```bash
aws iam get-role \
    --role-name GitHubActionsADRDeployRole \
    --query 'Role.AssumeRolePolicyDocument' \
    --output json | python -m json.tool
```

**Check for:**
- ✅ `"Federated"` contains correct account ID
- ✅ `"repo:anoopmc1981/AI-Project-ADR:*"` is in condition
- ✅ No syntax errors

### 4c. Verify Permissions
```bash
aws iam list-attached-role-policies \
    --role-name GitHubActionsADRDeployRole
```

**Should show:**
```json
{
    "AttachedPolicies": [
        {
            "PolicyName": "AdministratorAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
        }
    ]
}
```

---

## Step 5: Update GitHub Secret

### 5a. Get the Role ARN
```bash
aws iam get-role \
    --role-name GitHubActionsADRDeployRole \
    --query 'Role.Arn' \
    --output text
```

**Copy the output** (looks like: `arn:aws:iam::123456789012:role/GitHubActionsADRDeployRole`)

### 5b. Update GitHub Secret

1. Go to: https://github.com/anoopmc1981/AI-Project-ADR/settings/secrets/actions

2. Find or create secret `AWS_IAM_ROLE_ARN`

3. Update the value with the ARN from Step 5a

4. Click **Update secret**

---

## Step 6: Complete Verification Script

Run this all-in-one script to verify everything:

```bash
#!/bin/bash

echo "🔍 OIDC Configuration Verification"
echo "===================================="
echo ""

# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
echo "✅ AWS Account ID: $ACCOUNT_ID"
echo ""

# Check role exists
if aws iam get-role --role-name GitHubActionsADRDeployRole > /dev/null 2>&1; then
    echo "✅ Role exists: GitHubActionsADRDeployRole"
else
    echo "❌ Role NOT found!"
    exit 1
fi
echo ""

# Check OIDC provider
OIDC_PROVIDER="arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
if aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$OIDC_PROVIDER" > /dev/null 2>&1; then
    echo "✅ OIDC Provider exists: $OIDC_PROVIDER"
else
    echo "❌ OIDC Provider NOT found!"
    exit 1
fi
echo ""

# Check trust policy
echo "📋 Trust Policy:"
aws iam get-role \
    --role-name GitHubActionsADRDeployRole \
    --query 'Role.AssumeRolePolicyDocument' \
    --output json | python -m json.tool
echo ""

# Check permissions
echo "🔑 Attached Policies:"
aws iam list-attached-role-policies \
    --role-name GitHubActionsADRDeployRole \
    --output table
echo ""

# Get role ARN
ROLE_ARN=$(aws iam get-role \
    --role-name GitHubActionsADRDeployRole \
    --query 'Role.Arn' \
    --output text)
echo "🎯 Role ARN (use for GitHub secret):"
echo "$ROLE_ARN"
echo ""

echo "✅ All checks passed! Ready to deploy."
```

**Save this as**: `verify-oidc.sh`

**Run it**:
```bash
bash verify-oidc.sh
```

---

## ✅ Complete Manual Fix (All Steps)

If you want to do everything manually in one go:

```bash
#!/bin/bash

echo "🔧 Complete OIDC Fix"
echo "===================="

# Step 1: Get Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
echo "Account ID: $ACCOUNT_ID"

# Step 2: Create trust policy
cat > final-trust-policy.json << EOF
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
          "token.actions.githubusercontent.com:sub": "repo:anoopmc1981/AI-Project-ADR:*"
        }
      }
    }
  ]
}
EOF

echo "✅ Trust policy created"

# Step 3: Delete old role
echo "Deleting old role..."
aws iam list-attached-role-policies --role-name GitHubActionsADRDeployRole \
    --query 'AttachedPolicies[*].PolicyArn' --output text | \
    xargs -I {} aws iam detach-role-policy \
    --role-name GitHubActionsADRDeployRole --policy-arn {} 2>/dev/null

aws iam delete-role --role-name GitHubActionsADRDeployRole 2>/dev/null
echo "✅ Old role deleted"

# Step 4: Create new role
echo "Creating new role..."
aws iam create-role \
    --role-name GitHubActionsADRDeployRole \
    --assume-role-policy-document file://final-trust-policy.json

echo "✅ New role created"

# Step 5: Attach permissions
echo "Attaching permissions..."
aws iam attach-role-policy \
    --role-name GitHubActionsADRDeployRole \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

echo "✅ Permissions attached"

# Step 6: Get role ARN
ROLE_ARN=$(aws iam get-role \
    --role-name GitHubActionsADRDeployRole \
    --query 'Role.Arn' \
    --output text)

echo ""
echo "======================================"
echo "✅ OIDC FIX COMPLETE!"
echo "======================================"
echo ""
echo "Role ARN (copy this to GitHub secret):"
echo "$ROLE_ARN"
echo ""
echo "Next: Update GitHub secret AWS_IAM_ROLE_ARN with the value above"
echo ""
```

**Save as**: `complete-fix.sh`

**Run it**:
```bash
bash complete-fix.sh
```

---

## 🚀 After Fix

1. **Update GitHub secret** with new role ARN
2. **Go to GitHub Actions**: https://github.com/anoopmc1981/AI-Project-ADR/actions
3. **Re-run failed workflow**
4. **Watch deployment** (should now succeed!)

---

## ⚠️ If Still Failing

If you still get the OIDC error after this, check:

### Check 1: GitHub Secret Value
```bash
# This just shows how to verify (you can't see the actual value)
# But make sure in GitHub:
# Secret Name: AWS_IAM_ROLE_ARN
# Secret Value: arn:aws:iam::YOUR_ACCOUNT_ID:role/GitHubActionsADRDeployRole
```

### Check 2: GitHub Organization Name
```bash
# Make sure it's exactly: anoopmc1981
# Not: Anoopmc1981 or ANOOPMC1981
# Case matters!
```

### Check 3: GitHub Repo Name
```bash
# Make sure it's exactly: AI-Project-ADR
# Not: ai-project-adr or AI-PROJECT-ADR
# Case matters!
```

### Check 4: OIDC Provider
```bash
aws iam get-open-id-connect-provider \
    --open-id-connect-provider-arn "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
```

Should show provider details.

If error "NoSuchEntity", create OIDC provider:
```bash
aws iam create-open-id-connect-provider \
    --url https://token.actions.githubusercontent.com \
    --client-id-list sts.amazonaws.com \
    --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

---

## 📋 Checklist Before Re-running Workflow

- [ ] Trust policy created with correct Account ID
- [ ] Role deleted and recreated
- [ ] Trust policy contains `repo:anoopmc1981/AI-Project-ADR:*`
- [ ] Permissions attached (AdministratorAccess)
- [ ] GitHub secret `AWS_IAM_ROLE_ARN` updated with new role ARN
- [ ] GitHub secret value verified (copy-pasted correctly)
- [ ] OIDC provider verified to exist

---

**Run the complete-fix.sh script now, then update GitHub secret, then re-run workflow!** 🚀
