# منصة الأستاذ بسام الجنابي

منصة تعليمية كاملة مع رفع الفيديوهات، التقييم، المحادثات، والإدارة.

## الميزات

- ✅ تسجيل الدخول (JWT)
- ✅ إدارة المستخدمين (Admin/Student)
- ✅ رفع الفيديو (مع التحقق من المدة)
- ✅ التقييم الديناميكي
- ✅ التعليقات
- ✅ البطل الخارق
- ✅ الأرشيف
- ✅ المحادثات
- ✅ الملفات الشخصية
- ✅ التنبيهات

## البنية

- **Backend**: FastAPI + PostgreSQL
- **Frontend**: React + Vite + Tailwind + DaisyUI
- **Infrastructure**: AWS (VPC, ECS, RDS, S3, CloudFront)
- **Region**: me-south-1 (Bahrain)

## البدء السريع

### التطوير المحلي

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Database (Docker)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=changeme postgres:15
```

### استخدام Docker Compose

```bash
docker-compose up
```

## النشر على AWS

راجع [DEPLOYMENT.md](DEPLOYMENT.md) للتعليمات الكاملة.

## التوثيق

- [API Documentation](API_DOCUMENTATION.md)
- [Architecture](ARCHITECTURE.md)
- [Cost Optimization](COST_OPTIMIZATION.md)
- [Deployment Guide](DEPLOYMENT.md)

## الرخصة

MIT

