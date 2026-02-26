param(
  [Parameter(Mandatory = $true)]
  [string]$BucketName,

  [Parameter(Mandatory = $false)]
  [string]$DistributionId,

  [Parameter(Mandatory = $false)]
  [string]$Region = "eu-north-1",

  [Parameter(Mandatory = $false)]
  [string]$AwsProfile
)

$ErrorActionPreference = "Stop"

Write-Host "\n=== ExamBuddy Frontend Deploy (S3 + CloudFront) ===" -ForegroundColor Cyan

if ($AwsProfile) {
  $env:AWS_PROFILE = $AwsProfile
  Write-Host "Using AWS profile: $AwsProfile" -ForegroundColor Yellow
}

Write-Host "Checking required tools..." -ForegroundColor Yellow
aws --version | Out-Null
node --version | Out-Null
npm --version | Out-Null

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendPath = Join-Path $repoRoot "frontend"

if (-not (Test-Path $frontendPath)) {
  throw "Frontend folder not found at: $frontendPath"
}

Push-Location $frontendPath
try {
  Write-Host "Installing dependencies..." -ForegroundColor Yellow
  npm ci

  Write-Host "Building production frontend..." -ForegroundColor Yellow
  npm run build:prod

  $distPath = Join-Path $frontendPath "dist"
  if (-not (Test-Path $distPath)) {
    throw "Build output not found at: $distPath"
  }

  Write-Host "Uploading static assets with long cache..." -ForegroundColor Yellow
  aws s3 sync "$distPath" "s3://$BucketName" --delete --region $Region --exclude "index.html" --cache-control "public,max-age=31536000,immutable"

  Write-Host "Uploading index.html with no-cache..." -ForegroundColor Yellow
  aws s3 cp "$distPath/index.html" "s3://$BucketName/index.html" --region $Region --cache-control "no-cache,no-store,must-revalidate" --content-type "text/html"

  if ($DistributionId) {
    Write-Host "Creating CloudFront invalidation..." -ForegroundColor Yellow
    aws cloudfront create-invalidation --distribution-id $DistributionId --paths "/*" | Out-Null
    Write-Host "CloudFront invalidation submitted." -ForegroundColor Green
  }

  Write-Host "\nDeployment completed successfully." -ForegroundColor Green
  Write-Host "S3 Bucket: s3://$BucketName" -ForegroundColor Gray
  if ($DistributionId) {
    Write-Host "CloudFront Distribution: $DistributionId" -ForegroundColor Gray
  }
}
finally {
  Pop-Location
}
