# ❌ Deployment Failure - OIDC Trust Policy Issue

## What Failed?

Your GitHub Actions workflow failed at the AWS credential configuration step:

```
Error: Could not assume role with OIDC: 
Not authorized to perform sts:AssumeRoleWithWebIdentity
```

---

## Root Cause

Your AWS IAM role's **trust policy** (assume role policy) is not correctly configured to allow GitHub Actions to assume the role.

The trust policy needs to:
1. Trust the OIDC provider: `token.actions.githubusercontent.com`
2. Allow your specific GitHub repository to assume the role
3. Have the correct AWS account ID and GitHub organization/repo

---

## 🔧 Quick Fix (Choose One Method)

### Method 1: PowerShell Script (Windows)

```powershell
# Run from your project directory
.\QUICK_FIX_OIDC.ps1
```

This will automatically:
- Get your AWS Account ID
- Create correct trust policy JSON
- Update the IAM role
- Verify everything is working

### Method 2: Bash Script (macOS/Linux)

```bash
# Run from your project directory
bash quick-fix-oidc.sh
```

Same as PowerShell - automated fix.

### Method 3: Manual Fix (AWS CLI)

```bash
# Step 1: Get your AWS Account ID
aws sts get-caller-identity --query 'Account' --output text
# Note: Save this ID (e.g., 123456789012)

# Step 2: Create trust-policy.json file with this content:
# (Replace YOUR_AWS_ACCOUNT_ID with the ID from Step 1)

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

# Step 3: Update the IAM role trust policy
aws iam update-assume-role-policy \
    --role-name GitHubActionsADRDeployRole \
    --policy-document file://trust-policy.json

# Step 4: Verify it worked
aws iam get-role \
    --role-name GitHubActionsADRDeployRole \
    --query 'Role.AssumeRolePolicyDocument'
```

---

## 🚀 After Fixing

Once you've applied the fix:

1. **Go to GitHub Actions Tab:**
   https://github.com/anoopmc1981/AI-Project-ADR/actions

2. **Find the failed workflow run** (the one that just failed)

3. **Click "Re-run failed jobs"** button

4. **Watch the deployment progress:**
   - Should pass the "Configure AWS Credentials" step
   - Should continue to build and deploy
   - Total time: 30-40 minutes

5. **Monitor each step:**
   - ✅ Checkout code
   - ✅ Setup Python
   - ✅ **Configure AWS Credentials** (this was failing)
   - ✅ Build SAM
   - ✅ Deploy backend
   - ✅ Deploy frontend
   - ✅ Run tests
   - ✅ Success!

---

## ✅ Common Issues & Solutions

### Still getting "Not authorized"?

**Check 1: Trust policy syntax**
```bash
# Make sure JSON is valid
python -m json.tool trust-policy.json
```

**Check 2: Account ID is correct**
```bash
aws sts get-caller-identity
# Should show your account ID like: 123456789012
# Make sure this matches in the trust policy
```

**Check 3: GitHub username is correct**
- Should be: `anoopmc1981`
- Should match your repository path
- Should be lowercase

**Check 4: OIDC provider exists**
```bash
aws iam list-open-id-connect-providers
# Should show: arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com
```

### OIDC provider not found?

Create it:
```bash
aws iam create-open-id-connect-provider \
    --url https://token.actions.githubusercontent.com \
    --client-id-list sts.amazonaws.com \
    --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### Role not found?

Create it:
```bash
aws iam create-role \
    --role-name GitHubActionsADRDeployRole \
    --assume-role-policy-document file://trust-policy.json

# Attach permissions
aws iam attach-role-policy \
    --role-name GitHubActionsADRDeployRole \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

---

## 📋 Verification Checklist

After running the fix script, verify:

- [ ] Trust policy JSON file created correctly
- [ ] AWS CLI command executed successfully
- [ ] No error messages from `update-assume-role-policy`
- [ ] IAM role still exists
- [ ] Trust policy contains your GitHub org: `anoopmc1981`
- [ ] Trust policy contains your repo: `AI-Project-ADR`
- [ ] GitHub secret `AWS_IAM_ROLE_ARN` is set correctly
- [ ] Ready to re-run the workflow

---

## 📊 Expected vs Actual

### Expected (What Should Happen)
```
Configure AWS Credentials ✅
├─ Assuming role with OIDC ✅
├─ Role found ✅
├─ Credentials obtained ✅
└─ Ready to deploy ✅
```

### Actual (What Happened)
```
Configure AWS Credentials ❌
├─ Attempting OIDC assumption ❌
├─ Error: Not authorized to perform sts:AssumeRoleWithWebIdentity ❌
└─ Build stopped ❌
```

**Root Cause**: Trust policy didn't allow GitHub to assume the role

**After Fix**: Trust policy will be correct, OIDC will work! ✅

---

## 🎯 Why This Happened

Likely causes:

1. **Trust policy created with wrong account ID** - Most common
2. **Wrong GitHub organization/username** - Second most common  
3. **OIDC provider not configured** - Less common
4. **Role doesn't have permissions** - Rare, but possible

The fix script handles all of these automatically.

---

## 📞 Still Stuck?

If the fix script doesn't work, try these in order:

1. **Delete and recreate everything:**
   ```bash
   # Delete role (AWS IAM → Roles → GitHubActionsADRDeployRole → Delete)
   # Or via CLI:
   aws iam delete-role-policy --role-name GitHubActionsADRDeployRole --policy-name GitHubActionsADRDeployPolicy
   aws iam delete-role --role-name GitHubActionsADRDeployRole
   
   # Then run the fix script again
   ```

2. **Check AWS credentials are correct:**
   ```bash
   aws sts get-caller-identity
   # Should show your account, user, and ARN
   ```

3. **Verify GitHub repo path is correct:**
   - Expected: `anoopmc1981/AI-Project-ADR`
   - Check on GitHub: https://github.com/anoopmc1981/AI-Project-ADR
   - Should match exactly

4. **Run AWS CLI commands manually** to debug:
   ```bash
   # Check trust policy
   aws iam get-role --role-name GitHubActionsADRDeployRole \
       --query 'Role.AssumeRolePolicyDocument' \
       --output json | python -m json.tool
   ```

---

## ✨ What You Should See After Fix

### In GitHub Actions Log:
```
Run aws-actions/configure-aws-credentials@v4
  Assuming role with OIDC
  ✅ Credentials retrieved successfully

Run echo "🔐 Verifying AWS credentials..."
  🔐 Verifying AWS credentials...
  ✅ Success!
  
Build continues...
```

### Expected timeline after fix:
- Configure AWS: ✅ (was failing, now works)
- Build: ✅ 10-15 min
- Deploy: ✅ 10-15 min
- **Total**: 30-40 min

---

## 🚀 Final Steps

1. **Run the fix script:**
   ```
   PowerShell: .\QUICK_FIX_OIDC.ps1
   Bash: bash quick-fix-oidc.sh
   ```

2. **Check for success message:**
   ```
   ✅ OIDC TRUST POLICY FIX COMPLETE!
   ```

3. **Go to GitHub Actions and re-run the workflow**

4. **Watch it deploy successfully!** 🎉

---

**Your deployment will work once the trust policy is fixed. Run the script now!** 🚀
