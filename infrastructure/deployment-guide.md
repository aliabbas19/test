# دليل النشر الكامل - AWS VPC

## المتطلبات الأساسية

1. AWS CLI مُثبت ومُكوّن
2. Terraform مُثبت
3. Docker مُثبت
4. حساب AWS مع صلاحيات كافية

## الخطوات

### 1. إعداد AWS CLI

```bash
aws configure
# أدخل:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: me-south-1
# - Default output format: json
```

### 2. إنشاء ECR Repository

```bash
aws ecr create-repository \
  --repository-name basamaljanaby-backend \
  --region me-south-1
```

### 3. بناء وصورة Docker

```bash
cd backend
docker build -t basamaljanaby-backend .
```

### 4. رفع الصورة إلى ECR

```bash
# الحصول على token
aws ecr get-login-password --region me-south-1 | \
  docker login --username AWS --password-stdin \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.me-south-1.amazonaws.com

# Tag الصورة
docker tag basamaljanaby-backend:latest \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.me-south-1.amazonaws.com/basamaljanaby-backend:latest

# رفع الصورة
docker push \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.me-south-1.amazonaws.com/basamaljanaby-backend:latest
```

### 5. إعداد Terraform

```bash
cd infrastructure

# إنشاء ملف terraform.tfvars
cat > terraform.tfvars << EOF
ecr_repository_url = "$(aws sts get-caller-identity --query Account --output text).dkr.ecr.me-south-1.amazonaws.com/basamaljanaby-backend"
db_password = "YOUR_SECURE_PASSWORD"
secret_key = "YOUR_SECRET_KEY"
EOF

# Initialize
terraform init

# Plan
terraform plan

# Apply
terraform apply
```

### 6. إعداد قاعدة البيانات

```bash
# بعد إنشاء RDS، قم بتشغيل migrations
export DATABASE_URL="postgresql://basamaljanaby:YOUR_PASSWORD@RDS_ENDPOINT:5432/basamaljanaby"

cd backend
alembic upgrade head
```

### 7. ترحيل البيانات من SQLite

```bash
export SQLITE_DB_PATH="/path/to/school_platform.db"
python scripts/migrate_sqlite_to_postgres.py
```

### 8. إعداد Route53

1. اذهب إلى Route53 Console
2. أنشئ Hosted Zone لـ basamaljanaby.com (إذا لم تكن موجودة)
3. Terraform سيقوم بإنشاء السجلات تلقائياً

### 9. إعداد SSL Certificate (ACM)

```bash
# طلب شهادة SSL
aws acm request-certificate \
  --domain-name basamaljanaby.com \
  --subject-alternative-names "*.basamaljanaby.com" \
  --validation-method DNS \
  --region us-east-1  # CloudFront requires certificates in us-east-1
```

### 10. تحديث ECS Service

```bash
aws ecs update-service \
  --cluster basamaljanaby-cluster \
  --service basamaljanaby-backend-service \
  --force-new-deployment \
  --region me-south-1
```

## التحقق من النشر

1. تحقق من صحة ECS Service:
```bash
aws ecs describe-services \
  --cluster basamaljanaby-cluster \
  --services basamaljanaby-backend-service \
  --region me-south-1
```

2. تحقق من ALB Health:
```bash
aws elbv2 describe-target-health \
  --target-group-arn $(terraform output -raw target_group_arn) \
  --region me-south-1
```

3. اختبر API:
```bash
curl http://api.basamaljanaby.com/health
```

## التكلفة المتوقعة

- ECS Fargate: ~$10/month
- RDS db.t3.micro: ~$15/month
- ALB: ~$2/month
- NAT Gateway: ~$5/month
- S3: ~$1/month
- CloudFront: ~$1/month
- Route53: ~$0.50/month
- **Total: ~$34/month**

## ملاحظات مهمة

1. استخدم AWS Secrets Manager للأسرار الحساسة
2. فعّل CloudWatch Logs للمراقبة
3. أنشئ نسخ احتياطية منتظمة لـ RDS
4. راقب التكلفة باستخدام AWS Cost Explorer

