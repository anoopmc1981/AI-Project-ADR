@echo off
REM Deploy backend using CloudFormation

cd /d "d:\Project\Git-AI-Projects\AI-Project-ADR"

echo Deploying backend stack using CloudFormation...
aws cloudformation deploy ^
  --template-file template-cf.yaml ^
  --stack-name adr-scanner-dev ^
  --region ap-south-1 ^
  --capabilities CAPABILITY_NAMED_IAM

if errorlevel 1 (
  echo Deployment failed!
  pause
  exit /b 1
)

echo.
echo Stack deployed successfully!
echo Waiting 10 seconds for stack to settle...
timeout /t 10

echo.
echo Getting API endpoint...
for /f "delims=" %%i in ('aws cloudformation describe-stacks --stack-name adr-scanner-dev --region ap-south-1 --query "Stacks[0].Outputs[?OutputKey==`DashboardApiEndpoint`].OutputValue" --output text') do set API_ENDPOINT=%%i

echo.
echo ========================================
echo API Endpoint: %API_ENDPOINT%
echo ========================================
echo.
echo Next step: Update frontend\.env with:
echo REACT_APP_API_ENDPOINT=%API_ENDPOINT%
echo.
pause
