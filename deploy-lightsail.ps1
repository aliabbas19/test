# AWS Lightsail Deployment Script - Fixed Version
# Cost: ~$25-30/month
# Run: .\deploy-lightsail.ps1

$ErrorActionPreference = "Stop"
$Region = "eu-central-1"

$InstanceName = "basamaljanaby-server"
$DbName = "basamaljanaby-db"
$AwsAccountId = "655024857624"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AWS Lightsail Deployment - basamaljanaby" -ForegroundColor Cyan
Write-Host "  Cost: ~25-30 USD/month" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check AWS CLI
Write-Host "[1/7] Checking AWS CLI..." -ForegroundColor Yellow
$awsCheck = aws --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: AWS CLI installed" -ForegroundColor Green
}
else {
    Write-Host "  ERROR: AWS CLI not found" -ForegroundColor Red
    exit 1
}

# Create Lightsail Instance
Write-Host ""
Write-Host "[2/7] Creating Lightsail Instance (10 USD/month)..." -ForegroundColor Yellow

$AvailabilityZone = $Region + "a"

$result = aws lightsail create-instances --instance-names $InstanceName --availability-zone $AvailabilityZone --blueprint-id ubuntu_22_04 --bundle-id small_2_0 --region $Region 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: Instance created" -ForegroundColor Green
}
else {
    Write-Host "  INFO: Instance may already exist, continuing..." -ForegroundColor Yellow
}

# Create Database
Write-Host ""
Write-Host "[3/7] Creating Lightsail Database (15 USD/month)..." -ForegroundColor Yellow

$result = aws lightsail create-relational-database --relational-database-name $DbName --availability-zone $AvailabilityZone --relational-database-blueprint-id postgres_15 --relational-database-bundle-id micro_2_0 --master-database-name basamaljanaby --master-username basamaljanaby --master-user-password "ChangeThisPassword123" --region $Region 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: Database created" -ForegroundColor Green
}
else {
    Write-Host "  INFO: Database may already exist, continuing..." -ForegroundColor Yellow
}

# Open Ports
Write-Host ""
Write-Host "[4/7] Opening firewall ports..." -ForegroundColor Yellow

aws lightsail open-instance-public-ports --instance-name $InstanceName --port-info fromPort=80, toPort=80, protocol=tcp --region $Region 2>&1 | Out-Null
aws lightsail open-instance-public-ports --instance-name $InstanceName --port-info fromPort=443, toPort=443, protocol=tcp --region $Region 2>&1 | Out-Null
aws lightsail open-instance-public-ports --instance-name $InstanceName --port-info fromPort=22, toPort=22, protocol=tcp --region $Region 2>&1 | Out-Null
aws lightsail open-instance-public-ports --instance-name $InstanceName --port-info fromPort=8000, toPort=8000, protocol=tcp --region $Region 2>&1 | Out-Null

Write-Host "  OK: Ports 22, 80, 443, 8000 opened" -ForegroundColor Green

# Allocate Static IP
Write-Host ""
Write-Host "[5/7] Allocating static IP..." -ForegroundColor Yellow

$StaticIpName = $InstanceName + "-ip"
$result = aws lightsail allocate-static-ip --static-ip-name $StaticIpName --region $Region 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: Static IP allocated" -ForegroundColor Green
}
else {
    Write-Host "  INFO: Static IP may already exist" -ForegroundColor Yellow
}

$result = aws lightsail attach-static-ip --static-ip-name $StaticIpName --instance-name $InstanceName --region $Region 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: Static IP attached" -ForegroundColor Green
}

# Wait for instance
Write-Host ""
Write-Host "[6/7] Waiting for instance to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Get Instance Info
$InstanceJson = aws lightsail get-instance --instance-name $InstanceName --region $Region 2>&1
$Instance = $InstanceJson | ConvertFrom-Json
$PublicIP = $Instance.instance.publicIpAddress

if ($PublicIP) {
    Write-Host "  OK: Public IP: $PublicIP" -ForegroundColor Green
}
else {
    Write-Host "  WAIT: Instance still starting, check in a few minutes" -ForegroundColor Yellow
    $PublicIP = "PENDING"
}

# Get Database Info
Write-Host ""
Write-Host "[7/7] Getting database information..." -ForegroundColor Yellow

$DbJson = aws lightsail get-relational-database --relational-database-name $DbName --region $Region 2>&1
if ($LASTEXITCODE -eq 0) {
    $DB = $DbJson | ConvertFrom-Json
    $DbEndpoint = $DB.relationalDatabase.masterEndpoint.address
    $DbPort = $DB.relationalDatabase.masterEndpoint.port
    Write-Host "  OK: Database Endpoint: $DbEndpoint" -ForegroundColor Green
}
else {
    Write-Host "  WAIT: Database still creating, check in 5-10 minutes" -ForegroundColor Yellow
    $DbEndpoint = "PENDING"
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  LIGHTSAIL DEPLOYMENT INITIATED!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Instance IP: $PublicIP" -ForegroundColor Cyan
Write-Host "Database: $DbEndpoint" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Wait 5-10 minutes for everything to be ready"
Write-Host ""
Write-Host "2. Add DNS records in GoDaddy:"
Write-Host "   - A record: @ -> $PublicIP"
Write-Host "   - A record: api -> $PublicIP"
Write-Host "   - A record: www -> $PublicIP"
Write-Host ""
Write-Host "3. Download SSH key from AWS Console:"
Write-Host "   https://lightsail.aws.amazon.com/ls/webapp/account/keys"
Write-Host ""
Write-Host "4. SSH into instance:"
Write-Host "   ssh -i LightsailDefaultKey.pem ubuntu@$PublicIP"
Write-Host ""
Write-Host "5. Run setup commands on server (see setup-server.sh)"
Write-Host ""
