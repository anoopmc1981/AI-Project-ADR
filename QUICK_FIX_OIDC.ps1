# Quick Fix for OIDC Trust Policy Issue
# Run this PowerShell script to fix the deployment failure

Write-Host "🔧 ADR Scanner - OIDC Trust Policy Quick Fix" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

# Step 1: Get AWS Account ID
Write-Host "Step 1: Getting AWS Account ID..." -ForegroundColor Cyan
try {
    $accountId = aws sts get-caller-identity --query 'Account' --output text
    Write-Host "✅ Account ID: $accountId" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to get Account ID. Check AWS credentials." -ForegroundColor Red
    exit 1
}

# Step 2: Create trust policy JSON
Write-Host ""
Write-Host "Step 2: Creating trust policy JSON..." -ForegroundColor Cyan

$githubOrg = "anoopmc1981"
$githubRepo = "AI-Project-ADR"
$roleName = "GitHubActionsADRDeployRole"

$trustPolicy = @{
    Version = "2012-10-17"
    Statement = @(
        @{
            Effect = "Allow"
            Principal = @{
                Federated = "arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com"
            }
            Action = "sts:AssumeRoleWithWebIdentity"
            Condition = @{
                StringEquals = @{
                    "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
                }
                StringLike = @{
                    "token.actions.githubusercontent.com:sub" = "repo:${githubOrg}/${githubRepo}:*"
                }
            }
        }
    )
} | ConvertTo-Json -Depth 10

Write-Host "✅ Trust policy created" -ForegroundColor Green
Write-Host ""
Write-Host "Trust Policy Content:" -ForegroundColor Yellow
Write-Host $trustPolicy
Write-Host ""

# Step 3: Save to file
$trustPolicyFile = "trust-policy.json"
$trustPolicy | Out-File -FilePath $trustPolicyFile -Encoding UTF8
Write-Host "✅ Saved to: $trustPolicyFile" -ForegroundColor Green

# Step 4: Verify role exists
Write-Host ""
Write-Host "Step 3: Verifying IAM role exists..." -ForegroundColor Cyan
try {
    $role = aws iam get-role --role-name $roleName --query 'Role.Arn' --output text
    Write-Host "✅ Role found: $role" -ForegroundColor Green
} catch {
    Write-Host "❌ Role not found. Creating it..." -ForegroundColor Yellow
    aws iam create-role `
        --role-name $roleName `
        --assume-role-policy-document file://$trustPolicyFile
    Write-Host "✅ Role created" -ForegroundColor Green
}

# Step 5: Update trust policy
Write-Host ""
Write-Host "Step 4: Updating trust policy..." -ForegroundColor Cyan
try {
    aws iam update-assume-role-policy `
        --role-name $roleName `
        --policy-document file://$trustPolicyFile
    Write-Host "✅ Trust policy updated successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to update trust policy: $_" -ForegroundColor Red
    exit 1
}

# Step 6: Verify permissions
Write-Host ""
Write-Host "Step 5: Verifying permissions..." -ForegroundColor Cyan
try {
    $policies = aws iam list-attached-role-policies --role-name $roleName --query 'AttachedPolicies[*].PolicyName' --output text
    if ($policies -like "*Administrator*") {
        Write-Host "✅ Administrator policy attached" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Administrator policy not found. Attaching..." -ForegroundColor Yellow
        aws iam attach-role-policy `
            --role-name $roleName `
            --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
        Write-Host "✅ Administrator policy attached" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Failed to check permissions: $_" -ForegroundColor Red
}

# Step 7: Get role ARN
Write-Host ""
Write-Host "Step 6: Getting role ARN for GitHub secret..." -ForegroundColor Cyan
try {
    $roleArn = aws iam get-role --role-name $roleName --query 'Role.Arn' --output text
    Write-Host "✅ Role ARN: $roleArn" -ForegroundColor Green
    Write-Host ""
    Write-Host "Make sure this is set in GitHub secret: AWS_IAM_ROLE_ARN" -ForegroundColor Yellow
} catch {
    Write-Host "❌ Failed to get role ARN: $_" -ForegroundColor Red
}

# Step 8: Final verification
Write-Host ""
Write-Host "Step 7: Final verification..." -ForegroundColor Cyan
try {
    $finalPolicy = aws iam get-role --role-name $roleName --query 'Role.AssumeRolePolicyDocument' | ConvertFrom-Json
    $subCondition = $finalPolicy.Statement[0].Condition.StringLike."token.actions.githubusercontent.com:sub"
    
    if ($subCondition -like "*${githubOrg}/${githubRepo}*") {
        Write-Host "✅ Trust policy is correctly configured for your GitHub repo" -ForegroundColor Green
    } else {
        Write-Host "❌ Trust policy may not be correct. Expected: repo:${githubOrg}/${githubRepo}:*" -ForegroundColor Red
    }
} catch {
    Write-Host "⚠️  Could not verify trust policy: $_" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "✅ OIDC TRUST POLICY FIX COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Go to GitHub Actions: https://github.com/anoopmc1981/AI-Project-ADR/actions" -ForegroundColor White
Write-Host "2. Find the failed workflow run" -ForegroundColor White
Write-Host "3. Click 'Re-run failed jobs'" -ForegroundColor White
Write-Host "4. Watch the deployment progress" -ForegroundColor White
Write-Host ""
Write-Host "The deployment should now succeed! 🚀" -ForegroundColor Green
