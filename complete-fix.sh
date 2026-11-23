#!/bin/bash

echo "🔧 Complete OIDC Trust Policy Fix"
echo "=================================="
echo ""

# Step 1: Get Account ID
echo "Step 1: Getting AWS Account ID..."
ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
if [ -z "$ACCOUNT_ID" ]; then
    echo "❌ Failed to get Account ID. Check AWS CLI and credentials."
    exit 1
fi
echo "✅ Account ID: $ACCOUNT_ID"
echo ""

# Step 2: Create trust policy
echo "Step 2: Creating trust policy JSON..."
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
echo ""
echo "Trust Policy Content:"
cat final-trust-policy.json
echo ""
echo ""

# Step 3: Verify OIDC provider exists
echo "Step 3: Verifying OIDC Provider exists..."
OIDC_PROVIDER_ARN="arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
if aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$OIDC_PROVIDER_ARN" > /dev/null 2>&1; then
    echo "✅ OIDC Provider exists: $OIDC_PROVIDER_ARN"
else
    echo "⚠️  OIDC Provider not found. Creating..."
    aws iam create-open-id-connect-provider \
        --url https://token.actions.githubusercontent.com \
        --client-id-list sts.amazonaws.com \
        --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
    echo "✅ OIDC Provider created"
fi
echo ""

# Step 4: Delete old role if exists
echo "Step 4: Cleaning up old role..."
if aws iam get-role --role-name GitHubActionsADRDeployRole > /dev/null 2>&1; then
    echo "Found existing role. Deleting..."
    
    # Detach all policies
    POLICIES=$(aws iam list-attached-role-policies \
        --role-name GitHubActionsADRDeployRole \
        --query 'AttachedPolicies[*].PolicyArn' \
        --output text)
    
    for POLICY_ARN in $POLICIES; do
        echo "Detaching policy: $POLICY_ARN"
        aws iam detach-role-policy \
            --role-name GitHubActionsADRDeployRole \
            --policy-arn $POLICY_ARN
    done
    
    # Delete role
    echo "Deleting role..."
    aws iam delete-role --role-name GitHubActionsADRDeployRole
    echo "✅ Old role deleted"
else
    echo "ℹ️  No existing role found"
fi
echo ""

# Step 5: Create new role
echo "Step 5: Creating new role with correct trust policy..."
aws iam create-role \
    --role-name GitHubActionsADRDeployRole \
    --assume-role-policy-document file://final-trust-policy.json

if [ $? -eq 0 ]; then
    echo "✅ New role created: GitHubActionsADRDeployRole"
else
    echo "❌ Failed to create role"
    exit 1
fi
echo ""

# Step 6: Attach permissions
echo "Step 6: Attaching permissions..."
aws iam attach-role-policy \
    --role-name GitHubActionsADRDeployRole \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

if [ $? -eq 0 ]; then
    echo "✅ AdministratorAccess policy attached"
else
    echo "❌ Failed to attach policy"
    exit 1
fi
echo ""

# Step 7: Get role ARN
echo "Step 7: Getting role ARN..."
ROLE_ARN=$(aws iam get-role \
    --role-name GitHubActionsADRDeployRole \
    --query 'Role.Arn' \
    --output text)

echo "✅ Role ARN: $ROLE_ARN"
echo ""

# Step 8: Final verification
echo "Step 8: Final verification..."
echo ""
echo "Current Trust Policy:"
aws iam get-role \
    --role-name GitHubActionsADRDeployRole \
    --query 'Role.AssumeRolePolicyDocument' \
    --output json | python -m json.tool
echo ""

echo "Attached Policies:"
aws iam list-attached-role-policies \
    --role-name GitHubActionsADRDeployRole \
    --output table
echo ""

# Success summary
echo "=================================="
echo "✅ COMPLETE OIDC FIX FINISHED!"
echo "=================================="
echo ""
echo "📋 IMPORTANT: Copy the Role ARN below and update GitHub secret"
echo ""
echo "Role ARN:"
echo "$ROLE_ARN"
echo ""
echo "Steps to complete:"
echo "1. Go to: https://github.com/anoopmc1981/AI-Project-ADR/settings/secrets/actions"
echo "2. Find or create secret: AWS_IAM_ROLE_ARN"
echo "3. Set the value to: $ROLE_ARN"
echo "4. Click 'Update secret'"
echo ""
echo "5. Go to GitHub Actions: https://github.com/anoopmc1981/AI-Project-ADR/actions"
echo "6. Find the failed workflow run"
echo "7. Click 'Re-run failed jobs'"
echo "8. Watch the deployment (30-40 minutes)"
echo ""
echo "The deployment should now succeed! 🚀"
