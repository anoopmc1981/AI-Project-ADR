@echo off
REM Deploy frontend to S3
cd /d "d:\Project\Git-AI-Projects\AI-Project-ADR\frontend"

echo Building frontend...
call npm run build

echo Deploying to S3...
aws s3 sync build s3://adr-frontend-471533886200 --region ap-south-1 --delete

echo Deployment complete!
echo Frontend URL: http://adr-frontend-471533886200.s3-website.ap-south-1.amazonaws.com
