@echo off
REM Build and deploy frontend

cd /d "d:\Project\Git-AI-Projects\AI-Project-ADR\frontend"

echo Checking if build exists...
if exist build\index.html (
  echo Build already exists, skipping npm build...
) else (
  echo Building frontend...
  call npm run build
  if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
  )
)

echo.
echo Deploying to S3...
aws s3 sync build s3://adr-frontend-471533886200 --region ap-south-1 --delete

if errorlevel 1 (
  echo S3 deployment failed!
  pause
  exit /b 1
)

echo.
echo Deployment complete!
echo Frontend URL: http://adr-frontend-471533886200.s3-website.ap-south-1.amazonaws.com
echo.
pause
