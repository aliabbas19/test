# دليل البدء السريع

## التطوير المحلي

### 1. إعداد Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. إعداد قاعدة البيانات

```bash
# باستخدام Docker
docker run -d -p 5432:5432 \
  -e POSTGRES_USER=basamaljanaby \
  -e POSTGRES_PASSWORD=changeme \
  -e POSTGRES_DB=basamaljanaby \
  postgres:15

# أو استخدام docker-compose
docker-compose up postgres -d
```

### 3. إعداد Environment Variables

```bash
cp .env.example .env
# عدّل .env وأضف:
# DATABASE_URL=postgresql://basamaljanaby:changeme@localhost:5432/basamaljanaby
# SECRET_KEY=your-secret-key-here
```

### 4. تشغيل Migrations

```bash
cd backend
alembic upgrade head
```

### 5. تشغيل Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. إعداد Frontend

```bash
cd frontend
npm install
npm run dev
```

### 7. الوصول للتطبيق

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## استخدام Docker Compose

```bash
docker-compose up
```

سيقوم بـ:
- تشغيل PostgreSQL
- تشغيل Backend على المنفذ 8000
- تشغيل Frontend على المنفذ 5173

## الحساب الافتراضي

بعد تشغيل migrations، سيتم إنشاء حساب admin افتراضي:
- Username: `admin`
- Password: `admin123`

**⚠️ غيّر كلمة المرور فوراً في الإنتاج!**

## ترحيل البيانات من SQLite

```bash
export SQLITE_DB_PATH="/path/to/school_platform.db"
export DATABASE_URL="postgresql://basamaljanaby:changeme@localhost:5432/basamaljanaby"
python backend/scripts/migrate_sqlite_to_postgres.py
```

## النشر على AWS

راجع `DEPLOYMENT.md` للتعليمات الكاملة.

## استكشاف الأخطاء

### Backend لا يبدأ
- تحقق من DATABASE_URL في .env
- تأكد من تشغيل PostgreSQL
- تحقق من المنفذ 8000

### Frontend لا يتصل بالـ API
- تحقق من VITE_API_URL في .env
- تأكد من تشغيل Backend
- تحقق من CORS settings

### قاعدة البيانات
- تحقق من اتصال PostgreSQL
- شغّل `alembic upgrade head`
- تحقق من السجلات

