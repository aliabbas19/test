# خطة النشر الكاملة

## نظرة عامة

هذا المشروع منصة تعليمية كاملة تعمل على AWS داخل VPC واحدة.

## البنية

- **Backend**: FastAPI على ECS Fargate
- **Frontend**: React + Vite على CloudFront
- **Database**: PostgreSQL على RDS
- **Storage**: S3 + CloudFront
- **Region**: me-south-1 (Bahrain)

## خطوات النشر

### المرحلة 1: الإعداد المحلي

1. **استنساخ المشروع**
```bash
git clone https://github.com/aliabbas19/test.git
cd test
```

2. **إعداد Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **إعداد Frontend**
```bash
cd frontend
npm install
```

4. **اختبار محلي**
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: PostgreSQL (Docker)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=changeme postgres:15
```

### المرحلة 2: إعداد AWS

1. **إنشاء ECR Repository**
```bash
aws ecr create-repository --repository-name basamaljanaby-backend --region me-south-1
```

2. **بناء وصورة Docker**
```bash
cd backend
docker build -t basamaljanaby-backend .
```

3. **رفع الصورة**
```bash
# Login to ECR
aws ecr get-login-password --region me-south-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.me-south-1.amazonaws.com

# Tag and push
docker tag basamaljanaby-backend:latest ACCOUNT_ID.dkr.ecr.me-south-1.amazonaws.com/basamaljanaby-backend:latest
docker push ACCOUNT_ID.dkr.ecr.me-south-1.amazonaws.com/basamaljanaby-backend:latest
```

### المرحلة 3: نشر Infrastructure

1. **إعداد Terraform**
```bash
cd infrastructure
terraform init
```

2. **إنشاء terraform.tfvars**
```hcl
ecr_repository_url = "ACCOUNT_ID.dkr.ecr.me-south-1.amazonaws.com/basamaljanaby-backend"
db_password = "YOUR_SECURE_PASSWORD"
secret_key = "YOUR_SECRET_KEY"
```

3. **نشر Infrastructure**
```bash
terraform plan
terraform apply
```

### المرحلة 4: إعداد قاعدة البيانات

1. **تشغيل Migrations**
```bash
export DATABASE_URL="postgresql://basamaljanaby:PASSWORD@RDS_ENDPOINT:5432/basamaljanaby"
cd backend
alembic upgrade head
```

2. **ترحيل البيانات من SQLite**
```bash
export SQLITE_DB_PATH="/path/to/school_platform.db"
python scripts/migrate_sqlite_to_postgres.py
```

### المرحلة 5: نشر Frontend

1. **بناء Frontend**
```bash
cd frontend
npm run build
```

2. **رفع إلى S3**
```bash
aws s3 sync dist/ s3://basamaljanaby-media/frontend/ --delete
```

3. **تحديث CloudFront**
```bash
aws cloudfront create-invalidation --distribution-id DISTRIBUTION_ID --paths "/*"
```

## التحقق من النشر

1. **اختبار Backend**
```bash
curl https://api.basamaljanaby.com/health
```

2. **اختبار Frontend**
افتح المتصفح: https://basamaljanaby.com

3. **مراقبة Logs**
```bash
aws logs tail /ecs/basamaljanaby-backend --follow --region me-south-1
```

## الصيانة

### تحديث Backend
```bash
# Build new image
docker build -t basamaljanaby-backend .
docker push ACCOUNT_ID.dkr.ecr.me-south-1.amazonaws.com/basamaljanaby-backend:latest

# Force new deployment
aws ecs update-service --cluster basamaljanaby-cluster --service basamaljanaby-backend-service --force-new-deployment
```

### نسخ احتياطي قاعدة البيانات
```bash
aws rds create-db-snapshot --db-instance-identifier basamaljanaby-db --db-snapshot-identifier backup-$(date +%Y%m%d)
```

## استكشاف الأخطاء

1. **ECS Tasks لا تبدأ**
   - تحقق من Security Groups
   - تحقق من IAM Roles
   - راجع CloudWatch Logs

2. **قاعدة البيانات غير متاحة**
   - تحقق من Security Group rules
   - تحقق من Subnet Group
   - تحقق من RDS Status

3. **Frontend لا يظهر**
   - تحقق من S3 bucket permissions
   - تحقق من CloudFront distribution
   - تحقق من Route53 records

## الأمان

1. استخدم AWS Secrets Manager للأسرار
2. فعّل MFA على حساب AWS
3. استخدم IAM Roles بدلاً من Access Keys
4. فعّل CloudTrail للمراقبة
5. استخدم WAF على ALB

