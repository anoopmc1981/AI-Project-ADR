# Frontend Setup Guide

Your React frontend is now configured with Cognito authentication. Here's what's been set up and what you need to do next.

## What's Already Done

✅ **Cognito Configuration Files Created:**
- `frontend/.env` - Contains your Cognito credentials
  - Region: `ap-south-1`
  - User Pool ID: `ap-south-1_RYAH5LzcK`
  - Client ID: `2osdell6nkret9qmqjie6gd6un`

✅ **Authentication Service Created:**
- `frontend/src/services/authService.js` - Handles all Cognito operations (login, signup, logout, token refresh)

✅ **Frontend Components Created:**
- `frontend/src/components/Login.js` - Full login/signup UI
- `frontend/src/components/ProtectedRoute.js` - Route protection wrapper
- `frontend/src/App.js` - Main app with routing
- `frontend/src/App.css` - Dashboard styling
- `frontend/src/styles/Login.css` - Login page styling

✅ **React Configuration:**
- `frontend/package.json` - All dependencies listed
- `frontend/public/index.html` - HTML template
- `frontend/src/index.js` - React entry point
- `frontend/src/index.css` - Global styles

## Next Steps

### 1. Install Dependencies
```bash
cd frontend
npm install
```

This will install:
- React 18.2.0
- React Router 6.14.0
- Amazon Cognito Identity JS 6.2.0
- And other required packages

### 2. Test Locally (Optional)
```bash
npm start
```
This runs on `http://localhost:3000`. You can test signup and login with your Cognito user pool.

### 3. Build for Deployment
```bash
npm run build
```
This creates an optimized build in the `frontend/build/` directory.

### 4. Deploy to S3
```bash
aws s3 sync build/ s3://adr-frontend-471533886200/ --delete --region ap-south-1
```

This uploads your built frontend to S3 for hosting.

### 5. Access Your App
Once deployed, you can access your app via:
- **S3 Static Website Endpoint:** `http://adr-frontend-471533886200.s3-website.ap-south-1.amazonaws.com/`
- **CloudFront (when re-enabled):** Your CloudFront domain

## How It Works

### Authentication Flow
1. User lands on `/login` page
2. Can choose to Login or Sign Up
3. For signup:
   - Enter email, password, and name
   - Cognito sends confirmation code via email
   - User enters code to confirm account
   - User is logged in
4. For login:
   - User enters email and password
   - Tokens stored in browser's IndexedDB
5. Protected routes require valid session
6. Logout clears tokens and redirects to login

### Key Files Reference

| File | Purpose |
|------|---------|
| `frontend/.env` | Cognito credentials (DO NOT commit) |
| `frontend/src/services/authService.js` | All Cognito API calls |
| `frontend/src/components/Login.js` | Signup and Login UI |
| `frontend/src/App.js` | Routing and main layout |
| `frontend/package.json` | Dependencies |

## Troubleshooting

### "Cannot find module 'amazon-cognito-identity-js'"
Make sure you ran `npm install` first.

### "CORS error when calling Lambda"
You may need to add CORS headers to your Lambda functions. Add this to the Lambda responses:
```python
"headers": {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
}
```

### User not persisting after refresh
Cognito automatically stores tokens in IndexedDB. The auth check on app load reads from there. If this fails, check browser DevTools → Application tab → IndexedDB.

### "Cognito User Pool not found"
Verify your `.env` file has the correct credentials:
```
REACT_APP_COGNITO_REGION=ap-south-1
REACT_APP_COGNITO_USER_POOL_ID=ap-south-1_RYAH5LzcK
REACT_APP_COGNITO_CLIENT_ID=2osdell6nkret9qmqjie6gd6un
```

## Next Phase: Backend Integration

Once frontend is deployed, you can:
1. Update `REACT_APP_API_ENDPOINT` in `.env` to your API Gateway URL
2. Add API calls to your Lambda functions from the Dashboard component
3. Display ADR crossings, settings, and historical data

## Security Notes

- `.env` file contains credentials - never commit to Git (`.gitignore` already excludes it)
- Tokens are stored in IndexedDB by amazon-cognito-identity-js library
- Always use HTTPS in production
- Implement token refresh before expiry (optional - library handles basic refresh)
- Never hardcode API keys in frontend code

That's it! Your frontend is ready. Start with `npm install` and let me know if you hit any issues.
