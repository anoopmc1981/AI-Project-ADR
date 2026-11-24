# Quick Start Guide - Deploy Your Frontend

Your backend is deployed. Now let's get your React frontend running and deployed to S3.

## Prerequisites

You need Node.js installed. If you don't have it:
- Download from https://nodejs.org/
- Choose LTS version
- Install and restart your terminal

## Step 1: Install Dependencies (5 minutes)

```bash
cd d:\Project\Git-AI-Projects\AI-Project-ADR\frontend
npm install
```

This downloads and installs all required packages:
- React 18.2.0
- React Router 6.14.0
- Amazon Cognito Identity JS 6.2.0
- And ~50 other dependencies

**Expected output:** Ends with `added X packages` (usually 100-200 packages)

## Step 2: Test Locally (Optional - 2 minutes)

```bash
npm start
```

This:
- Starts dev server on http://localhost:3000
- Opens in your browser
- Shows Login page

**To test:**
1. Click "Don't have an account? Sign Up"
2. Enter: 
   - Name: Your name
   - Email: Your email (Cognito will send confirmation code)
   - Password: Abc123!@# (or any that meets: 8+ chars, uppercase, lowercase, number)
3. Submit → You'll see "Confirm Your Email" prompt
4. Check your email for confirmation code
5. Enter code → You're logged in! Dashboard appears with your name

**To stop:** Press Ctrl+C in terminal

## Step 3: Build for Production (3 minutes)

```bash
npm run build
```

This:
- Creates optimized build
- Minifies JavaScript and CSS
- Outputs to `frontend/build/` directory
- Much smaller and faster than dev version

**Expected output:** Ends with `Build complete!` and file sizes shown

## Step 4: Deploy to AWS S3 (1 minute)

```bash
aws s3 sync build/ s3://adr-frontend-471533886200/ --delete --region ap-south-1
```

This:
- Uploads all files from `build/` to S3 bucket
- Sets correct content types (HTML, JS, CSS)
- `--delete` removes old files no longer in build

**Expected output:** Shows each file being uploaded, ends with:
```
Completed X.X KiB/Y.Y MiB (Z files)
```

## Step 5: Access Your App 🎉

Your app is now live at:

```
http://adr-frontend-471533886200.s3-website.ap-south-1.amazonaws.com/
```

**What you can do:**
1. Create new account (signup)
2. Confirm email
3. Login
4. See dashboard with your name
5. Logout

## Common Issues

### "npm: command not found"
- Node.js not installed or not in PATH
- **Fix:** Restart terminal after installing Node.js, or install from https://nodejs.org/

### "node_modules not found"
- Didn't run `npm install`
- **Fix:** Run `npm install` first

### "build directory not found"
- Didn't run `npm run build`
- **Fix:** Run `npm run build` first

### "S3 upload failed - Access Denied"
- AWS credentials not configured
- **Fix:** Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set in environment

### "502 Bad Gateway" or "Cannot GET /"
- S3 website not configured yet
- **Fix:** GitHub Actions workflow updated template. Wait 2-3 minutes for deployment to complete

### Cognito email not received
- Need to verify sender email in AWS SES
- **For now:** Check AWS Cognito console for test email or use different email
- **Later:** Set up SES email verification

## Full Deployment Commands (All at Once)

If you want to run everything at once:

```bash
cd d:\Project\Git-AI-Projects\AI-Project-ADR\frontend
npm install
npm run build
aws s3 sync build/ s3://adr-frontend-471533886200/ --delete --region ap-south-1
```

Then visit the S3 website URL above.

## Verification

After deployment, verify by:

1. ✅ Visit S3 website URL in browser
2. ✅ See login page appears
3. ✅ Create account with email
4. ✅ Receive confirmation code
5. ✅ Login succeeds
6. ✅ Dashboard shows your name
7. ✅ Logout button works

## What's Happening Behind the Scenes

1. **npm install** - Downloads dependencies from npm registry
2. **npm run build** - React build script:
   - Compiles JSX to JavaScript
   - Minifies code
   - Creates optimized assets
3. **aws s3 sync** - Uploads build to S3 bucket
4. **S3 Website Hosting** - Serves files as static website
5. **Cognito** - Handles user authentication
6. **Browser** - Stores tokens in IndexedDB for session persistence

## Next Steps After Deployment

1. Test all features (signup, login, logout)
2. Check AWS CloudWatch logs if issues occur
3. Connect frontend to backend Lambda functions
4. Add dashboard data loading
5. Test WhatsApp alerts when implemented

## Support

If you get stuck, common things to check:
- Is Node.js installed? (`node --version`)
- Did `npm install` complete without errors?
- Did `npm run build` create `frontend/build/` directory?
- Is AWS CLI configured? (`aws --version`)
- Can you access S3 bucket in AWS console?

Good luck! Let me know when you deploy and if you hit any issues.
