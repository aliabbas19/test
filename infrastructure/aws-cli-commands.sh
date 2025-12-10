#!/bin/bash
# AWS CLI Commands for Deployment
# Region: me-south-1

set -e

REGION="me-south-1"
PROJECT_NAME="basamaljanaby"

echo "=== AWS Deployment Commands ==="

# 1. Create ECR Repository
echo "1. Creating ECR repository..."
aws ecr create-repository \
  --repository-name ${PROJECT_NAME}-backend \
  --region ${REGION} \
  --image-scanning-configuration scanOnPush=true

# 2. Get ECR Login Token
echo "2. Getting ECR login token..."
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.${REGION}.amazonaws.com

# 3. Build and Push Docker Image
echo "3. Building and pushing Docker image..."
ECR_REPO=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.${REGION}.amazonaws.com/${PROJECT_NAME}-backend

cd backend
docker build -t ${PROJECT_NAME}-backend .
docker tag ${PROJECT_NAME}-backend:latest ${ECR_REPO}:latest
docker push ${ECR_REPO}:latest
cd ..

# 4. Initialize Terraform
echo "4. Initializing Terraform..."
cd infrastructure
terraform init

# 5. Plan Terraform
echo "5. Planning Terraform changes..."
terraform plan \
  -var="ecr_repository_url=${ECR_REPO}" \
  -var="db_password=YOUR_DB_PASSWORD" \
  -var="secret_key=YOUR_SECRET_KEY"

# 6. Apply Terraform
echo "6. Applying Terraform changes..."
terraform apply \
  -var="ecr_repository_url=${ECR_REPO}" \
  -var="db_password=YOUR_DB_PASSWORD" \
  -var="secret_key=YOUR_SECRET_KEY" \
  -auto-approve

# 7. Update ECS Service
echo "7. Updating ECS service..."
aws ecs update-service \
  --cluster ${PROJECT_NAME}-cluster \
  --service ${PROJECT_NAME}-backend-service \
  --force-new-deployment \
  --region ${REGION}

echo "=== Deployment Complete ==="

