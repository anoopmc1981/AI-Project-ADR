# Verify Your Trust Policy - Still Getting OIDC Error

## Error You're Still Getting:
```
Error: Could not assume role with OIDC: Not authorized to perform sts:AssumeRoleWithWebIdentity
```

This means your trust policy **still has the wrong format**.

---

## 🔍 **IMPORTANT - Check Your Current Trust Policy**

Go to AWS Console **RIGHT NOW**:

1. https://console.aws.amazon.com/iam/
2. Click **Roles** → Search: `GitHubActionsADRDeployRole`
3. Click the role
4. Click **Trust relationships** tab
5. **Copy the ENTIRE trust policy JSON** and paste it here

**What does it currently show?**

---

## ⚠️ **Most Likely Problems:**

Based on the error repeating, I suspect one of these:

### Problem 1: Array Format (What You Showed Earlier)
```json
"token.actions.githubusercontent.com:sub": [
    "repo:anoopmc1981/*",
    "repo:anoopmc1981/*"
]
```

**This is WRONG.** Should be:
```json
"token.actions.githubusercontent.com:sub": "repo:anoopmc1981/AI-Project-ADR:*"
```

---

### Problem 2: Wrong Repository Pattern
```json
"repo:anoopmc1981/*"  ❌ WRONG
```

Should be:
```json
"repo:anoopmc1981/AI-Project-ADR:*"  ✅ CORRECT
```

---

### Problem 3: Missing the StringLike Condition Entirely
If you only see:
```json
"Condition": {
    "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
    }
}
```

You're **missing the StringLike condition**. You need BOTH.

---

## ✅ **CORRECT Trust Policy (Copy This Exactly):**

Replace `YOUR_ACCOUNT_ID` with your account ID (`471533886200`):

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

---

## 🔧 **To Fix:**

1. Go to AWS IAM → Roles → GitHubActionsADRDeployRole
2. Click **Trust relationships** tab
3. Click **[Edit trust policy]**
4. **Delete everything**
5. **Paste the CORRECT policy above** (with your account ID)
6. Click **[Update policy]**

---

## ✅ **After Update - What to Verify:**

The trust policy should have:
- [ ] Effect: `"Allow"`
- [ ] Principal Federated: `arn:aws:iam::471533886200:oidc-provider/token.actions.githubusercontent.com`
- [ ] Action: `"sts:AssumeRoleWithWebIdentity"`
- [ ] **StringEquals** condition with `aud: sts.amazonaws.com`
- [ ] **StringLike** condition with `sub: repo:anoopmc1981/AI-Project-ADR:*`
- [ ] NO array brackets `[]` - should be a simple string

---

## 🧪 **After You Update:**

1. Go to GitHub Actions
2. Find the last failed run
3. Click **[Re-run jobs]** → **[Re-run all jobs]**
4. Watch for: `STS assumed role successfully` ✅

---

## 🆘 **Can You Tell Me:**

1. What does your trust policy currently show in AWS Console?
2. Does it have the array format `[]` or single string?
3. Does it have TWO condition blocks or just one?

This will help me see exactly what's wrong! 🔍

