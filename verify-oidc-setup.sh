#!/bin/bash

# ========================================================================
# OIDC Setup Verification Script
# Run this in Git Bash to verify all AWS OIDC components
# ========================================================================

set +e  # Don't exit on errors - we want to see all results

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           AWS OIDC Setup Verification Script                  ║"
echo "║                 (For ADR Scanner Project)                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

ACCOUNT_ID="471533886200"
ROLE_NAME="GitHubActionsADRDeployRole"
IDENTITY_PROVIDER="token.actions.githubusercontent.com"
REPOSITORY="repo:anoopmc1981/AI-Project-ADR:*"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "Account ID: $ACCOUNT_ID"
echo "Role Name: $ROLE_NAME"
echo "Identity Provider: $IDENTITY_PROVIDER"
echo "Repository: $REPOSITORY"
echo ""

# ========================================================================
# CHECK 1: AWS CLI Available
# ========================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ CHECK 1: AWS CLI Available"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version)
    echo -e "${GREEN}✅ AWS CLI is installed${NC}"
    echo "   Version: $AWS_VERSION"
else
    echo -e "${RED}❌ AWS CLI is NOT installed${NC}"
    exit 1
fi
echo ""

# ========================================================================
# CHECK 2: AWS Credentials
# ========================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ CHECK 2: AWS Credentials"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CALLER_IDENTITY=$(aws sts get-caller-identity 2>&1)
if echo "$CALLER_IDENTITY" | grep -q "Account"; then
    echo -e "${GREEN}✅ AWS Credentials are configured${NC}"
    CALLER_ACCOUNT=$(echo "$CALLER_IDENTITY" | grep -o '"Account": "[^"]*"' | cut -d'"' -f4)
    CALLER_ARN=$(echo "$CALLER_IDENTITY" | grep -o '"Arn": "[^"]*"' | cut -d'"' -f4)
    echo "   Account: $CALLER_ACCOUNT"
    echo "   ARN: $CALLER_ARN"
else
    echo -e "${RED}❌ AWS Credentials are NOT configured or invalid${NC}"
    echo "   Error: $CALLER_IDENTITY"
    exit 1
fi
echo ""

# ========================================================================
# CHECK 3: IAM Role Exists
# ========================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ CHECK 3: IAM Role Exists"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ROLE_INFO=$(aws iam get-role --role-name "$ROLE_NAME" 2>&1)
if echo "$ROLE_INFO" | grep -q "Arn"; then
    echo -e "${GREEN}✅ IAM Role exists${NC}"
    ROLE_ARN=$(echo "$ROLE_INFO" | grep -o '"Arn": "[^"]*"' | cut -d'"' -f4 | head -1)
    ROLE_CREATE_DATE=$(echo "$ROLE_INFO" | grep -o '"CreateDate": "[^"]*"' | cut -d'"' -f4)
    echo "   Role Name: $ROLE_NAME"
    echo "   Role ARN: $ROLE_ARN"
    echo "   Created: $ROLE_CREATE_DATE"
else
    echo -e "${RED}❌ IAM Role does NOT exist${NC}"
    echo "   Need to create: $ROLE_NAME"
    exit 1
fi
echo ""

# ========================================================================
# CHECK 4: Trust Policy
# ========================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ CHECK 4: Trust Policy"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

TRUST_POLICY=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.AssumeRolePolicyDocument' 2>&1)

# Check for OIDC provider in trust policy
if echo "$TRUST_POLICY" | grep -q "token.actions.githubusercontent.com"; then
    echo -e "${GREEN}✅ Trust Policy references OIDC provider${NC}"
else
    echo -e "${RED}❌ Trust Policy does NOT reference OIDC provider${NC}"
fi

# Check for StringEquals condition
if echo "$TRUST_POLICY" | grep -q "StringEquals"; then
    echo -e "${GREEN}✅ Trust Policy has StringEquals condition${NC}"
else
    echo -e "${RED}❌ Trust Policy missing StringEquals condition${NC}"
fi

# Check for StringLike condition
if echo "$TRUST_POLICY" | grep -q "StringLike"; then
    echo -e "${GREEN}✅ Trust Policy has StringLike condition${NC}"
else
    echo -e "${RED}❌ Trust Policy missing StringLike condition${NC}"
fi

# Check for audience
if echo "$TRUST_POLICY" | grep -q "sts.amazonaws.com"; then
    echo -e "${GREEN}✅ Trust Policy has audience: sts.amazonaws.com${NC}"
else
    echo -e "${RED}❌ Trust Policy missing audience condition${NC}"
fi

# Check for repository
if echo "$TRUST_POLICY" | grep -q "anoopmc1981/AI-Project-ADR"; then
    echo -e "${GREEN}✅ Trust Policy references correct repository${NC}"
else
    echo -e "${RED}❌ Trust Policy does NOT reference correct repository${NC}"
fi

echo ""
echo "Full Trust Policy:"
echo "─────────────────────────────────────────────────────────────────"
echo "$TRUST_POLICY" | python3 -m json.tool 2>/dev/null || echo "$TRUST_POLICY"
echo "─────────────────────────────────────────────────────────────────"
echo ""

# ========================================================================
# CHECK 5: Role Policies (Permissions)
# ========================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ CHECK 5: Role Policies (Permissions)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

POLICIES=$(aws iam list-attached-role-policies --role-name "$ROLE_NAME" 2>&1)

if echo "$POLICIES" | grep -q "AdministratorAccess"; then
    echo -e "${GREEN}✅ AdministratorAccess policy is attached${NC}"
else
    echo -e "${RED}❌ AdministratorAccess policy is NOT attached${NC}"
fi

if echo "$POLICIES" | grep -q "AttachedPolicies"; then
    POLICY_COUNT=$(echo "$POLICIES" | grep -o '"PolicyName"' | wc -l)
    if [ "$POLICY_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ Role has $POLICY_COUNT policy/policies attached${NC}"
    else
        echo -e "${RED}❌ No policies attached to role${NC}"
    fi
else
    echo -e "${RED}❌ Error checking policies${NC}"
fi

echo ""
echo "Policies:"
echo "─────────────────────────────────────────────────────────────────"
echo "$POLICIES" | grep -E '"PolicyName"|"PolicyArn"' || echo "No policies found"
echo "─────────────────────────────────────────────────────────────────"
echo ""

# ========================================================================
# CHECK 6: Identity Provider
# ========================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ CHECK 6: Identity Provider"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

PROVIDER_ARN="arn:aws:iam::${ACCOUNT_ID}:oidc-provider/${IDENTITY_PROVIDER}"

PROVIDER_INFO=$(aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$PROVIDER_ARN" 2>&1)

if echo "$PROVIDER_INFO" | grep -q "Url"; then
    echo -e "${GREEN}✅ Identity Provider exists${NC}"
    PROVIDER_URL=$(echo "$PROVIDER_INFO" | grep -o '"Url": "[^"]*"' | cut -d'"' -f4)
    echo "   Provider URL: $PROVIDER_URL"
else
    echo -e "${RED}❌ Identity Provider does NOT exist${NC}"
    echo "   Provider ARN: $PROVIDER_ARN"
fi

if echo "$PROVIDER_INFO" | grep -q "sts.amazonaws.com"; then
    echo -e "${GREEN}✅ Provider has correct audience: sts.amazonaws.com${NC}"
else
    echo -e "${YELLOW}⚠️  Cannot verify audience${NC}"
fi

echo ""
echo "Provider Details:"
echo "─────────────────────────────────────────────────────────────────"
echo "$PROVIDER_INFO" | python3 -m json.tool 2>/dev/null || echo "$PROVIDER_INFO"
echo "─────────────────────────────────────────────────────────────────"
echo ""

# ========================================================================
# CHECK 7: Workflow File
# ========================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ CHECK 7: Workflow File"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

WORKFLOW_FILE=".github/workflows/deploy.yml"

if [ -f "$WORKFLOW_FILE" ]; then
    echo -e "${GREEN}✅ Workflow file exists${NC}"
    echo "   File: $WORKFLOW_FILE"
else
    echo -e "${RED}❌ Workflow file NOT found${NC}"
    echo "   Expected: $WORKFLOW_FILE"
fi

if grep -q "id-token: write" "$WORKFLOW_FILE"; then
    echo -e "${GREEN}✅ Workflow has 'id-token: write' permission${NC}"
else
    echo -e "${RED}❌ Workflow missing 'id-token: write' permission${NC}"
fi

if grep -q "aws-actions/configure-aws-credentials@v4" "$WORKFLOW_FILE"; then
    echo -e "${GREEN}✅ Workflow uses aws-actions/configure-aws-credentials@v4${NC}"
else
    echo -e "${RED}❌ Workflow NOT using correct credentials action${NC}"
fi

if grep -q "arn:aws:iam::471533886200:role/GitHubActionsADRDeployRole" "$WORKFLOW_FILE"; then
    echo -e "${GREEN}✅ Workflow has correct hardcoded role ARN${NC}"
else
    echo -e "${RED}❌ Workflow does NOT have correct role ARN${NC}"
fi

echo ""

# ========================================================================
# FINAL SUMMARY
# ========================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ FINAL SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Count successes
CHECKS_PASSED=0
CHECKS_FAILED=0

if echo "$CALLER_IDENTITY" | grep -q "Account"; then ((CHECKS_PASSED++)); else ((CHECKS_FAILED++)); fi
if echo "$ROLE_INFO" | grep -q "Arn"; then ((CHECKS_PASSED++)); else ((CHECKS_FAILED++)); fi
if echo "$TRUST_POLICY" | grep -q "token.actions.githubusercontent.com"; then ((CHECKS_PASSED++)); else ((CHECKS_FAILED++)); fi
if echo "$POLICIES" | grep -q "AdministratorAccess"; then ((CHECKS_PASSED++)); else ((CHECKS_FAILED++)); fi
if echo "$PROVIDER_INFO" | grep -q "Url"; then ((CHECKS_PASSED++)); else ((CHECKS_FAILED++)); fi
if [ -f "$WORKFLOW_FILE" ] && grep -q "id-token: write" "$WORKFLOW_FILE"; then ((CHECKS_PASSED++)); else ((CHECKS_FAILED++)); fi

echo "Checks Passed: ${GREEN}$CHECKS_PASSED${NC}"
echo "Checks Failed: ${RED}$CHECKS_FAILED${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ALL CHECKS PASSED - OIDC Setup is Correct!                 ║${NC}"
    echo -e "${GREEN}║  Ready to deploy! Try re-running the workflow.                 ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ $CHECKS_FAILED Check(s) Failed - Fix issues above            ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
fi

echo ""
echo "END OF VERIFICATION SCRIPT"
echo ""

exit $CHECKS_FAILED
