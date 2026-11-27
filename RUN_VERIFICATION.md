# How to Run the OIDC Verification Script

## 📋 Prerequisites

Make sure you have:
- ✅ Git Bash installed
- ✅ AWS CLI configured with credentials
- ✅ You can run `aws sts get-caller-identity` successfully

---

## 🚀 Steps to Run

### Step 1: Open Git Bash

1. Navigate to your project directory:
   ```bash
   cd /d/Project/Git-AI-Projects/AI-Project-ADR
   ```

### Step 2: Make Script Executable

```bash
chmod +x verify-oidc-setup.sh
```

### Step 3: Run the Verification Script

```bash
./verify-oidc-setup.sh
```

### Step 4: Wait for Results

The script will check:
- ✅ AWS CLI availability
- ✅ AWS credentials
- ✅ IAM role exists
- ✅ Trust policy correct
- ✅ Policies attached
- ✅ Identity provider exists
- ✅ Workflow file correct

---

## 📤 What to Do With the Output

After running the script:

1. **Copy ALL the output** from the terminal
2. **Paste it here** in the chat
3. **I will analyze it** and tell you exactly what needs fixing

---

## ✅ Expected Output (If Everything is Correct)

You should see:
```
✅ AWS CLI is installed
✅ AWS Credentials are configured
✅ IAM Role exists
✅ Trust Policy references OIDC provider
✅ Trust Policy has StringEquals condition
✅ Trust Policy has StringLike condition
✅ Trust Policy has audience: sts.amazonaws.com
✅ Trust Policy references correct repository
✅ AdministratorAccess policy is attached
✅ Identity Provider exists
✅ Workflow file exists
✅ Workflow has 'id-token: write' permission
✅ Workflow uses aws-actions/configure-aws-credentials@v4
✅ Workflow has correct hardcoded role ARN

✅ ALL CHECKS PASSED - OIDC Setup is Correct!
```

---

## ❌ Expected Output (If Something is Wrong)

You might see:
```
❌ AdministratorAccess policy is NOT attached
❌ Identity Provider does NOT exist
❌ Workflow missing 'id-token: write' permission

❌ 3 Check(s) Failed - Fix issues above
```

---

## 🔧 If Script Fails to Run

### Error: "Permission Denied"
```bash
chmod +x verify-oidc-setup.sh
./verify-oidc-setup.sh
```

### Error: "command not found: aws"
AWS CLI is not installed or not in PATH.
Check: `aws --version`

### Error: "Unable to locate credentials"
AWS credentials are not configured.
Run: `aws configure`

---

## 💡 Tips

1. **Copy the full output** - Don't skip any part
2. **Include timestamps** - Shows when you ran it
3. **Keep terminal open** - In case I need more details
4. **Paste as code block** - Makes it easier to read

---

## 🎯 Once You Have the Output

Just paste it in the chat and tell me:
- ✅ Script ran successfully?
- ✅ How many checks passed?
- ✅ How many checks failed?

I'll analyze it immediately! 🚀

