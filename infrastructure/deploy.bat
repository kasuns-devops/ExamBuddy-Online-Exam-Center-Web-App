@echo off
REM Docker Deployment Quick Start Script for Windows

echo.
echo ==========================================
echo ExamBuddy Docker Deployment Script
echo ==========================================
echo.

REM Check if Docker is running
echo Checking Docker status...
docker ps >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Docker is not running!
    echo.
    echo Please start Docker Desktop and run this script again.
    echo.
    pause
    exit /b 1
)

echo [OK] Docker is running ✓
echo.

REM Check AWS credentials
echo Checking AWS credentials...
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo.
    echo [WARNING] AWS credentials not configured!
    echo.
    echo Running: aws configure
    echo.
    call aws configure
    if errorlevel 1 (
        echo [ERROR] AWS configuration failed!
        pause
        exit /b 1
    )
)

echo [OK] AWS credentials configured ✓
echo.

REM Build Docker image
echo.
echo Step 1: Building Docker image...
echo ==========================================
docker build -f Dockerfile.deploy -t exambuddy-deploy:latest .
if errorlevel 1 (
    echo [ERROR] Docker build failed!
    pause
    exit /b 1
)

echo [OK] Docker image built successfully ✓
echo.

REM Run SAM build
echo.
echo Step 2: Running SAM build...
echo ==========================================
docker run -it ^
  -v %CD%:/app ^
  -w /app/backend ^
  exambuddy-deploy:latest ^
  sam build

if errorlevel 1 (
    echo [ERROR] SAM build failed!
    pause
    exit /b 1
)

echo [OK] SAM build completed ✓
echo.

REM Run SAM deploy
echo.
echo Step 3: Running SAM deploy (interactive)...
echo ==========================================
echo.
echo You will now be prompted for deployment parameters.
echo Press Enter to continue...
pause

docker run -it ^
  -v %CD%:/app ^
  -v %USERPROFILE%/.aws:/root/.aws ^
  -w /app/backend ^
  exambuddy-deploy:latest ^
  sam deploy --guided

if errorlevel 1 (
    echo [ERROR] SAM deploy failed!
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Deployment completed! ✓
echo.
echo Next steps:
echo 1. Note your API Gateway URL from CloudFormation outputs
echo 2. Update frontend API configuration
echo 3. Test endpoints in staging
echo.
pause
