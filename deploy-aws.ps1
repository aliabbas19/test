# PowerShell Script for Automatic AWS Deployment
# Run: .\deploy-aws.ps1

param(
    [Parameter(Mandatory = $true)]
    [string]$AwsAccountId,
    
    [Parameter(Mandatory = $true)]
    [string]$DbPassword,
    
    [Parameter(Mandatory = $true)]
    [string]$SecretKey,
    
    [string]$Region = "me-south-1",
    [string]$ProjectName = "basamaljanaby"
)

$ErrorActionPreference = "Stop"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  AWS Automatic Deployment Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "[1/8] Checking prerequisites..." -ForegroundColor Yellow

# Check AWS CLI
try {
    aws --version | Out-Null
    Write-Host "  ✓ AWS CLI installed" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ AWS CLI not found. Install from: https://aws.amazon.com/cli/" -ForegroundColor Red
    exit 1
}

# Check Docker
try {
    docker --version | Out-Null
    Write-Host "  ✓ Docker installed" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Docker not found. Install Docker Desktop" -ForegroundColor Red
    exit 1
}

# Check Terraform
try {
    terraform --version | Out-Null
    Write-Host "  ✓ Terraform installed" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Terraform not found. Install from: https://terraform.io" -ForegroundColor Red
    exit 1
}

# Variables
$EcrRepo = "$AwsAccountId.dkr.ecr.$Region.amazonaws.com/$ProjectName-backend"

# Step 2: Create ECR Repository
Write-Host ""
Write-Host "[2/8] Creating ECR Repository..." -ForegroundColor Yellow
try {
    aws ecr create-repository --repository-name "$ProjectName-backend" --region $Region --image-scanning-configuration scanOnPush=true 2>$null
    Write-Host "  ✓ ECR repository created" -ForegroundColor Green
}
catch {
    Write-Host "  ✓ ECR repository already exists" -ForegroundColor Green
}

# Step 3: Login to ECR
Write-Host ""
Write-Host "[3/8] Logging in to ECR..." -ForegroundColor Yellow
$loginCmd = aws ecr get-login-password --region $Region
docker login --username AWS --password $loginCmd "$AwsAccountId.dkr.ecr.$Region.amazonaws.com"
Write-Host "  ✓ Logged in to ECR" -ForegroundColor Green

# Step 4: Build Docker Image
Write-Host ""
Write-Host "[4/8] Building Docker image..." -ForegroundColor Yellow
Push-Location backend
docker build -t "$ProjectName-backend" .
docker tag "${ProjectName}-backend:latest" "${EcrRepo}:latest"
Pop-Location
Write-Host "  ✓ Docker image built" -ForegroundColor Green

# Step 5: Push to ECR
Write-Host ""
Write-Host "[5/8] Pushing image to ECR..." -ForegroundColor Yellow
docker push "${EcrRepo}:latest"
Write-Host "  ✓ Image pushed to ECR" -ForegroundColor Green

# Step 6: Initialize Terraform
Write-Host ""
Write-Host "[6/8] Initializing Terraform..." -ForegroundColor Yellow
Push-Location infrastructure
terraform init
Write-Host "  ✓ Terraform initialized" -ForegroundColor Green

# Step 7: Apply Terraform
Write-Host ""
Write-Host "[7/8] Deploying infrastructure with Terraform..." -ForegroundColor Yellow
terraform apply `
    -var="ecr_repository_url=$EcrRepo" `
    -var="db_password=$DbPassword" `
    -var="secret_key=$SecretKey" `
    -auto-approve
Pop-Location
Write-Host "  ✓ Infrastructure deployed" -ForegroundColor Green

# Step 8: Build and Deploy Frontend
Write-Host ""
Write-Host "[8/8] Building and deploying frontend..." -ForegroundColor Yellow
Push-Location frontend
npm run build

# Get S3 bucket name from Terraform output
Push-Location ..\infrastructure
$S3Bucket = terraform output -raw s3_bucket_name 2>$null
$CloudFrontId = terraform output -raw cloudfront_distribution_id 2>$null
Pop-Location

if ($S3Bucket) {
    aws s3 sync dist/ "s3://$S3Bucket/frontend/" --delete
    Write-Host "  ✓ Frontend uploaded to S3" -ForegroundColor Green
    
    if ($CloudFrontId) {
        aws cloudfront create-invalidation --distribution-id $CloudFrontId --paths "/*"
        Write-Host "  ✓ CloudFront cache invalidated" -ForegroundColor Green
    }
}
Pop-Location

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  ✓ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your application is now deployed on AWS!" -ForegroundColor Cyan
Write-Host ""
