# AWS EC2 Deployment Script - Simple Version
# Run: .\deploy-ec2.ps1

$Region = "eu-central-1"
$InstanceName = "basamaljanaby-server"
$KeyPairName = "basamaljanaby-key"
$SecurityGroupName = "basamaljanaby-sg"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AWS EC2 Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Create Key Pair
Write-Host "`n[1/5] Creating Key Pair..." -ForegroundColor Yellow
$keyResult = aws ec2 create-key-pair --key-name $KeyPairName --query 'KeyMaterial' --output text --region $Region 2>$null
if ($keyResult) {
    $keyResult | Out-File -Encoding ascii "$KeyPairName.pem"
    Write-Host "  Created: $KeyPairName.pem" -ForegroundColor Green
}
else {
    Write-Host "  Key already exists" -ForegroundColor Green
}

# Step 2: Get Default VPC
Write-Host "`n[2/5] Getting VPC..." -ForegroundColor Yellow
$VpcId = aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query "Vpcs[0].VpcId" --output text --region $Region
Write-Host "  VPC: $VpcId" -ForegroundColor Green

# Step 3: Create Security Group
Write-Host "`n[3/5] Creating Security Group..." -ForegroundColor Yellow
$SgId = aws ec2 create-security-group --group-name $SecurityGroupName --description "basamaljanaby" --vpc-id $VpcId --region $Region --query 'GroupId' --output text 2>$null
if (-not $SgId) {
    $SgId = aws ec2 describe-security-groups --group-names $SecurityGroupName --region $Region --query 'SecurityGroups[0].GroupId' --output text
}
Write-Host "  Security Group: $SgId" -ForegroundColor Green

# Add rules
aws ec2 authorize-security-group-ingress --group-id $SgId --protocol tcp --port 22 --cidr 0.0.0.0/0 --region $Region 2>$null
aws ec2 authorize-security-group-ingress --group-id $SgId --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $Region 2>$null
aws ec2 authorize-security-group-ingress --group-id $SgId --protocol tcp --port 443 --cidr 0.0.0.0/0 --region $Region 2>$null
aws ec2 authorize-security-group-ingress --group-id $SgId --protocol tcp --port 8000 --cidr 0.0.0.0/0 --region $Region 2>$null
Write-Host "  Ports opened: 22, 80, 443, 8000" -ForegroundColor Green

# Step 4: Get Ubuntu AMI
Write-Host "`n[4/5] Getting Ubuntu AMI..." -ForegroundColor Yellow
$AmiId = aws ec2 describe-images --owners 099720109477 --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" "Name=state,Values=available" --query "Images | sort_by(@, &CreationDate) | [-1].ImageId" --output text --region $Region
Write-Host "  AMI: $AmiId" -ForegroundColor Green

# Step 5: Launch Instance
Write-Host "`n[5/5] Launching EC2 Instance..." -ForegroundColor Yellow
$InstanceId = aws ec2 run-instances --image-id $AmiId --instance-type t3.small --key-name $KeyPairName --security-group-ids $SgId --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$InstanceName}]" --region $Region --query 'Instances[0].InstanceId' --output text

Write-Host "  Instance: $InstanceId" -ForegroundColor Green
Write-Host "  Waiting for IP..." -ForegroundColor Yellow

Start-Sleep -Seconds 30

$PublicIP = aws ec2 describe-instances --instance-ids $InstanceId --region $Region --query 'Reservations[0].Instances[0].PublicIpAddress' --output text

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  DONE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "IP: $PublicIP" -ForegroundColor Cyan
Write-Host ""
Write-Host "Add in GoDaddy DNS:" -ForegroundColor Yellow
Write-Host "  A @ -> $PublicIP"
Write-Host "  A api -> $PublicIP"
Write-Host ""
Write-Host "SSH: ssh -i $KeyPairName.pem ubuntu@$PublicIP"
Write-Host ""
