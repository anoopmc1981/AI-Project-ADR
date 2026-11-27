@echo off
echo Installing dependencies...
call npm install

echo.
echo Building frontend...
call npm run build

echo.
echo Build complete! Files ready in build/ directory
pause
