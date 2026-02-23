#!/usr/bin/env pwsh
# Docker Deployment Quick Start Script for PowerShell

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ExamBuddy Docker Deployment Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
try {
    docker ps > $null 2>&1
    Write-Host "[OK] Docker is running ✓" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "[ERROR] Docker is not running!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start Docker Desktop and run this script again." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check AWS credentials
Write-Host "Checking AWS credentials..." -ForegroundColor Yellow
try {
    aws sts get-caller-identity > $null 2>&1
    Write-Host "[OK] AWS credentials configured ✓" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "[WARNING] AWS credentials not configured!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Running: aws configure" -ForegroundColor Yellow
    Write-Host ""
    
    aws configure
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] AWS configuration failed!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""

# Build Docker image
Write-Host ""
Write-Host "Step 1: Building Docker image..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

docker build -f Dockerfile.deploy -t exambuddy-deploy:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker build failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Docker image built successfully ✓" -ForegroundColor Green
Write-Host ""

# Run SAM build
Write-Host ""
Write-Host "Step 2: Running SAM build..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$projectRoot = Get-Location
$backedPath = Join-Path $projectRoot "backend"

docker run -it `
  -v ${projectRoot}:/app `
  -w /app/backend `
  exambuddy-deploy:latest `
  sam build

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] SAM build failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] SAM build completed ✓" -ForegroundColor Green
Write-Host ""

# Run SAM deploy
Write-Host ""
Write-Host "Step 3: Running SAM deploy (interactive)..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You will now be prompted for deployment parameters:" -ForegroundColor Yellow
Write-Host ""
Write-Host "When asked:" -ForegroundColor Yellow
Write-Host "  - Stack name: exambuddy-staging" -ForegroundColor Gray
Write-Host "  - Region: us-east-1" -ForegroundColor Gray
Write-Host "  - S3 Bucket names: Must be GLOBALLY UNIQUE" -ForegroundColor Gray
Write-Host "  - Parameters: See DOCKER_DEPLOYMENT_GUIDE.md" -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to continue"

$awsPath = Join-Path $env:USERPROFILE ".aws"

docker run -it `
  -v ${projectRoot}:/app `
  -v ${awsPath}:/root/.aws `
  -w /app/backend `
  exambuddy-deploy:latest `
  sam deploy --guided

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] SAM deploy failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[SUCCESS] Deployment completed! ✓" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Note your API Gateway URL from CloudFormation outputs" -ForegroundColor Gray
Write-Host "  2. Update frontend API configuration" -ForegroundColor Gray
Write-Host "  3. Test endpoints in staging" -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to exit"
