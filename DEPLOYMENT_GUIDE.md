# ADR Scanner - Backend & Frontend Integration Guide

## Prerequisites
- AWS CLI configured with proper credentials
- AWS Account with ap-south-1 region
- Node.js and npm installed

## Step 1: Deploy Backend with API Gateway

### Update CloudFormation Stack
The template.yaml has been updated with API Gateway integration. Deploy:

```bash
cd d:\Project\Git-AI-Projects\AI-Project-ADR
sam deploy
```

Or use the IAM credentials:

```bash
sam deploy \
  --template-file template.yaml \
  --stack-name adr-scanner-dev \
  --region ap-south-1 \
  --capabilities CAPABILITY_IAM \
  --profile default
```

### Get API Gateway Endpoint
After deployment, get the API endpoint from CloudFormation outputs:

```bash
aws cloudformation describe-stacks \
  --stack-name adr-scanner-dev \
  --region ap-south-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`DashboardApiEndpoint`].OutputValue' \
  --output text
```

The output will look like:
```
https://xxxxxxxxxx.execute-api.ap-south-1.amazonaws.com/dev
```

## Step 2: Update Frontend Configuration

### Update .env file
Edit `frontend/.env` and set the API endpoint:

```
REACT_APP_API_ENDPOINT=https://xxxxxxxxxx.execute-api.ap-south-1.amazonaws.com/dev
```

Replace `xxxxxxxxxx` with your actual API Gateway ID.

## Step 3: Rebuild and Deploy Frontend

```bash
cd frontend
npm run build
aws s3 sync build s3://adr-frontend-471533886200 --region ap-south-1 --delete
```

## Step 4: Test the Integration

1. Open browser and visit: `http://adr-frontend-471533886200.s3-website.ap-south-1.amazonaws.com`
2. Login with your credentials
3. The Dashboard should now display crossings data from DynamoDB

## Troubleshooting

### API Error: "Not Authenticated"
- Ensure tokens are being stored in localStorage
- Check browser console for auth errors
- Verify Cognito user pool configuration

### API Error: 404
- Verify the API Gateway endpoint in .env is correct
- Check that the DashboardFunction is properly deployed
- Ensure Lambda execution role has DynamoDB read permissions

### No Crossings Displayed
- The DynamoDB tables might be empty
- Run the crossing detection function to populate data
- Or manually insert test data into DynamoDB

### CORS Errors
- The Lambda function already returns CORS headers
- Ensure the API Gateway is properly configured
- Check browser network tab for specific CORS error details

## Data Flow

1. **Frontend** → Calls Dashboard API with authentication token
2. **API Gateway** → Validates Cognito authorization
3. **Lambda (Dashboard)** → Reads from DynamoDB CrossingsTable
4. **Lambda** → Formats and returns data
5. **Frontend** → Displays crossings in the dashboard

## Next Steps

1. Add dashboard data population (ADR calculations)
2. Set up scheduled crossing detection
3. Configure WhatsApp alerts
4. Add user settings management
