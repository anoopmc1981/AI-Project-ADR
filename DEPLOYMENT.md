# ADR Level Breakout Stock Scanner - Deployment Guide

## Prerequisites

1. **AWS Account** with appropriate permissions (IAM, Lambda, DynamoDB, S3, etc.)
2. **AWS CLI** configured with credentials
3. **AWS SAM CLI** installed
4. **Python 3.11+**
5. **Fyers Broker Account** with API credentials
6. **WhatsApp Business Account** (for alerts)

## Environment Setup

### 1. Clone and Setup Repository

```bash
git clone <repository-url>
cd AI-Project-ADR
```

### 2. Create Python Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 3. Configure Secrets

Create secrets in AWS Secrets Manager:

```bash
# Fyers API Credentials
aws secretsmanager create-secret \
    --name fyers-api-key \
    --secret-string '{"api_key":"YOUR_FYERS_API_KEY"}'

# WhatsApp Credentials
aws secretsmanager create-secret \
    --name whatsapp-credentials \
    --secret-string '{
        "api_key": "YOUR_WHATSAPP_API_KEY",
        "api_url": "YOUR_WHATSAPP_API_URL"
    }'
```

### 4. Update SAM Template

Edit `template.yaml` and update:
- `Environment` parameter (dev/staging/prod)
- `CognitoDomain` parameter
- Region and account ID references

## Deployment Steps

### Step 1: Build the Application

```bash
sam build --use-container
```

### Step 2: Deploy to AWS

#### First Deployment (Interactive)
```bash
sam deploy --guided
```

You'll be prompted for:
- Stack name (e.g., `adr-scanner-dev`)
- AWS Region
- Confirm changes before deploy
- Allow SAM to create IAM roles
- Save parameters to samconfig.toml

#### Subsequent Deployments
```bash
sam deploy
```

### Step 3: Retrieve Outputs

```bash
aws cloudformation describe-stacks \
    --stack-name adr-scanner-dev \
    --query 'Stacks[0].Outputs'
```

Note the following outputs:
- `CloudFrontURL` - Frontend URL
- `ApiEndpoint` - API Gateway endpoint
- `CognitoUserPoolId` - For user management
- `CognitoClientId` - For frontend auth

### Step 4: Deploy Frontend

```bash
# Get S3 bucket name from CloudFormation outputs
aws s3 sync frontend/ s3://YOUR_FRONTEND_BUCKET_NAME/ \
    --delete \
    --cache-control "max-age=300"

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
    --distribution-id YOUR_DISTRIBUTION_ID \
    --paths "/*"
```

## Configuration

### Update Frontend Config

Edit `frontend/js/auth.js` and update:
- `API_BASE_URL` - Set to your API Gateway endpoint
- Cognito User Pool ID
- Cognito Client ID

```javascript
const API_BASE_URL = 'https://your-api-gateway-url.execute-api.region.amazonaws.com/dev';
```

### Create Cognito Users

```bash
# Create test user
aws cognito-idp admin-create-user \
    --user-pool-id YOUR_USER_POOL_ID \
    --username testuser@example.com \
    --temporary-password TempPassword123! \
    --message-action SUPPRESS

# Set permanent password
aws cognito-idp admin-set-user-password \
    --user-pool-id YOUR_USER_POOL_ID \
    --username testuser@example.com \
    --password FinalPassword123! \
    --permanent
```

## Local Development

### Run SAM Local API

```bash
sam local start-api --port 3001
```

This starts a local API Gateway at `http://localhost:3001`

### Test Individual Lambda Functions

```bash
# Test ADR calculation
sam local invoke ADRCalculationFunction \
    --event events/adr-calc-event.json

# Test crossing detection
sam local invoke CrossingDetectionFunction \
    --event events/crossing-event.json
```

## Testing

### Unit Tests

```bash
pytest tests/ -v

# Run specific test
pytest tests/test_adr_calculation.py -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

### Integration Tests

```bash
# Test with live DynamoDB
AWS_ENDPOINT_URL=http://localhost:8000 pytest tests/integration/ -v
```

### Manual Testing

1. Navigate to CloudFront URL
2. Login with test user credentials
3. Verify dashboard loads
4. Test filters and search
5. Try AI assistant queries

## Monitoring and Debugging

### View Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/adr-scanner-dashboard-dev --follow

# View specific function logs
aws logs tail /aws/lambda/adr-scanner-calculation-dev --follow

# Search for errors
aws logs filter-log-events \
    --log-group-name /aws/lambda/adr-scanner-crossing-dev \
    --filter-pattern "ERROR"
```

### CloudWatch Metrics

```bash
# View Lambda invocations
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Invocations \
    --dimensions Name=FunctionName,Value=adr-scanner-calculation-dev \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-31T23:59:59Z \
    --period 3600 \
    --statistics Sum
```

### CloudWatch Alarms

```bash
# Create alarm for Lambda errors
aws cloudwatch put-metric-alarm \
    --alarm-name adr-scanner-calculation-errors \
    --alarm-description "Alert on ADR calculation errors" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --threshold 5 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1
```

## Troubleshooting

### API Gateway CORS Issues

If you see CORS errors in frontend, ensure the API Gateway has CORS enabled:

```bash
aws apigateway put-integration-response \
    --rest-api-id YOUR_API_ID \
    --resource-id YOUR_RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Headers":"'"'"'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"'"'","method.response.header.Access-Control-Allow-Methods":"'"'"'GET,POST,PUT,DELETE,OPTIONS'"'"'","method.response.header.Access-Control-Allow-Origin":"'"'"'*'"'"'"}' \
    --response-templates '{"application/json":""}'
```

### DynamoDB Throttling

If experiencing throttling:

```bash
# Check current provisioning
aws dynamodb describe-table --table-name adr-scanner-crossings-dev

# Update to higher capacity if needed (PAY_PER_REQUEST is already set)
# No action needed as template uses on-demand billing
```

### Cognito Authentication Issues

```bash
# Check user attributes
aws cognito-idp admin-get-user \
    --user-pool-id YOUR_USER_POOL_ID \
    --username testuser@example.com

# Reset password
aws cognito-idp admin-set-user-password \
    --user-pool-id YOUR_USER_POOL_ID \
    --username testuser@example.com \
    --password NewPassword123! \
    --permanent
```

## Production Deployment Checklist

- [ ] Update all environment variables for production
- [ ] Enable CloudFront OAI for S3 frontend bucket
- [ ] Configure custom domain for CloudFront
- [ ] Setup SSL/TLS certificates
- [ ] Enable CloudWatch detailed monitoring
- [ ] Setup CloudWatch alarms for key metrics
- [ ] Enable VPC endpoints for private access
- [ ] Configure backup for DynamoDB tables
- [ ] Setup cross-region replication if needed
- [ ] Test disaster recovery procedures
- [ ] Document runbooks for operations
- [ ] Setup budget alerts
- [ ] Review IAM policies for least privilege
- [ ] Enable API Gateway logging
- [ ] Configure rate limiting on APIs
- [ ] Enable X-Ray tracing

## Cost Optimization

1. **DynamoDB**: Using on-demand billing (PAY_PER_REQUEST)
   - Pay for read/write capacity used
   - No provisioning needed

2. **Lambda**: 
   - Monitor execution duration
   - Optimize cold starts
   - Consider Reserved Concurrency if needed

3. **S3**:
   - Use S3 lifecycle policies for older data
   - Consider Glacier for historical data retention

4. **CloudFront**:
   - Configure appropriate cache TTLs
   - Use regional edge caches

## Support and Updates

For issues or updates:
1. Check CloudWatch logs first
2. Review AWS service health dashboard
3. Check Fyers API status
4. Review application logs in DynamoDB

## Cleanup

To delete all AWS resources:

```bash
# Delete CloudFormation stack (this removes all resources)
aws cloudformation delete-stack --stack-name adr-scanner-dev

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete --stack-name adr-scanner-dev

# Delete Secrets Manager secrets
aws secretsmanager delete-secret --secret-id fyers-api-key --force-delete-without-recovery
aws secretsmanager delete-secret --secret-id whatsapp-credentials --force-delete-without-recovery
```

---

**Important**: This application handles real market data. Thoroughly test in non-production environments before deploying to production.
