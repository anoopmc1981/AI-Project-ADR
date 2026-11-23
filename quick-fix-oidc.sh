#!/bin/bash

# Quick Fix for OIDC Trust Policy Issue
# Run this script to fix the deployment failure

echo "🔧 ADR Scanner - OIDC Trust Policy Quick Fix"
echo "============================================"
echo ""

# Step 1: Get AWS Account ID
echo "Step 1: Getting AWS Account ID..."
ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
if [ -z "$ACCOUNT_ID" ]; then
    echo "❌ Failed to get Account ID. Check AWS credentials."
    exit 1
fi
echo "✅ Account ID: $ACCOUNT_ID"

# Step 2: Create trust policy JSON
echo ""
echo "Step 2: Creating trust policy JSON..."

GITHUB_ORG="anoopmc1981"
GITHUB_REPO="AI-Project-ADR"
ROLE_NAME="GitHubActionsADRDeployRole"
TRUST_POLICY_FILE="trust-policy.json"

cat > "$TRUST_POLICY_FILE" << EOF
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

echo "✅ Trust policy created"
echo ""
echo "Trust Policy Content:"
cat "$TRUST_POLICY_FILE"
echo ""
echo "✅ Saved to: $TRUST_POLICY_FILE"

# Step 3: Verify role exists
echo ""
echo "Step 3: Verifying IAM role exists..."
if aws iam get-role --role-name "$ROLE_NAME" > /dev/null 2>&1; then
    ROLE_ARN=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)
    echo "✅ Role found: $ROLE_ARN"
else
    echo "❌ Role not found. Creating it..."
    aws iam create-role \
        --role-name "$ROLE_NAME" \
        --assume-role-policy-document file://"$TRUST_POLICY_FILE"
    echo "✅ Role created"
fi

# Step 4: Update trust policy
echo ""
echo "Step 4: Updating trust policy..."
if aws iam update-assume-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-document file://"$TRUST_POLICY_FILE"; then
    echo "✅ Trust policy updated successfully!"
else
    echo "❌ Failed to update trust policy"
    exit 1
fi

# Step 5: Verify permissions
echo ""
echo "Step 5: Verifying permissions..."
POLICIES=$(aws iam list-attached-role-policies --role-name "$ROLE_NAME" --query 'AttachedPolicies[*].PolicyName' --output text)
if [[ "$POLICIES" == *"AdministratorAccess"* ]]; then
    echo "✅ Administrator policy attached"
else
    echo "⚠️  Administrator policy not found. Attaching..."
    aws iam attach-role-policy \
        --role-name "$ROLE_NAME" \
        --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
    echo "✅ Administrator policy attached"
fi

# Step 6: Get role ARN
echo ""
echo "Step 6: Getting role ARN for GitHub secret..."
ROLE_ARN=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)
echo "✅ Role ARN: $ROLE_ARN"
echo ""
echo "⚠️  Make sure this is set in GitHub secret: AWS_IAM_ROLE_ARN"

# Step 7: Final verification
echo ""
echo "Step 7: Final verification..."
TRUST_POLICY=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.AssumeRolePolicyDocument' --output json)
SUB_CONDITION=$(echo "$TRUST_POLICY" | grep -o "repo:${GITHUB_ORG}/${GITHUB_REPO}:\*" || echo "")

if [ ! -z "$SUB_CONDITION" ]; then
    echo "✅ Trust policy is correctly configured for your GitHub repo"
else
    echo "⚠️  Trust policy may not be correct. Expected: repo:${GITHUB_ORG}/${GITHUB_REPO}:*"
fi

# Summary
echo ""
echo "============================================"
echo "✅ OIDC TRUST POLICY FIX COMPLETE!"
echo "============================================"
echo ""
echo "Next Steps:"
echo "1. Go to GitHub Actions: https://github.com/${GITHUB_ORG}/AI-Project-ADR/actions"
echo "2. Find the failed workflow run"
echo "3. Click 'Re-run failed jobs'"
echo "4. Watch the deployment progress"
echo ""
echo "The deployment should now succeed! 🚀"
