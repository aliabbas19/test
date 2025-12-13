# إعداد الدومين basamaljanaby.com مع AWS

## الخطوة 1: إنشاء شهادة SSL في AWS Certificate Manager

```bash
# في منطقة us-east-1 (مطلوب لـ CloudFront)
aws acm request-certificate \
  --domain-name basamaljanaby.com \
  --subject-alternative-names "*.basamaljanaby.com" \
  --validation-method DNS \
  --region us-east-1
```

## الخطوة 2: إضافة سجلات DNS في GoDaddy

### للتحقق من ملكية الدومين (SSL):
1. افتح AWS Console → Certificate Manager
2. انسخ CNAME Name و CNAME Value
3. أضفهم في GoDaddy DNS

### بعد النشر، أضف هذه السجلات في GoDaddy:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | (CloudFront IP) | 600 |
| CNAME | www | dxxxxxxxxxx.cloudfront.net | 600 |
| CNAME | api | basamaljanaby-alb-xxxxx.me-south-1.elb.amazonaws.com | 600 |

## الخطوة 3: تحديث terraform.tfvars

```hcl
domain_name = "basamaljanaby.com"
certificate_arn = "arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/xxxxx"
```

## الخطوة 4: تشغيل النشر

```powershell
.\deploy-aws.ps1 -AwsAccountId "YOUR_ACCOUNT_ID" -DbPassword "SECURE_PASSWORD" -SecretKey "SECRET_KEY"
```

## الخطوة 5: تحديث GoDaddy DNS

بعد اكتمال النشر:
1. احصل على CloudFront URL من Terraform output
2. احصل على ALB URL من Terraform output  
3. حدّث سجلات DNS في GoDaddy

## الروابط النهائية:
- **الموقع:** https://basamaljanaby.com
- **API:** https://api.basamaljanaby.com
