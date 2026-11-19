# ADR Stock Scanner - Quick Start Guide

**Get the application running in 30 minutes!**

## 5-Minute Setup

### 1. Prerequisites Check
```bash
# Verify installations
python --version                 # Should be 3.11+
sam --version                   # Should be 1.100+
aws --version                   # Should be 2.x
docker --version                # Should be running
```

### 2. Clone & Install
```bash
git clone <repo-url>
cd AI-Project-ADR
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

## 15-Minute Local Development

### 1. Build
```bash
sam build --use-container
```

### 2. Start Local API
```bash
# Terminal 1
sam local start-api --port 3001
```

### 3. Serve Frontend
```bash
# Terminal 2
cd frontend
python -m http.server 8080
```

### 4. Access Dashboard
- Open browser: **http://localhost:8080**
- Use test credentials (or create Cognito user)
- Dashboard should load with sample data

## 30-Minute AWS Deployment

### Prerequisites
- AWS account
- Fyers API key
- WhatsApp API credentials (optional for now)

### Step 1: Configure AWS
```bash
aws configure
# Enter: AWS Access Key ID
# Enter: AWS Secret Access Key
# Enter: Default region (us-east-1)
# Enter: Default output format (json)
```

### Step 2: Create Secrets
```bash
# Store Fyers API key
aws secretsmanager create-secret \
    --name fyers-api-key \
    --secret-string '{"api_key":"YOUR_FYERS_KEY_HERE"}'

# Store WhatsApp credentials (optional)
aws secretsmanager create-secret \
    --name whatsapp-credentials \
    --secret-string '{
        "api_key": "YOUR_WHATSAPP_KEY",
        "api_url": "YOUR_WHATSAPP_URL"
    }'
```

### Step 3: Deploy
```bash
# First deployment (interactive)
sam deploy --guided

# You'll be prompted for:
# Stack name: adr-scanner-dev
# Region: us-east-1
# Confirm changes: Y
# Allow IAM role creation: Y
# Save configuration: Y
```

### Step 4: Get Outputs
```bash
aws cloudformation describe-stacks \
    --stack-name adr-scanner-dev \
    --query 'Stacks[0].Outputs' \
    --output table
```

### Step 5: Deploy Frontend
```bash
# Get bucket name from outputs
aws s3 sync frontend/ s3://YOUR_BUCKET_NAME --delete

# Get CloudFront distribution ID
aws cloudfront create-invalidation \
    --distribution-id YOUR_DIST_ID \
    --paths "/*"
```

### Step 6: Access Application
- Open the CloudFront URL from outputs
- Login with Cognito user
- Start using the dashboard!

## Command Reference

### Build & Test
```bash
sam build --use-container           # Build SAM
sam validate                        # Validate template
sam local start-api --port 3001     # Local API
sam local invoke FunctionName       # Invoke function
pytest tests/ -v                    # Run tests
```

### Deploy & Manage
```bash
sam deploy                          # Deploy to AWS
sam sync --watch                    # Hot reload during development
sam delete                          # Delete stack

# CloudFormation
aws cloudformation describe-stacks --stack-name adr-scanner-dev
aws cloudformation delete-stack --stack-name adr-scanner-dev
```

### Monitor & Debug
```bash
# View logs
aws logs tail /aws/lambda/adr-scanner-calculation-dev --follow

# Search errors
aws logs filter-log-events \
    --log-group-name /aws/lambda/adr-scanner-crossing-dev \
    --filter-pattern "ERROR"

# Get metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Invocations \
    --dimensions Name=FunctionName,Value=adr-scanner-calculation-dev \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-31T23:59:59Z \
    --period 3600 \
    --statistics Sum
```

### User Management (Cognito)
```bash
# Create user
aws cognito-idp admin-create-user \
    --user-pool-id POOL_ID \
    --username user@example.com \
    --temporary-password TempPass123! \
    --message-action SUPPRESS

# Set permanent password
aws cognito-idp admin-set-user-password \
    --user-pool-id POOL_ID \
    --username user@example.com \
    --password NewPass123! \
    --permanent

# Get user info
aws cognito-idp admin-get-user \
    --user-pool-id POOL_ID \
    --username user@example.com
```

### Database Queries
```bash
# Query ADR levels for today
aws dynamodb query \
    --table-name adr-scanner-levels-dev \
    --key-condition-expression "symbol = :sym AND calculation_date = :date" \
    --expression-attribute-values \
        '{":sym":{"S":"INFY"},":date":{"S":"2024-01-15"}}'

# Scan today's crossings
aws dynamodb query \
    --table-name adr-scanner-crossings-dev \
    --index-name SymbolDateIndex \
    --key-condition-expression "crossing_date = :date" \
    --expression-attribute-values '{":date":{"S":"2024-01-15"}}'
```

## API Testing

### Test Login
```bash
curl -X POST http://localhost:3001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@example.com",
    "password":"password123"
  }'
```

### Get Crossings
```bash
curl -X GET "http://localhost:3001/api/crossings?direction=UPPER" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test AI Chat
```bash
curl -X POST http://localhost:3001/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query":"Show upper crossings with high volume",
    "type":"filter"
  }'
```

## Troubleshooting

### SAM Build Fails
```bash
# Clean and retry
rm -rf .aws-sam build/
sam build --use-container
```

### DynamoDB Local Issues
```bash
# Stop and restart
docker stop $(docker ps -q)
docker run -p 8000:8000 amazon/dynamodb-local
```

### Lambda Timeout
```yaml
# Increase in template.yaml
Timeout: 300  # Increase from default 60
```

### CORS Errors
- Check API Gateway CORS settings
- Verify Authorization header in requests
- Check Access-Control-Allow-Origin

### Login Fails
```bash
# Verify user exists
aws cognito-idp list-users --user-pool-id POOL_ID

# Check credentials
# Email must match exactly (case-sensitive)
```

## File Locations

| What | Where |
|-----|-------|
| Backend code | `backend/functions/*/app.py` |
| Frontend HTML | `frontend/index.html` |
| Frontend CSS | `frontend/css/style.css` |
| Frontend JS | `frontend/js/*.js` |
| Infrastructure | `template.yaml` |
| Local config | `.aws-sam/` (auto-generated) |
| Requirements | `backend/requirements.txt` |

## Environment Variables

For local testing, create `.env`:
```
ENVIRONMENT=dev
AWS_REGION=us-east-1
FYERS_API_KEY=your_key
ADR_PERIOD=14
ADR_MULTIPLIER=1.0
```

## Next Steps

1. ✅ Complete setup (this guide)
2. 📖 Read [README.md](README.md) for features
3. 🏗️ Review [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md) for details
4. 📦 Read [DEPLOYMENT.md](DEPLOYMENT.md) for production
5. 💻 Start developing!

## Getting Help

| Issue | Solution |
|-------|----------|
| Build fails | Check SAM version, Docker running |
| API 502 | Check Lambda logs with `aws logs tail` |
| Frontend blank | Check browser console for errors |
| Login fails | Verify Cognito user pool ID |
| No data | Check Fyers API key, market hours |

## Performance Tips

```bash
# Profile Lambda
sam local invoke -d 5858 FunctionName --event event.json

# Monitor dashboard
watch -n 1 'aws cloudformation describe-stacks \
    --stack-name adr-scanner-dev \
    --query Stacks[0].StackStatus'

# Check costs (estimated)
aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity DAILY \
    --metrics "BlendedCost"
```

## Quick Deployment Checklist

- [ ] AWS credentials configured
- [ ] Fyers API key in Secrets Manager
- [ ] SAM CLI installed & verified
- [ ] Docker running
- [ ] `sam build` completes successfully
- [ ] `sam deploy --guided` runs without errors
- [ ] Cognito user created
- [ ] Frontend uploaded to S3
- [ ] CloudFront URL accessible
- [ ] Dashboard loads in browser
- [ ] Login works
- [ ] Can see sample data

## One-Liner Commands

```bash
# Build and deploy everything
sam build --use-container && sam deploy

# Check all Lambda functions
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `adr-scanner`)].FunctionName'

# View all DynamoDB tables
aws dynamodb list-tables | grep adr-scanner

# Get all API Gateway endpoints
aws apigateway get-rest-apis --query 'items[?name==`ADRScannerApi`].id' | aws apigateway get-stages --rest-api-id=$(aws apigateway get-rest-apis --query 'items[?name==`ADRScannerApi`].id' --output text) --query 'item[].invokeUrl'

# Monitor Lambda errors
watch -n 5 'aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Errors --dimensions Name=FunctionName,Value=adr-scanner-calculation-dev --start-time $(date -u -d "10 minutes ago" +%Y-%m-%dT%H:%M:%S) --end-time $(date -u +%Y-%m-%dT%H:%M:%S) --period 60 --statistics Sum'
```

## Cleanup

```bash
# Delete everything
aws cloudformation delete-stack --stack-name adr-scanner-dev

# Wait for completion
aws cloudformation wait stack-delete-complete --stack-name adr-scanner-dev

# Delete secrets
aws secretsmanager delete-secret --secret-id fyers-api-key --force-delete-without-recovery

# Delete S3 bucket (if needed)
aws s3 rb s3://YOUR_BUCKET_NAME --force
```

---

**Ready to go! You have everything needed to deploy the ADR Stock Scanner to production. 🚀**
