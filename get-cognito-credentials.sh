#!/bin/bash

# Get the current Cognito credentials from CloudFormation stack
echo "Getting Cognito credentials from CloudFormation..."

USER_POOL_ID=$(aws cloudformation describe-stacks \
  --stack-name adr-scanner-dev \
  --region ap-south-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`CognitoUserPoolId`].OutputValue' \
  --output text)

CLIENT_ID=$(aws cloudformation describe-stacks \
  --stack-name adr-scanner-dev \
  --region ap-south-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`CognitoClientId`].OutputValue' \
  --output text)

echo "User Pool ID: $USER_POOL_ID"
echo "Client ID: $CLIENT_ID"

# Update .env file
cat > frontend/.env << EOF
REACT_APP_COGNITO_REGION=ap-south-1
REACT_APP_COGNITO_USER_POOL_ID=$USER_POOL_ID
REACT_APP_COGNITO_CLIENT_ID=$CLIENT_ID
REACT_APP_API_ENDPOINT=http://localhost:3001
EOF

echo "✅ Updated frontend/.env with new Cognito credentials"
