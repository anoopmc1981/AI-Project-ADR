# Immediate Action Plan - Fix OIDC Error

Your trust policy is correct, but OIDC is still failing. Follow this exact checklist.

---

## ✅ **Action 1: Check AdministratorAccess Policy (5 minutes)**

**Go to AWS Console:**

1. https://console.aws.amazon.com/iam/
2. Click **Roles** (left sidebar)
3. Search: `GitHubActionsADRDeployRole`
4. Click the role name
5. Click **Permissions** tab

**Question:** Do you see **AdministratorAccess** listed?

### If YES ✅
- Move to Action 2

### If NO ❌
- Click **[Add permissions]** → **[Attach policies]**
- Search: `AdministratorAccess`
- Check the checkbox
- Click **[Attach policies]**
- Wait 1 minute
- Move to Action 2

---

## ✅ **Action 2: Verify Identity Provider (5 minutes)**

**Go to AWS Console:**

1. https://console.aws.amazon.com/iam/
2. Click **Identity providers** (left sidebar)

**Question:** Do you see `token.actions.githubusercontent.com`?

### If YES ✅
- Click on it
- Verify details:
  - Type: OpenID Connect
  - Provider URL: `https://token.actions.githubusercontent.com`
  - Audience: `sts.amazonaws.com`
- If all correct, move to Action 3

### If NO ❌
- Click **[Add provider]**
- Provider type: **OpenID Connect**
- Provider URL: `https://token.actions.githubusercontent.com`
- Click **[Get thumbprint]** (wait for it)
- Audience: `sts.amazonaws.com`
- Click **[Add provider]**
- Wait 1 minute
- Move to Action 3

---

## ✅ **Action 3: Verify GitHub Secret (3 minutes)**

**Go to GitHub:**

1. https://github.com/anoopmc1981/AI-Project-ADR/settings/secrets/actions
2. Click **AWS_IAM_ROLE**
3. Click **[Edit secret]**

**Question:** What value is shown in the text field?

### If it shows: `arn:aws:iam::471533886200:role/GitHubActionsADRDeployRole` ✅
- Perfect! Move to Action 4

### If it's blank or different ❌
- **Delete this secret:**
  - Click **[Edit secret]** again
  - Click **[Delete secret]** at bottom
  - Confirm deletion

- **Create new secret:**
  - Click **[New repository secret]**
  - Name: `AWS_IAM_ROLE`
  - Value: `arn:aws:iam::471533886200:role/GitHubActionsADRDeployRole`
  - Click **[Add secret]**
  - Move to Action 4

---

## ✅ **Action 4: Check Workflow Permissions (3 minutes)**

**Go to GitHub:**

1. https://github.com/anoopmc1981/AI-Project-ADR/blob/main/.github/workflows/deploy.yml
2. Look at the first 20 lines
3. Find `permissions:` section

**Question:** Do you see `id-token: write`?

### If YES ✅
- Perfect! Move to Action 5

### If NO or MISSING ❌
- Click the **pencil icon** (Edit button)
- Find `permissions:` section
- Add or verify:
  ```yaml
  permissions:
    id-token: write
    contents: read
    issues: write
  ```
- Click **[Commit changes]**
- Move to Action 5

---

## ✅ **Action 5: Wait for Propagation (2 minutes)**

**Wait 2-3 minutes** for all changes to propagate through AWS and GitHub.

---

## ✅ **Action 6: Test the Deployment (1 minute)**

**Go to GitHub Actions:**

1. https://github.com/anoopmc1981/AI-Project-ADR/actions
2. Find the **last failed workflow run** (shows red ❌)
3. Click on it to open
4. Click **[Re-run jobs]** button (top right)
5. Click **[Re-run all jobs]**
6. Watch the logs

---

## 🔍 **What to Look For:**

### Success ✅
```
✅ Configure AWS Credentials - PASSED
   Getting AWS Credentials for GitHub Actions
   STS assumed role successfully
   arn:aws:iam::471533886200:role/GitHubActionsADRDeployRole
```

### Failure ❌
```
❌ Configure AWS Credentials - FAILED
   Error: Could not assume role with OIDC
   Not authorized to perform sts:AssumeRoleWithWebIdentity
```

---

## 📋 **Summary Checklist**

Go through each action above and mark when complete:

- [ ] **Action 1:** AdministratorAccess policy attached
- [ ] **Action 2:** Identity provider exists and verified
- [ ] **Action 3:** GitHub secret has correct ARN
- [ ] **Action 4:** Workflow has `id-token: write` permission
- [ ] **Action 5:** Waited 2-3 minutes
- [ ] **Action 6:** Re-ran workflow

---

## 🚀 **If Still Failing After All Steps**

Try the **AWS CLI recreation** (more aggressive):

Save this as `trust-policy.json`:
```json
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
```

Then run:
```bash
# Delete old role
aws iam delete-role --role-name GitHubActionsADRDeployRole

# Wait
sleep 5

# Create new role
aws iam create-role \
  --role-name GitHubActionsADRDeployRole \
  --assume-role-policy-document file://trust-policy.json

# Attach policy
aws iam attach-role-policy \
  --role-name GitHubActionsADRDeployRole \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Verify
aws iam get-role --role-name GitHubActionsADRDeployRole
```

Then re-run workflow.

---

## 📞 **Need Help?**

After you complete all 6 actions, let me know:

1. ✅ All 6 actions completed?
2. ❌ Did workflow still fail?
3. What error message did you see?

This will help me diagnose the exact issue! 🔍

