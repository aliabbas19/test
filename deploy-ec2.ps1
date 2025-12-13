# AWS EC2 Deployment Script
# Cost: ~$10-25/month (t3.small)
# Run: .\deploy-ec2.ps1

$ErrorActionPreference = "Stop"
$Region = "eu-central-1"
$InstanceName = "basamaljanaby-server"
$KeyPairName = "basamaljanaby-key"
$SecurityGroupName = "basamaljanaby-sg"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AWS EC2 Deployment - basamaljanaby" -ForegroundColor Cyan
Write-Host "  Cost: ~10-25 USD/month" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check AWS CLI
Write-Host "[1/6] Checking AWS CLI..." -ForegroundColor Yellow
aws sts get-caller-identity | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: AWS CLI configured" -ForegroundColor Green
}
else {
    Write-Host "  ERROR: AWS CLI not configured" -ForegroundColor Red
    exit 1
}

# Create Key Pair
Write-Host ""
Write-Host "[2/6] Creating SSH Key Pair..." -ForegroundColor Yellow
$KeyExists = aws ec2 describe-key-pairs --key-names $KeyPairName --region $Region 2>&1
if ($LASTEXITCODE -ne 0) {
    aws ec2 create-key-pair --key-name $KeyPairName --query 'KeyMaterial' --output text --region $Region | Out-File -Encoding ascii "$KeyPairName.pem"
    Write-Host "  OK: Key pair created and saved to $KeyPairName.pem" -ForegroundColor Green
    Write-Host "  IMPORTANT: Keep this file safe!" -ForegroundColor Yellow
}
else {
    Write-Host "  OK: Key pair already exists" -ForegroundColor Green
}

# Create Security Group
Write-Host ""
Write-Host "[3/6] Creating Security Group..." -ForegroundColor Yellow
$VpcId = aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query "Vpcs[0].VpcId" --output text --region $Region
$SgExists = aws ec2 describe-security-groups --group-names $SecurityGroupName --region $Region 2>&1
if ($LASTEXITCODE -ne 0) {
    $SgId = aws ec2 create-security-group --group-name $SecurityGroupName --description "Security group for basamaljanaby" --vpc-id $VpcId --region $Region --query 'GroupId' --output text
    
    # Allow SSH
    aws ec2 authorize-security-group-ingress --group-id $SgId --protocol tcp --port 22 --cidr 0.0.0.0/0 --region $Region | Out-Null
    # Allow HTTP
    aws ec2 authorize-security-group-ingress --group-id $SgId --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $Region | Out-Null
    # Allow HTTPS
    aws ec2 authorize-security-group-ingress --group-id $SgId --protocol tcp --port 443 --cidr 0.0.0.0/0 --region $Region | Out-Null
    # Allow Backend
    aws ec2 authorize-security-group-ingress --group-id $SgId --protocol tcp --port 8000 --cidr 0.0.0.0/0 --region $Region | Out-Null
    
    Write-Host "  OK: Security group created with ports 22, 80, 443, 8000" -ForegroundColor Green
}
else {
    $SgId = aws ec2 describe-security-groups --group-names $SecurityGroupName --region $Region --query 'SecurityGroups[0].GroupId' --output text
    Write-Host "  OK: Security group already exists" -ForegroundColor Green
}

# Get Ubuntu AMI
Write-Host ""
Write-Host "[4/6] Getting Ubuntu 22.04 AMI..." -ForegroundColor Yellow
$AmiId = aws ec2 describe-images --owners 099720109477 --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" "Name=state,Values=available" --query "Images | sort_by(@, &CreationDate) | [-1].ImageId" --output text --region $Region
Write-Host "  OK: AMI ID: $AmiId" -ForegroundColor Green

# Launch EC2 Instance
Write-Host ""
Write-Host "[5/6] Launching EC2 Instance (t3.small)..." -ForegroundColor Yellow

$UserData = @'
#!/bin/bash
apt-get update && apt-get upgrade -y
curl -fsSL https://get.docker.com | sh
usermod -aG docker ubuntu
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
apt-get install -y nginx certbot python3-certbot-nginx git
cd /home/ubuntu
git clone https://github.com/aliabbas19/test.git app
chown -R ubuntu:ubuntu app
echo "Setup complete!" > /home/ubuntu/setup-done.txt
'@

$UserDataBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($UserData))

$InstanceId = aws ec2 run-instances `
    --image-id $AmiId `
    --instance-type t3.small `
    --key-name $KeyPairName `
    --security-group-ids $SgId `
    --user-data $UserDataBase64 `
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$InstanceName}]" `
    --region $Region `
    --query 'Instances[0].InstanceId' `
    --output text

Write-Host "  OK: Instance launched: $InstanceId" -ForegroundColor Green

# Wait for instance
Write-Host ""
Write-Host "[6/6] Waiting for instance to be running..." -ForegroundColor Yellow
aws ec2 wait instance-running --instance-ids $InstanceId --region $Region
Write-Host "  OK: Instance is running" -ForegroundColor Green

# Get Public IP
$PublicIP = aws ec2 describe-instances --instance-ids $InstanceId --region $Region --query 'Reservations[0].Instances[0].PublicIpAddress' --output text

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  EC2 DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Instance ID: $InstanceId" -ForegroundColor Cyan
Write-Host "Public IP: $PublicIP" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Add DNS records in GoDaddy:"
Write-Host "   A record: @ -> $PublicIP"
Write-Host "   A record: api -> $PublicIP"
Write-Host "   A record: www -> $PublicIP"
Write-Host ""
Write-Host "2. Wait 5 minutes for setup to complete, then SSH:"
Write-Host "   ssh -i $KeyPairName.pem ubuntu@$PublicIP"
Write-Host ""
Write-Host "3. On the server, configure and start:"
Write-Host "   cd ~/app"
Write-Host "   nano backend/.env  # Add DATABASE_URL, SECRET_KEY"
Write-Host "   docker-compose up -d --build"
Write-Host ""
Write-Host "4. Setup SSL:"
Write-Host "   sudo certbot --nginx -d basamaljanaby.com -d api.basamaljanaby.com"
Write-Host ""
