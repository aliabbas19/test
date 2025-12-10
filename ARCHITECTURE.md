# مخطط البنية المعمارية

## نظرة عامة

منصة تعليمية كاملة تعمل على AWS داخل VPC واحدة في منطقة me-south-1 (Bahrain).

## البنية المعمارية

```
┌─────────────────────────────────────────────────────────┐
│                    Internet                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     │
        ┌────────────▼────────────┐
        │   Route53 DNS           │
        │  basamaljanaby.com      │
        │  api.basamaljanaby.com  │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   CloudFront            │
        │   (Frontend CDN)        │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   S3 Bucket             │
        │   basamaljanaby-media   │
        │   (Static Files)        │
        └─────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    VPC (10.0.0.0/16)                    │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │  Public Subnet   │      │  Public Subnet    │        │
│  │  10.0.1.0/24     │      │  10.0.2.0/24     │        │
│  │  (AZ-1a)         │      │  (AZ-1b)          │        │
│  │                  │      │                  │        │
│  │  ┌────────────┐  │      │  ┌────────────┐  │        │
│  │  │    ALB    │  │      │  │  NAT GW    │  │        │
│  │  └────────────┘  │      │  └────────────┘  │        │
│  └──────────────────┘      └──────────────────┘        │
│           │                                              │
│  ┌────────▼──────────────────┐                          │
│  │  Internet Gateway          │                          │
│  └────────────────────────────┘                          │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │  Private Subnet  │      │  Private Subnet   │        │
│  │  10.0.11.0/24    │      │  10.0.12.0/24     │        │
│  │  (AZ-1a)         │      │  (AZ-1b)          │        │
│  │                  │      │                  │        │
│  │  ┌────────────┐  │      │  ┌────────────┐  │        │
│  │  │ ECS Tasks │  │      │  │ ECS Tasks  │  │        │
│  │  │ (Backend) │  │      │  │ (Backend)  │  │        │
│  │  └────────────┘  │      │  └────────────┘  │        │
│  │                  │      │                  │        │
│  │  ┌────────────┐  │      │  ┌────────────┐  │        │
│  │  │   RDS     │  │      │  │            │  │        │
│  │  │ PostgreSQL│  │      │  │            │  │        │
│  │  └────────────┘  │      │  └────────────┘  │        │
│  └──────────────────┘      └──────────────────┘        │
└──────────────────────────────────────────────────────────┘
```

## المكونات

### 1. VPC Network
- **CIDR**: 10.0.0.0/16
- **Public Subnets**: 10.0.1.0/24, 10.0.2.0/24
- **Private Subnets**: 10.0.11.0/24, 10.0.12.0/24
- **Internet Gateway**: للوصول من/إلى الإنترنت
- **NAT Gateway**: للوصول إلى الإنترنت من Private Subnets

### 2. Application Load Balancer (ALB)
- **Location**: Public Subnets
- **Purpose**: توزيع الطلبات على ECS Tasks
- **SSL/TLS**: عبر ACM Certificate

### 3. ECS Fargate
- **Service**: Backend API (FastAPI)
- **Location**: Private Subnets
- **Resources**: 0.25 vCPU, 0.5GB RAM
- **Auto Scaling**: بناءً على CPU/Memory

### 4. RDS PostgreSQL
- **Instance**: db.t3.micro
- **Location**: Private Subnets
- **Multi-AZ**: Disabled (لتوفير التكلفة)
- **Backup**: 7 days retention

### 5. S3 Bucket
- **Name**: basamaljanaby-media
- **Purpose**: تخزين الفيديوهات والصور
- **Versioning**: Enabled
- **Lifecycle**: نقل الملفات القديمة إلى Glacier

### 6. CloudFront
- **Purpose**: CDN للوصول إلى S3
- **Caching**: للصور والفيديوهات
- **Signed URLs**: للوصول الآمن

### 7. Route53
- **Hosted Zone**: basamaljanaby.com
- **Records**:
  - basamaljanaby.com → CloudFront
  - api.basamaljanaby.com → ALB

## تدفق البيانات

### 1. طلب Frontend
```
User → Route53 → CloudFront → S3
```

### 2. طلب API
```
User → Route53 → ALB → ECS Task → RDS
```

### 3. رفع ملف
```
User → ALB → ECS Task → S3
```

### 4. الوصول إلى ملف
```
User → CloudFront → S3 (Signed URL)
```

## الأمان

1. **Network Security**:
   - Private Subnets للـ Backend و RDS
   - Security Groups محدودة
   - لا وصول مباشر من الإنترنت

2. **Application Security**:
   - JWT Authentication
   - HTTPS فقط
   - CORS محدود
   - Rate Limiting

3. **Data Security**:
   - Encryption at rest (RDS, S3)
   - Encryption in transit (HTTPS)
   - Signed URLs للوصول إلى الملفات

## المراقبة

1. **CloudWatch Logs**: لـ ECS Tasks
2. **CloudWatch Metrics**: لـ RDS, ECS, ALB
3. **CloudWatch Alarms**: للتنبيهات
4. **AWS Cost Explorer**: لمراقبة التكلفة

## النسخ الاحتياطي

1. **RDS**: Automated backups (7 days)
2. **S3**: Versioning enabled
3. **Manual Snapshots**: قبل التحديثات الكبيرة

## التوسع المستقبلي

1. **Multi-AZ**: لـ RDS (عند الحاجة)
2. **Auto Scaling**: لـ ECS (بناءً على الطلب)
3. **CloudFront**: إضافة المزيد من Edge Locations
4. **Caching**: Redis/ElastiCache للجلسات

