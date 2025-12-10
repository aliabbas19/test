# تحسين التكلفة - هدف أقل من $25/شهر

## التكلفة الحالية (me-south-1)

| الخدمة | التكلفة الشهرية |
|--------|----------------|
| ECS Fargate (0.25 vCPU, 0.5GB) | ~$10 |
| RDS db.t3.micro | ~$15 |
| ALB | ~$2 |
| NAT Gateway | ~$5 |
| S3 | ~$1 |
| CloudFront | ~$1 |
| Route53 | ~$0.50 |
| **المجموع** | **~$34.50** |

## استراتيجيات التحسين

### 1. استبدال NAT Gateway بـ NAT Instance

**التوفير**: ~$4/شهر

```bash
# استخدام t3.micro instance كـ NAT
# التكلفة: ~$1/شهر بدلاً من ~$5/شهر
```

**الخطوات**:
1. إنشاء EC2 t3.micro instance
2. تعطيل Source/Destination Check
3. تحديث Route Table للـ Private Subnets

### 2. RDS Reserved Instance

**التوفير**: ~$4.50/شهر (30% خصم)

شراء Reserved Instance لمدة سنة واحدة:
- التكلفة العادية: $15/شهر
- مع Reserved: ~$10.50/شهر

### 3. S3 Lifecycle Policies

**التوفير**: ~$0.50/شهر

نقل الملفات القديمة (>90 يوم) إلى Glacier:
- S3 Standard: $0.023/GB
- Glacier: $0.004/GB

### 4. CloudFront Caching

**التوفير**: ~$0.30/شهر

تقليل TTL للكاش:
- تقليل طلبات Origin
- تقليل تكلفة Data Transfer

### 5. ECS Spot Fargate (إذا متاح)

**التوفير**: ~$3/شهر (70% خصم)

استخدام Spot capacity للـ ECS tasks:
- مناسب للتطبيقات التي تتحمل الانقطاع

## التكلفة بعد التحسين

| الخدمة | قبل | بعد |
|--------|-----|-----|
| ECS Fargate | $10 | $7 (Spot) |
| RDS | $15 | $10.50 (Reserved) |
| ALB | $2 | $2 |
| NAT | $5 | $1 (Instance) |
| S3 | $1 | $0.50 (Lifecycle) |
| CloudFront | $1 | $0.70 (Caching) |
| Route53 | $0.50 | $0.50 |
| **المجموع** | **$34.50** | **$22.20** |

## خطوات التنفيذ

### 1. إنشاء NAT Instance

```bash
# Launch t3.micro instance
aws ec2 run-instances \
  --image-id ami-xxxxx \
  --instance-type t3.micro \
  --subnet-id subnet-public-1a \
  --security-group-ids sg-nat \
  --user-data file://nat-instance-setup.sh
```

### 2. شراء RDS Reserved Instance

1. اذهب إلى AWS Console > RDS > Reserved Instances
2. اختر db.t3.micro
3. مدة: 1 year
4. Payment: All Upfront (أكبر خصم)

### 3. إعداد S3 Lifecycle

```bash
aws s3api put-bucket-lifecycle-configuration \
  --bucket basamaljanaby-media \
  --lifecycle-configuration file://lifecycle.json
```

### 4. مراقبة التكلفة

```bash
# استخدام AWS Cost Explorer
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

## نصائح إضافية

1. **إيقاف الموارد غير المستخدمة**: أوقف الموارد ليلاً إذا أمكن
2. **استخدام AWS Budgets**: ضع تنبيهات عند تجاوز الميزانية
3. **مراجعة شهرياً**: راجع التكلفة شهرياً وتحقق من التحسينات
4. **استخدام AWS Cost Anomaly Detection**: للكشف عن التكاليف غير المتوقعة

## الهدف النهائي

**التكلفة المستهدفة**: < $25/شهر ✅

مع التحسينات المذكورة أعلاه، يمكن الوصول إلى **~$22/شهر**.

