# ADR Level Breakout Stock Scanner

A complete serverless application for scanning Average Daily Range (ADR) level breakouts in NIFTY 50 stocks, with real-time alerts and historical analysis.

## 🚀 Quick Links

- **Frontend Deployment:** [QUICK_START.md](QUICK_START.md)
- **Architecture Overview:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Frontend Setup:** [FRONTEND_SETUP.md](FRONTEND_SETUP.md)
- **Deployment Checklist:** [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

## 📊 What This Does

The ADR Scanner:
1. **Fetches stock data** from Fyers API (NIFTY 50 stocks)
2. **Calculates ADR levels** (Average Daily Range breakout points)
3. **Detects crossings** when stock price crosses ADR levels
4. **Sends alerts** via WhatsApp and email
5. **Stores history** in DynamoDB for analysis
6. **Provides dashboard** with real-time updates

## 🏗️ Architecture

```
React Frontend (S3) → Cognito Auth → Lambda Functions → DynamoDB + S3
```

**Technology Stack:**
- Frontend: React 18, React Router, AWS Cognito SDK
- Backend: Python 3.11, AWS Lambda, AWS DynamoDB
- Infrastructure: CloudFormation (SAM), S3, Cognito
- CI/CD: GitHub Actions
- Deployment Region: ap-south-1 (Mumbai)

## ✅ What's Deployed

### Backend (Complete)
- ✅ 3 Lambda functions deployed
- ✅ 3 DynamoDB tables created
- ✅ Cognito User Pool configured
- ✅ S3 buckets for data storage
- ✅ GitHub Actions CI/CD pipeline
- ✅ CloudFormation infrastructure as code

### Frontend (Ready to Deploy)
- ✅ React application with authentication
- ✅ Login/Signup UI with email confirmation
- ✅ Protected routes and dashboard
- ✅ Cognito integration complete
- ✅ All dependencies configured
- ⏳ Needs: `npm install` and `npm run build`

## 🎯 Next Steps (Do This)

### 1. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 2. Build for Production
```bash
npm run build
```

### 3. Deploy to S3
```bash
aws s3 sync build/ s3://adr-frontend-471533886200/ --delete --region ap-south-1
```

### 4. Access Your App
```
http://adr-frontend-471533886200.s3-website.ap-south-1.amazonaws.com/
```

**See [QUICK_START.md](QUICK_START.md) for detailed instructions.**

## 📁 Project Structure

```
AI-Project-ADR/
├── frontend/                        # React SPA
│   ├── src/
│   │   ├── App.js                   # Main component
│   │   ├── components/              # Login, Dashboard, etc.
│   │   ├── services/                # Cognito integration
│   │   ├── config/                  # Configuration
│   │   └── styles/                  # Styling
│   ├── public/                      # Static files
│   ├── package.json                 # Dependencies
│   ├── .env                         # Environment variables
│   └── build/                       # Production build (created after npm run build)
│
├── backend/                         # Python Lambda functions
│   ├── functions/
│   │   ├── auth/                    # User authentication
│   │   ├── crossing_detection/      # ADR scanning
│   │   └── dashboard/               # Data retrieval
│   ├── requirements.txt             # Python dependencies
│   └── layer/                       # Optional shared dependencies
│
├── template.yaml                    # CloudFormation infrastructure
├── .github/workflows/               # GitHub Actions CI/CD
│   └── deploy.yml                   # Deployment workflow
│
├── QUICK_START.md                   # 👈 Start here for frontend deployment
├── ARCHITECTURE.md                  # System design and data flows
├── FRONTEND_SETUP.md                # Detailed frontend configuration
├── DEPLOYMENT_CHECKLIST.md          # Complete checklist
└── README.md                        # This file
```

## 🔐 Credentials & Configuration

### Your Cognito Setup
- **Region:** ap-south-1
- **User Pool ID:** ap-south-1_RYAH5LzcK
- **Client ID:** 2osdell6nkret9qmqjie6gd6un
- **Auth Flows:** USER_PASSWORD_AUTH, REFRESH_TOKEN_AUTH

### Your AWS Account
- **Account ID:** 471533886200
- **Region:** ap-south-1 (Mumbai)
- **Environment:** dev (development)

### Frontend Environment (.env)
```
REACT_APP_COGNITO_REGION=ap-south-1
REACT_APP_COGNITO_USER_POOL_ID=ap-south-1_RYAH5LzcK
REACT_APP_COGNITO_CLIENT_ID=2osdell6nkret9qmqjie6gd6un
REACT_APP_API_ENDPOINT=http://localhost:3001
```

## 🧪 Testing the App

After deployment to S3:

1. **Sign Up**
   - Go to: http://adr-frontend-471533886200.s3-website.ap-south-1.amazonaws.com/
   - Click "Don't have an account? Sign Up"
   - Enter name, email, password
   - Check email for confirmation code
   - Enter code to confirm

2. **Login**
   - Use credentials from signup
   - Should redirect to dashboard
   - See your name displayed

3. **Logout**
   - Click "Logout" button
   - Redirects to login page
   - Session cleared

4. **Session Persistence**
   - Login and refresh page
   - Should remain logged in
   - Logout and refresh page
   - Should redirect to login

## 📊 Deployed Resources

| Resource | Name | Status |
|----------|------|--------|
| Lambda | adr-scanner-login-dev | ✅ Active |
| Lambda | adr-scanner-crossing-dev | ✅ Active |
| Lambda | adr-scanner-dashboard-dev | ✅ Active |
| DynamoDB | adr-crossings-dev | ✅ Active |
| DynamoDB | adr-history-dev | ✅ Active |
| DynamoDB | adr-settings-dev | ✅ Active |
| Cognito | adr-scanner-pool-dev | ✅ Active |
| S3 | adr-frontend-471533886200 | ✅ Active |
| S3 | adr-ohlcv-471533886200 | ✅ Active |
| CloudFormation | adr-scanner-dev | ✅ Active |
| GitHub Actions | Deploy Workflow | ✅ Active |

## 🔄 CI/CD Pipeline

**Automatic deployment on Git push:**

```
Push to main
    ↓
GitHub Actions triggers
    ↓
Validate CloudFormation template
    ↓
Deploy infrastructure changes
    ↓
Test Lambda functions
    ↓
✅ Deployment complete (2-3 minutes)
```

**CI/CD Configuration:** `.github/workflows/deploy.yml`

## 📝 Features

### Current (Implemented)
- ✅ User signup with email verification
- ✅ User login/logout
- ✅ Session persistence
- ✅ Protected routes
- ✅ Dashboard with user info
- ✅ Responsive design
- ✅ Automatic deployments

### Coming Next (Phase 2)
- ⏳ API Gateway integration
- ⏳ Dashboard data loading
- ⏳ ADR crossing detection
- ⏳ WhatsApp alerts
- ⏳ Email notifications
- ⏳ Historical analysis

### Future (Phase 3)
- 🔮 Real-time streaming updates
- 🔮 Multiple user support
- 🔮 Custom ADR levels
- 🔮 Advanced charting
- 🔮 Mobile app

## 🔗 Useful Commands

**Frontend Development:**
```bash
cd frontend
npm install          # Install dependencies
npm start            # Run dev server (http://localhost:3000)
npm run build        # Build for production
npm test             # Run tests
```

**AWS Deployment:**
```bash
# Deploy frontend to S3
aws s3 sync build/ s3://adr-frontend-471533886200/ --delete --region ap-south-1

# Check CloudFormation status
aws cloudformation describe-stacks --stack-name adr-scanner-dev --region ap-south-1

# View Lambda logs
aws logs tail /aws/lambda/adr-scanner-login-dev --region ap-south-1 --follow

# Check Cognito users
aws cognito-idp list-users --user-pool-id ap-south-1_RYAH5LzcK --region ap-south-1
```

**Git/GitHub:**
```bash
git push origin main              # Push changes (triggers deployment)
git log --oneline -10             # View recent commits
gh pr create                       # Create pull request (GitHub CLI)
```

## 🐛 Troubleshooting

### "npm: command not found"
Install Node.js from https://nodejs.org/ and restart terminal.

### "Cannot access S3 website"
Wait 2-3 minutes for S3 website hosting configuration to complete. Check AWS S3 console.

### "Login fails with Cognito error"
- Verify `.env` has correct credentials
- Check browser console for error details
- Ensure email is verified in Cognito (may need to check email/spam)

### "Dependencies installation failed"
```bash
rm -rf node_modules
npm cache clean --force
npm install
```

### "Build failed"
Check for TypeScript/syntax errors:
```bash
npm run build 2>&1 | head -50
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [QUICK_START.md](QUICK_START.md) | Step-by-step deployment guide |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design and data flows |
| [FRONTEND_SETUP.md](FRONTEND_SETUP.md) | Frontend configuration details |
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Complete deployment status |

## 💡 Key Concepts

### Authentication Flow
1. User signs up with email/password
2. Cognito sends confirmation code via email
3. User confirms account
4. User logs in with credentials
5. Cognito issues JWT tokens
6. Frontend stores tokens in IndexedDB
7. Protected routes check token validity

### Data Storage
- **DynamoDB:** User settings, ADR crossings, scan history
- **S3:** OHLCV data, frontend build files
- **Cognito:** User credentials and sessions

### Infrastructure
- **CloudFormation:** Define infrastructure as code
- **GitHub Actions:** Automatic deployment on git push
- **Lambda:** Serverless compute for functions
- **S3:** Static file hosting and data storage

## 🌐 API Integration (Future)

Once API Gateway is added, frontend will call:
```
GET  /crossings              # Get ADR crossings
GET  /history/{date}         # Get scan history
POST /settings               # Save user preferences
GET  /settings               # Get user preferences
POST /alerts/whatsapp        # Configure WhatsApp alerts
```

## 📊 Estimated Costs (Monthly)

| Service | Estimated Cost |
|---------|---|
| Lambda | $0.20 |
| DynamoDB | $1.00 |
| S3 | $0.50 |
| Cognito | $0 (free tier) |
| **Total** | **~$2** |

## 🤝 Contributing

This is a personal project, but future contributions welcome. Standard Git workflow:
```bash
git checkout -b feature/new-feature
# Make changes
git commit -m "Add new feature"
git push origin feature/new-feature
# Create pull request on GitHub
```

## 📞 Support

For issues:
1. Check [QUICK_START.md](QUICK_START.md) troubleshooting section
2. Check AWS CloudWatch logs
3. Check browser console for errors
4. Verify AWS credentials are configured
5. Ensure all prerequisites are installed

## 🎓 Learning Resources

- [React Documentation](https://react.dev/)
- [AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [AWS Cognito](https://docs.aws.amazon.com/cognito/)
- [AWS CloudFormation](https://docs.aws.amazon.com/cloudformation/)
- [GitHub Actions](https://docs.github.com/en/actions)

## 📄 License

Personal project - all rights reserved.

---

## 🎯 Ready to Deploy?

Start with this command:
```bash
cd frontend && npm install && npm run build && aws s3 sync build/ s3://adr-frontend-471533886200/ --delete --region ap-south-1
```

Then visit: http://adr-frontend-471533886200.s3-website.ap-south-1.amazonaws.com/

**Questions?** Check the docs, check AWS console, check browser logs. Good luck! 🚀
