# API Documentation

## Base URL

- **Development**: http://localhost:8000
- **Production**: https://api.basamaljanaby.com

## Authentication

جميع الـ endpoints (ما عدا `/api/auth/login`) تتطلب JWT token في Header:

```
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### POST /api/auth/login
تسجيل الدخول

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response**:
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

#### POST /api/auth/refresh
تحديث Access Token

**Request Body**:
```json
{
  "refresh_token": "string"
}
```

**Response**: نفس `/api/auth/login`

#### POST /api/auth/logout
تسجيل الخروج

**Response**:
```json
{
  "message": "Logged out successfully"
}
```

### Videos

#### GET /api/videos
الحصول على قائمة الفيديوهات

**Query Parameters**:
- `class_name` (optional): فلترة حسب الصف
- `section_name` (optional): فلترة حسب الشعبة
- `video_type` (optional): 'منهجي' أو 'اثرائي'
- `is_archived` (optional): true/false

**Response**:
```json
[
  {
    "id": 1,
    "title": "string",
    "filepath": "string",
    "file_url": "string",
    "user_id": 1,
    "timestamp": "2024-01-01T00:00:00",
    "video_type": "منهجي",
    "is_approved": true,
    "is_archived": false
  }
]
```

#### GET /api/videos/{video_id}
الحصول على فيديو محدد

#### POST /api/videos/{video_id}/like
إعجاب/إلغاء إعجاب

**Response**:
```json
{
  "status": "success",
  "likes_count": 10,
  "user_likes": true
}
```

#### POST /api/videos/{video_id}/approve
موافقة على فيديو (Admin only)

#### POST /api/videos/{video_id}/archive
أرشفة فيديو (Admin only)

#### DELETE /api/videos/{video_id}
حذف فيديو

### Uploads

#### POST /api/uploads/video
رفع فيديو

**Request**: `multipart/form-data`
- `title`: string
- `video_type`: 'منهجي' أو 'اثرائي'
- `video_file`: file

**Response**:
```json
{
  "status": "success",
  "message": "Video uploaded successfully (45s)",
  "video_id": 1,
  "is_approved": false
}
```

#### POST /api/uploads/profile-image
رفع صورة شخصية

**Request**: `multipart/form-data`
- `image_file`: file

**Response**:
```json
{
  "status": "success",
  "message": "Profile image uploaded successfully",
  "file_url": "string",
  "s3_key": "string"
}
```

### Health Check

#### GET /health
فحص صحة الخدمة

**Response**:
```json
{
  "status": "healthy"
}
```

## Error Responses

جميع الأخطاء تتبع هذا الشكل:

```json
{
  "detail": "Error message"
}
```

**Status Codes**:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

## Swagger UI

للوصول إلى Swagger UI التفاعلي:
- **Development**: http://localhost:8000/docs
- **Production**: https://api.basamaljanaby.com/docs

## Rate Limiting

- **Limit**: 100 requests/minute per IP
- **Headers**: 
  - `X-RateLimit-Limit`: الحد الأقصى
  - `X-RateLimit-Remaining`: المتبقي
  - `X-RateLimit-Reset`: وقت إعادة التعيين

## File Upload Limits

- **Videos**: 
  - Max size: 200MB
  - Allowed: mp4, mov, avi
  - Duration: 60s (منهجي), 240s (اثرائي)
- **Images**: 
  - Max size: 5MB
  - Allowed: png, jpg, jpeg, gif

