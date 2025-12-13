# AWS Lightsail Deployment Script
# Cost: ~$25-30/month
# Run: .\deploy-lightsail.ps1

param(
    [string]$Region = "me-south-1",
    [string]$InstanceName = "basamaljanaby-server",
    [string]$DbName = "basamaljanaby-db",
    [string]$Domain = "basamaljanaby.com"
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AWS Lightsail Deployment - basamaljanaby" -ForegroundColor Cyan
Write-Host "  Cost: ~`$25-30/month" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check AWS CLI
Write-Host "[1/7] Checking AWS CLI..." -ForegroundColor Yellow
try {
    aws --version | Out-Null
    Write-Host "  ✓ AWS CLI installed" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ AWS CLI not found. Install from: https://aws.amazon.com/cli/" -ForegroundColor Red
    exit 1
}

# Create Lightsail Instance
Write-Host ""
Write-Host "[2/7] Creating Lightsail Instance (`$10/month)..." -ForegroundColor Yellow
$UserData = @"
#!/bin/bash
# Update system
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-`$(uname -s)-`$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Nginx
apt-get install -y nginx certbot python3-certbot-nginx

# Clone repository
cd /home/ubuntu
git clone https://github.com/aliabbas19/test.git app
chown -R ubuntu:ubuntu app

# Create .env file placeholder
echo "DATABASE_URL=postgresql://basamaljanaby:CHANGE_ME@DB_ENDPOINT:5432/basamaljanaby" > /home/ubuntu/app/backend/.env
echo "SECRET_KEY=CHANGE_THIS_SECRET_KEY" >> /home/ubuntu/app/backend/.env
echo "DEBUG=false" >> /home/ubuntu/app/backend/.env
echo "BACKEND_URL=https://api.basamaljanaby.com" >> /home/ubuntu/app/backend/.env

echo "Setup complete! Configure .env and run docker-compose up -d"
"@

$UserDataBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($UserData))

try {
    aws lightsail create-instances `
        --instance-names $InstanceName `
        --availability-zone "${Region}a" `
        --blueprint-id ubuntu_22_04 `
        --bundle-id small_2_0 `
        --user-data $UserDataBase64 `
        --region $Region
    Write-Host "  ✓ Instance created" -ForegroundColor Green
}
catch {
    Write-Host "  ! Instance may already exist, continuing..." -ForegroundColor Yellow
}

# Create Database
Write-Host ""
Write-Host "[3/7] Creating Lightsail Database (`$15/month)..." -ForegroundColor Yellow
try {
    aws lightsail create-relational-database `
        --relational-database-name $DbName `
        --availability-zone "${Region}a" `
        --relational-database-blueprint-id postgres_15 `
        --relational-database-bundle-id micro_2_0 `
        --master-database-name basamaljanaby `
        --master-username basamaljanaby `
        --master-user-password "ChangeThisPassword123!" `
        --region $Region
    Write-Host "  ✓ Database created" -ForegroundColor Green
}
catch {
    Write-Host "  ! Database may already exist, continuing..." -ForegroundColor Yellow
}

# Open Ports
Write-Host ""
Write-Host "[4/7] Opening firewall ports..." -ForegroundColor Yellow
aws lightsail open-instance-public-ports `
    --instance-name $InstanceName `
    --port-info fromPort=80, toPort=80, protocol=tcp `
    --region $Region 2>$null

aws lightsail open-instance-public-ports `
    --instance-name $InstanceName `
    --port-info fromPort=443, toPort=443, protocol=tcp `
    --region $Region 2>$null

aws lightsail open-instance-public-ports `
    --instance-name $InstanceName `
    --port-info fromPort=8000, toPort=8000, protocol=tcp `
    --region $Region 2>$null

Write-Host "  ✓ Ports 80, 443, 8000 opened" -ForegroundColor Green

# Allocate Static IP
Write-Host ""
Write-Host "[5/7] Allocating static IP..." -ForegroundColor Yellow
try {
    aws lightsail allocate-static-ip `
        --static-ip-name "${InstanceName}-ip" `
        --region $Region
    
    aws lightsail attach-static-ip `
        --static-ip-name "${InstanceName}-ip" `
        --instance-name $InstanceName `
        --region $Region
    Write-Host "  ✓ Static IP allocated and attached" -ForegroundColor Green
}
catch {
    Write-Host "  ! Static IP may already exist" -ForegroundColor Yellow
}

# Get Instance Info
Write-Host ""
Write-Host "[6/7] Getting instance information..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
$Instance = aws lightsail get-instance --instance-name $InstanceName --region $Region | ConvertFrom-Json
$PublicIP = $Instance.instance.publicIpAddress

Write-Host "  ✓ Public IP: $PublicIP" -ForegroundColor Green

# Get Database Info
Write-Host ""
Write-Host "[7/7] Getting database information..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
try {
    $DB = aws lightsail get-relational-database --relational-database-name $DbName --region $Region | ConvertFrom-Json
    $DbEndpoint = $DB.relationalDatabase.masterEndpoint.address
    Write-Host "  ✓ Database Endpoint: $DbEndpoint" -ForegroundColor Green
}
catch {
    Write-Host "  ! Database still creating, check later" -ForegroundColor Yellow
    $DbEndpoint = "PENDING"
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  ✓ LIGHTSAIL DEPLOYMENT INITIATED!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Instance IP: $PublicIP" -ForegroundColor Cyan
Write-Host "Database: $DbEndpoint" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Wait 5-10 minutes for instance to be ready"
Write-Host "2. Add DNS records in GoDaddy:"
Write-Host "   - A record: @ -> $PublicIP"
Write-Host "   - A record: api -> $PublicIP"
Write-Host "   - A record: www -> $PublicIP"
Write-Host ""
Write-Host "3. SSH into instance:"
Write-Host "   ssh ubuntu@$PublicIP"
Write-Host ""
Write-Host "4. Configure and start the app:"
Write-Host "   cd ~/app && docker-compose up -d"
Write-Host ""
Write-Host "5. Setup SSL (free):"
Write-Host "   sudo certbot --nginx -d basamaljanaby.com -d api.basamaljanaby.com"
Write-Host ""
