# Git Bash - AWS CLI Setup & OIDC Fix Guide

## ✅ Good News!

Git Bash **will work perfectly** for running the OIDC fix script. It's a Unix-like environment that runs Bash scripts natively on Windows.

---

## 1️⃣ Check if AWS CLI is Already Installed

Open Git Bash and run:

```bash
aws --version
```

**If you see output like:**
```
aws-cli/2.13.0 Python/3.11.0 Windows/10.0.19045
```

✅ **AWS CLI is installed!** Skip to Step 2

**If you see:**
```
command not found: aws
```

❌ **AWS CLI is NOT installed.** See Step 1b below

---

## 1b: Install AWS CLI (If Needed)

### Option A: Using chocolatey (Easiest)

If you have chocolatey installed:

```bash
choco install awscli
```

Then close and reopen Git Bash.

### Option B: Download & Install Manually

1. Go to: https://aws.amazon.com/cli/
2. Click "Download for Windows"
3. Download the MSI installer
4. Run the installer
5. Close and reopen Git Bash

### Option C: Using Python pip

If you have Python installed:

```bash
pip install awscliv2
```

### Verify Installation

```bash
aws --version
```

Should show version info.

---

## 2️⃣ Configure AWS Credentials in Git Bash

```bash
aws configure
```

You'll be prompted for:
```
AWS Access Key ID: [your-access-key]
AWS Secret Access Key: [your-secret-key]
Default region name: ap-south-1
Default output format: json
```

**Get these from:**
- AWS Console → IAM → Users → Security credentials
- Or use the credentials you already have configured

### Verify Configuration

```bash
aws sts get-caller-identity
```

Should show your AWS account info:
```json
{
    "UserId": "AIDACKCEVSQ6C2EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:root"
}
```

---

## 3️⃣ Run the OIDC Fix Script in Git Bash

Navigate to your project:

```bash
cd D:/Project/Git-AI-Projects/AI-Project-ADR
```

**Note**: In Git Bash, use forward slashes (/) not backslashes (\)

Run the fix script:

```bash
bash quick-fix-oidc.sh
```

**Expected output:**

```
🔧 ADR Scanner - OIDC Trust Policy Quick Fix
============================================

Step 1: Getting AWS Account ID...
✅ Account ID: 123456789012

Step 2: Creating trust policy JSON...
✅ Trust policy created

Step 3: Verifying IAM role exists...
✅ Role found: arn:aws:iam::123456789012:role/GitHubActionsADRDeployRole

Step 4: Updating trust policy...
✅ Trust policy updated successfully!

Step 5: Verifying permissions...
✅ Administrator policy attached

Step 6: Getting role ARN for GitHub secret...
✅ Role ARN: arn:aws:iam::123456789012:role/GitHubActionsADRDeployRole

============================================
✅ OIDC TRUST POLICY FIX COMPLETE!
============================================

Next Steps:
1. Go to GitHub Actions: https://github.com/anoopmc1981/AI-Project-ADR/actions
2. Find the failed workflow run
3. Click 'Re-run failed jobs'
4. Watch the deployment progress

The deployment should now succeed! 🚀
```

---

## ✅ Troubleshooting in Git Bash

### Issue 1: "command not found: aws"

```bash
# Check if AWS CLI is in PATH
which aws

# If nothing shows, AWS CLI is not installed
# Install it following Step 1b above
```

### Issue 2: "command not found: python"

```bash
# Git Bash might not have Python in PATH
# Check if Python is installed on your system
python --version

# If not found, install Python from python.org
```

### Issue 3: Permission Denied on Script

```bash
# Make script executable
chmod +x quick-fix-oidc.sh

# Then run it
bash quick-fix-oidc.sh
```

### Issue 4: Script Hangs or Takes Too Long

```bash
# Press Ctrl+C to stop
# Check AWS credentials are configured
aws sts get-caller-identity

# Then run script again
bash quick-fix-oidc.sh
```

---

## 🎯 Complete Step-by-Step for Git Bash

### Step 1: Open Git Bash
Right-click anywhere → "Git Bash Here"

Or search for "Git Bash" in Start Menu

### Step 2: Navigate to Project
```bash
cd D:/Project/Git-AI-Projects/AI-Project-ADR
```

**Note**: Use forward slashes (/) in Git Bash

### Step 3: Check AWS CLI
```bash
aws --version
```

If not installed, install it (see Step 1b above)

### Step 4: Configure AWS
```bash
aws configure
```

Enter your AWS credentials

### Step 5: Verify AWS Access
```bash
aws sts get-caller-identity
```

Should show your account info

### Step 6: Run Fix Script
```bash
bash quick-fix-oidc.sh
```

Watch for ✅ success messages

### Step 7: Go to GitHub & Re-run Workflow
1. Open: https://github.com/anoopmc1981/AI-Project-ADR/actions
2. Find failed run
3. Click "Re-run failed jobs"
4. Wait 30-40 minutes for deployment

---

## 💡 Git Bash Tips

### Path Formatting
- **Windows**: `C:\Users\YourName\Desktop`
- **Git Bash**: `C:/Users/YourName/Desktop` or `/c/Users/YourName/Desktop`

### Common Commands
```bash
# Navigate to home directory
cd ~

# List files
ls -la

# Show current directory
pwd

# Go to Windows drive
cd /c/Users/YourName/

# Edit files
nano filename.txt    # Simple editor
vim filename.txt     # Advanced editor
```

### View Files
```bash
# View JSON file
cat trust-policy.json

# View with pretty formatting
cat trust-policy.json | python -m json.tool
```

---

## ✨ What the Script Does in Git Bash

The `quick-fix-oidc.sh` script:

1. ✅ Gets your AWS Account ID using `aws sts get-caller-identity`
2. ✅ Creates `trust-policy.json` with correct configuration
3. ✅ Verifies your IAM role exists
4. ✅ Updates the trust policy using `aws iam update-assume-role-policy`
5. ✅ Checks permissions are attached
6. ✅ Verifies the fix worked
7. ✅ Shows you next steps

**All these AWS CLI commands work perfectly in Git Bash!**

---

## ⚠️ Alternative: Use PowerShell Instead

If you have issues with Git Bash, you can use PowerShell instead:

```powershell
# Open PowerShell as Administrator
# Navigate to project
cd D:\Project\Git-AI-Projects\AI-Project-ADR

# Run PowerShell script
.\QUICK_FIX_OIDC.ps1
```

Both scripts do the same thing - choose whichever you're comfortable with.

---

## 🚀 Quick Reference for Git Bash

| Task | Command |
|------|---------|
| Open Git Bash | Search "Git Bash" or right-click → Git Bash Here |
| Navigate project | `cd D:/Project/Git-AI-Projects/AI-Project-ADR` |
| Check AWS CLI | `aws --version` |
| Configure AWS | `aws configure` |
| Test AWS access | `aws sts get-caller-identity` |
| Run fix script | `bash quick-fix-oidc.sh` |
| View JSON file | `cat trust-policy.json` |
| Check if script exists | `ls -la quick-fix-oidc.sh` |
| Make script executable | `chmod +x quick-fix-oidc.sh` |

---

## ✅ You're Ready!

1. **Open Git Bash**
2. **Navigate to project**: `cd D:/Project/Git-AI-Projects/AI-Project-ADR`
3. **Install AWS CLI** (if needed)
4. **Configure AWS**: `aws configure`
5. **Run fix**: `bash quick-fix-oidc.sh`
6. **Re-run workflow** in GitHub Actions

**Your deployment will succeed! 🚀**

---

## 📞 Still Need Help?

### Common Issues in Git Bash

**"command not found: aws"**
- AWS CLI not installed or not in PATH
- Solution: Install AWS CLI following Step 1b

**"Permission denied"**
- Script not executable
- Solution: `chmod +x quick-fix-oidc.sh`

**"aws configure" won't save credentials**
- Run `aws configure` again, it should work
- Or check: `cat ~/.aws/credentials`

**Script doesn't complete**
- Check AWS CLI is working: `aws sts get-caller-identity`
- Check JSON is valid: `cat trust-policy.json | python -m json.tool`

**"python: command not found"**
- Python not in Git Bash PATH
- Solution: Use `python` command if installed, or skip JSON validation step

---

**Git Bash will work perfectly for running the OIDC fix script! Just make sure AWS CLI is installed and configured.** ✅
