# Final Diagnostic - OIDC Error Persists

## Error Summary:
```
Error: Could not assume role with OIDC: Not authorized to perform sts:AssumeRoleWithWebIdentity
```

This error means AWS is **rejecting the OIDC token from GitHub**.

---

## 🔧 **What This Error Actually Means:**

GitHub is sending an OIDC token, but AWS is saying:
- ❌ "I don't trust this token"
- ❌ "The conditions don't match"
- ❌ "You're not authorized"

---

## 📋 **I Need You to Verify These Exact Things in AWS Console:**

### Check 1: Does the Role Exist?

```bash
AWS Console → IAM → Roles → Search: GitHubActionsADRDeployRole
```

**What should you see?**
- ✅ Role name: `GitHubActionsADRDeployRole`
- ✅ ARN: `arn:aws:iam::471533886200:role/GitHubActionsADRDeployRole`

**Can you see it?** YES / NO

---

### Check 2: Does the Role Have Permissions?

```bash
AWS Console → Roles → GitHubActionsADRDeployRole → Permissions tab
```

**What should you see?**
- ✅ At least ONE policy listed
- ✅ Ideally: `AdministratorAccess` (AWS managed policy)

**Can you see ANY policy?** YES / NO

**If YES, what's the policy name?**
```
Policy name: ___________________
```

---

### Check 3: Is the Identity Provider Registered?

```bash
AWS Console → IAM → Identity providers
```

**What should you see?**
- ✅ Provider name: `token.actions.githubusercontent.com`
- ✅ Type: `OpenID Connect`

**Do you see it?** YES / NO

**If YES, click on it and verify:**
- Provider URL: `https://token.actions.githubusercontent.com` ✅
- Audience: `sts.amazonaws.com` ✅
- Thumbprint: (populated with a value) ✅

---

### Check 4: Is the Workflow Permission Correct?

```bash
GitHub → Repository → .github/workflows/deploy.yml
```

**Find this section at the TOP of the file:**

```yaml
permissions:
  id-token: write
  contents: read
  issues: write
```

**Do you see `id-token: write`?** YES / NO

---

## 🆘 **My Diagnosis Based on Error Repeating:**

Since the error **keeps repeating even after hardcoding the ARN**, the issue is NOT the GitHub secret or workflow role-to-assume line.

The issue is **definitely one of these AWS components:**

1. **Most Likely:** AdministratorAccess policy is **NOT attached** to the role
2. **Also Possible:** Identity provider is **missing**
3. **Less Likely:** Workflow missing `id-token: write` permission

---

## ✅ **Immediate Fix - Try This:**

### Step 1: Add AdministratorAccess Policy

Go to AWS Console:

1. IAM → Roles → GitHubActionsADRDeployRole
2. Click **Permissions** tab
3. Click **[Add permissions]** → **[Attach policies]**
4. Search box: type `AdministratorAccess`
5. Find the policy: **AdministratorAccess** (AWS managed)
6. Click the **checkbox** to select it
7. Click **[Attach policies]** button

**Verify:** You should see `AdministratorAccess` now listed in Permissions tab

### Step 2: Wait 2 Minutes

Let AWS propagate the change.

### Step 3: Re-run Workflow

GitHub Actions → Click last failed run → [Re-run jobs] → [Re-run all jobs]

### Step 4: Check Logs

Watch for:
- ✅ Success: `STS assumed role successfully`
- ❌ Failure: Same error again

---

## 🚨 **If Still Failing After Adding Policy:**

Then the issue is the **Identity Provider** is missing.

Go to AWS Console:

1. IAM → **Identity providers**
2. Do you see `token.actions.githubusercontent.com`?

**If NO:**
- Click **[Add provider]**
- Provider type: `OpenID Connect`
- Provider URL: `https://token.actions.githubusercontent.com`
- Click **[Get thumbprint]** (wait for it to populate)
- Audience: `sts.amazonaws.com`
- Click **[Add provider]**

**Then wait 2 minutes and re-run workflow**

---

## 📝 **Please Answer These Questions:**

1. **AdministratorAccess policy attached?** YES / NO
2. **If NO, can you attach it now?**
3. **Identity provider exists?** YES / NO
4. **If NO, can you create it now?**
5. **Workflow has `id-token: write`?** YES / NO

Once you answer these, I'll know exactly what to fix! 🔍

