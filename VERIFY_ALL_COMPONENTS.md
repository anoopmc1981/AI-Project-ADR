# Complete OIDC Verification - All Components

Since your trust policy is correct but OIDC still fails, let's verify every component systematically.

---

## ✅ **Component 1: Check AdministratorAccess Policy**

### In AWS Console:

1. Go to: https://console.aws.amazon.com/iam/
2. Click **Roles** → **GitHubActionsADRDeployRole**
3. Click **Permissions** tab

**What you should see:**
```
Permissions
├─ AdministratorAccess (AWS managed policy)
   └─ Status: Attached ✅
```

**If you see "No permissions attached":**
- Click **[Add permissions]** → **[Attach policies]**
- Search box: type `AdministratorAccess`
- Look for: **AdministratorAccess** (Full access to AWS services)
- Click the checkbox
- Click **[Attach policies]**

---

## ✅ **Component 2: Check Identity Provider Exists**

### In AWS Console:

1. Go to: https://console.aws.amazon.com/iam/
2. Click **Identity providers** (left sidebar)

**What you should see:**
```
Identity Providers

Provider name: token.actions.githubusercontent.com
Type: OpenID Connect
ARN: arn:aws:iam::471533886200:oidc-provider/token.actions.githubusercontent.com
```

**If NOT listed:**
- Click **[Add provider]**
- Provider type: **OpenID Connect**
- Provider URL: `https://token.actions.githubusercontent.com`
- Click **[Get thumbprint]** (wait for it to populate)
- Audience: `sts.amazonaws.com`
- Click **[Add provider]**

---

## ✅ **Component 3: Verify GitHub Secret**

### In GitHub:

1. Go to: https://github.com/anoopmc1981/AI-Project-ADR/settings/secrets/actions
2. Click **AWS_IAM_ROLE** secret
3. Click **[Edit secret]**

**What you should see in the text field:**
```
arn:aws:iam::471533886200:role/GitHubActionsADRDeployRole
```

**Check:**
- ✅ Starts with `arn:aws:iam::`
- ✅ Has your account ID: `471533886200`
- ✅ Has role name: `GitHubActionsADRDeployRole`
- ✅ No extra spaces before or after
- ✅ No quotes or special characters

**If wrong:**
- Delete the secret
- Click **[New repository secret]**
- Name: `AWS_IAM_ROLE`
- Value: `arn:aws:iam::471533886200:role/GitHubActionsADRDeployRole`
- Click **[Add secret]**

---

## ✅ **Component 4: Check Workflow Permissions**

### In GitHub:

1. Go to: https://github.com/anoopmc1981/AI-Project-ADR/blob/main/.github/workflows/deploy.yml
2. Look at the first 20 lines
3. Find the `permissions:` section

**What you should see:**
```yaml
permissions:
  id-token: write     # ← THIS IS CRITICAL
  contents: read
  issues: write
```

**Check:**
- ✅ `id-token: write` is present
- ✅ `contents: read` is present

**If missing `id-token: write`:**
- Click **[Edit this file]** (pencil icon)
- Add or verify the permissions section has `id-token: write`
- Click **[Commit changes]**

---

## ✅ **Component 5: Check Workflow Role Configuration**

### In GitHub:

1. Same file: `.github/workflows/deploy.yml`
2. Look for the step: **"Configure AWS Credentials"**

**What you should see:**
```yaml
- name: Configure AWS Credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_IAM_ROLE }}
    aws-region: ap-south-1
    role-session-name: GitHubActionsADRDeployment
```

**Check:**
- ✅ Uses: `aws-actions/configure-aws-credentials@v4`
- ✅ role-to-assume: `${{ secrets.AWS_IAM_ROLE }}` (matches your secret name)
- ✅ aws-region: `ap-south-1`

---

## 🧪 **Quick Verification via AWS CLI**

If you want to verify from command line (optional):

```bash
# Check if identity provider exists
aws iam get-open-id-connect-provider \
  --open-id-connect-provider-arn "arn:aws:iam::471533886200:oidc-provider/token.actions.githubusercontent.com"

# Check if role exists
aws iam get-role --role-name GitHubActionsADRDeployRole

# Check role trust policy
aws iam get-role --role-name GitHubActionsADRDeployRole \
  --query 'Role.AssumeRolePolicyDocument'

# Check attached policies
aws iam list-attached-role-policies --role-name GitHubActionsADRDeployRole
```

**Expected output for last command:**
```
AttachedPolicies:
- PolicyName: AdministratorAccess
  PolicyArn: arn:aws:iam::aws:policy/AdministratorAccess
```

---

## 📋 **Full Verification Checklist**

Go through each and mark ✅ or ❌:

### AWS IAM Role
- [ ] Role name: `GitHubActionsADRDeployRole` exists
- [ ] Trust policy: Shows correct JSON (you verified ✅)
- [ ] Permissions: `AdministratorAccess` policy attached
- [ ] ARN: `arn:aws:iam::471533886200:role/GitHubActionsADRDeployRole`

### AWS Identity Provider
- [ ] Provider: `token.actions.githubusercontent.com` exists
- [ ] Type: OpenID Connect
- [ ] Audience: `sts.amazonaws.com`
- [ ] Thumbprint: Populated

### GitHub Secrets
- [ ] Secret name: `AWS_IAM_ROLE` exists
- [ ] Secret value: `arn:aws:iam::471533886200:role/GitHubActionsADRDeployRole`
- [ ] No extra spaces or quotes
- [ ] Recently updated (within last hour)

### GitHub Workflow
- [ ] Permissions section has: `id-token: write`
- [ ] Permissions section has: `contents: read`
- [ ] "Configure AWS Credentials" step present
- [ ] Uses: `aws-actions/configure-aws-credentials@v4`
- [ ] role-to-assume: `${{ secrets.AWS_IAM_ROLE }}`
- [ ] aws-region: `ap-south-1`

### GitHub Repository
- [ ] Repository is public (required for OIDC without GitHub Enterprise)
- [ ] Actions are enabled
- [ ] Workflow file is on `main` branch

---

## 🔧 **If Everything Above is Correct But Still Failing**

The issue might be AWS-side. Try this:

### Option 1: Recreate the Role

```bash
# Delete old role
aws iam delete-role --role-name GitHubActionsADRDeployRole 2>/dev/null || true

# Wait 5 seconds
sleep 5

# Create new role with this trust policy (save as trust-policy.json):
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::471533886200:oidc-provider/token.actions.githubusercontent.com"
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

# Create role
aws iam create-role \
  --role-name GitHubActionsADRDeployRole \
  --assume-role-policy-document file://trust-policy.json

# Attach policy
aws iam attach-role-policy \
  --role-name GitHubActionsADRDeployRole \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

### Option 2: Wait and Retry

AWS sometimes takes a few minutes to propagate changes:
1. Wait 5 minutes
2. Go to GitHub Actions
3. Click **[Re-run jobs]** → **[Re-run all jobs]**

---

## 📞 **Next Steps**

Can you tell me which of these are TRUE or FALSE:

1. **AdministratorAccess policy is attached** to GitHubActionsADRDeployRole? (TRUE/FALSE)
2. **Identity provider** `token.actions.githubusercontent.com` **exists**? (TRUE/FALSE)
3. **GitHub secret** `AWS_IAM_ROLE` **has the correct ARN value**? (TRUE/FALSE)
4. **Workflow has** `id-token: write` **permission**? (TRUE/FALSE)

This will help me know exactly what needs fixing! 🔍

