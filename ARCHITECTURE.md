# ADR Scanner - Complete Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        End User (Browser)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     S3 Website Hosting                           │
│         adr-frontend-471533886200.s3-website...                  │
│                   (React SPA - index.html)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │ Static Files
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│          Frontend Application (React + Cognito SDK)              │
│  - Login.js (Signup/Login/Confirm)                               │
│  - App.js (Routing & Dashboard)                                  │
│  - authService.js (Cognito Integration)                          │
│  - ProtectedRoute.js (Auth Guard)                                │
└────────────────────────────┬────────────────────────────────────┘
                             │ JWT Token
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              AWS Cognito User Pool                               │
│         ap-south-1_RYAH5LzcK (User Management)                   │
│  - Signup validation                                             │
│  - Email confirmation                                            │
│  - Token generation                                              │
│  - Session management                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │ Future: API Gateway
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              AWS Lambda Functions                                │
│  1. LoginFunction - User authentication (auth/)                  │
│  2. CrossingDetectionFunction - ADR scanning (crossing_detection/)
│  3. DashboardFunction - Data retrieval (dashboard/)              │
└────────────────────────────┬────────────────────────────────────┘
                             │ Read/Write
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              AWS DynamoDB Tables                                 │
│  - adr-crossings-dev (ADR crossing events)                       │
│  - adr-history-dev (Scan history)                                │
│  - adr-settings-dev (User preferences)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              AWS S3 Buckets                                      │
│  - adr-ohlcv-471533886200 (Price data)                           │
│  - adr-frontend-471533886200 (Frontend code)                     │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Frontend Layer (React)

```
frontend/
├── public/
│   └── index.html                 # HTML template
├── src/
│   ├── App.js                     # Main routing component
│   ├── App.css                    # Main styles
│   ├── index.js                   # React entry point
│   ├── index.css                  # Global styles
│   ├── components/
│   │   ├── Login.js               # Signup/Login/Confirm UI
│   │   └── ProtectedRoute.js      # Route protection wrapper
│   ├── services/
│   │   └── authService.js         # Cognito API integration
│   ├── config/
│   │   └── cognito.js             # Cognito configuration
│   └── styles/
│       └── Login.css              # Login page styling
├── .env                           # Environment variables (Cognito credentials)
├── .gitignore                     # Git exclusions
├── package.json                   # Dependencies
└── build/                         # Production build (created by npm run build)
```

### Backend Layer (Lambda + DynamoDB)

```
backend/
├── requirements.txt               # Python dependencies
├── functions/
│   ├── auth/
│   │   └── app.py                 # Authentication logic
│   ├── crossing_detection/
│   │   └── app.py                 # ADR scanning logic
│   └── dashboard/
│       └── app.py                 # Data retrieval
├── layer/                         # Optional: shared dependencies
└── tests/                         # Unit tests
```

## Data Flow

### 1. Authentication Flow

```
User              Frontend              Cognito
 │                   │                     │
 ├─ Sign Up ──────→  │                     │
 │                   ├─ SignUp ───────────→│
 │                   │                     ├─ Validate password
 │                   │                     ├─ Send confirmation email
 │                   │                     │
 │   ← Confirmation  │                     │
 │     Email         │                     │
 │                   │                     │
 ├─ Enter Code ────→ │                     │
 │                   ├─ ConfirmSignUp ────→│
 │                   │                     ├─ Verify code
 │                   │                     ├─ Activate account
 │                   │                     │
 ├─ Login ──────────→│                     │
 │                   ├─ Login ────────────→│
 │                   │                     ├─ Verify credentials
 │                   │                     ├─ Generate tokens
 │                   │                     │
 │                   │← Access Token ──────┤
 │                   │← ID Token ──────────┤
 │                   │← Refresh Token ─────┤
 │                   │
 │   ← Dashboard ────┤
```

### 2. Protected Route Access

```
User              Frontend              AuthService
 │                   │                     │
 ├─ Visit /dashboard │                     │
 │                   ├─ Check Auth ───────→│
 │                   │                     ├─ Read IndexedDB
 │                   │                     ├─ Verify session
 │                   │                     ├─ Check token expiry
 │                   │                     │
 │                   │← isAuthenticated ───┤
 │                   │
 │   ← Dashboard ────┤  (if true)
 │                   │
 │                   ├─ Logout ───────────→│
 │                   │                     ├─ Clear tokens
 │                   │
 │   ← Login Page ───┤  (if false)
```

### 3. Future API Flow (Phase 2)

```
Frontend              API Gateway           Lambda
  │                        │                  │
  ├─ GET /crossings ───→   │                  │
  │   (JWT header)         ├─ Validate JWT   │
  │                        ├─ Authorize ────→│
  │                        │                  │
  │                        │  ← Query Data ──┤─ DynamoDB
  │                        │                  │
  │   ← 200 Crossings ─────┤← Response ──────┤
  │
```

## AWS Account Setup

### Account Details
- **Account ID:** 471533886200
- **Region:** ap-south-1 (Mumbai)
- **Environment:** dev

### Resources by Service

**Cognito:**
- User Pool: `ap-south-1_RYAH5LzcK`
- Client ID: `2osdell6nkret9qmqjie6gd6un`
- Auth Flows: USER_PASSWORD_AUTH, REFRESH_TOKEN_AUTH
- Password: 8+ chars, uppercase, lowercase, numbers

**Lambda:**
- Function Runtime: Python 3.11
- Memory: 512 MB
- Timeout: 60 seconds
- Trigger: Manual (future: EventBridge for scheduled scans)

**DynamoDB:**
- Billing: PAY_PER_REQUEST (auto-scaling)
- Tables: 3 (crossings, history, settings)
- Partition Key: Determined per table
- Encryption: Default AWS managed

**S3:**
- Frontend Bucket: `adr-frontend-471533886200`
  - Website Hosting: Enabled
  - Public Access: Allowed for website
  - Versioning: Enabled
- Data Bucket: `adr-ohlcv-471533886200`
  - Versioning: Enabled

### IAM Setup

**GitHub Actions User:**
- Username: `github-actions-adr-user`
- Permissions:
  - CloudFormation: Full access
  - Lambda: Full access
  - DynamoDB: Full access
  - S3: Full access
  - IAM: PassRole permission

## Deployment Pipeline

### GitHub Actions Workflow

```
Push to main branch
       ↓
Checkout code
       ↓
Configure AWS credentials (IAM user)
       ↓
Validate CloudFormation template
       ↓
Deploy stack (create or update)
       ↓
Test Lambda functions
       ↓
✅ Success or ❌ Failure notification
```

**Triggers:** Push to main branch (automatic)

**Timing:** ~2-3 minutes per deployment

## Development Environment

### Local Setup

```
Your Machine
└── Project
    └── AI-Project-ADR
        ├── frontend/           (React SPA)
        │   ├── src/
        │   ├── public/
        │   ├── package.json
        │   ├── .env            (Cognito credentials)
        │   └── build/          (after npm run build)
        │
        ├── backend/            (Python Lambda functions)
        │   ├── functions/
        │   └── requirements.txt
        │
        ├── template.yaml       (CloudFormation IaC)
        ├── .github/workflows/  (CI/CD)
        └── docs/               (Documentation)
```

### Environment Variables

**Frontend (.env):**
```
REACT_APP_COGNITO_REGION=ap-south-1
REACT_APP_COGNITO_USER_POOL_ID=ap-south-1_RYAH5LzcK
REACT_APP_COGNITO_CLIENT_ID=2osdell6nkret9qmqjie6gd6un
REACT_APP_API_ENDPOINT=http://localhost:3001
```

**Backend (Lambda environment):**
```
ENVIRONMENT=dev
DYNAMODB_TABLE_CROSSINGS=adr-crossings-dev
DYNAMODB_TABLE_HISTORY=adr-history-dev
S3_BUCKET_OHLCV=adr-ohlcv-471533886200
```

**GitHub Secrets:**
```
AWS_ACCESS_KEY_ID=***
AWS_SECRET_ACCESS_KEY=***
```

## Security Layers

### 1. Frontend Layer
- Tokens stored in browser IndexedDB (amazon-cognito-identity-js)
- Automatic token refresh
- Protected routes require valid session
- HTTPS only (S3 website hosting)

### 2. Authentication Layer
- Cognito User Pool (AWS managed)
- Email verification required
- Strong password policy enforced
- JWT tokens for API calls

### 3. Backend Layer
- Lambda functions execute in VPC
- DynamoDB encryption at rest (default)
- S3 bucket versioning enabled
- CloudFormation for infrastructure as code

### 4. CI/CD Layer
- GitHub Actions uses IAM credentials
- No OIDC (switched to static credentials)
- Repository secrets for sensitive data
- Deployment limited to authenticated GitHub actions

## Monitoring & Logging

### CloudWatch

**Lambda Logs:**
- `aws logs tail /aws/lambda/adr-scanner-login-dev`
- `aws logs tail /aws/lambda/adr-scanner-crossing-dev`
- `aws logs tail /aws/lambda/adr-scanner-dashboard-dev`

**DynamoDB Metrics:**
- Item count
- Read/write units consumed
- Latency

### Error Handling

- Frontend: Try/catch blocks, error messages to user
- Lambda: Structured logging, error responses
- Cognito: Standard error codes (InvalidPasswordException, etc.)

## Cost Optimization

**Free Tier Usage:**
- Cognito: 50,000 monthly active users
- Lambda: 1 million free requests + 400,000 GB-seconds
- DynamoDB: 25 GB storage

**Expected Monthly Cost:**
- Lambda: ~$0.20
- DynamoDB: ~$1.00
- S3: ~$0.50
- Cognito: $0 (under free tier)
- **Total: ~$2**

## Future Enhancements

1. **API Gateway Integration**
   - RESTful API endpoints
   - Request/response validation
   - Rate limiting
   - CORS headers

2. **Additional Features**
   - WhatsApp notifications
   - Email alerts
   - Real-time ADR calculations
   - Historical analysis dashboard

3. **Infrastructure**
   - CloudFront CDN for faster delivery
   - SNS/SQS for async processing
   - EventBridge for scheduled scans
   - RDS for complex queries

4. **Monitoring**
   - CloudWatch dashboards
   - X-Ray tracing
   - Custom metrics
   - Alarms for failures

---

**Architecture Last Updated:** 2026-11-24  
**Stack:** React + Cognito + Lambda + DynamoDB + S3  
**Region:** ap-south-1 (Mumbai)
