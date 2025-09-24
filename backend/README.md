# Legal Cases Management System - Backend API

نظام إدارة القضايا القانونية - الخادم الخلفي

## Overview المقدمة

This is a comprehensive FastAPI-based backend system for managing legal cases, built with Arabic language support and advanced search capabilities.

هذا نظام شامل مبني على FastAPI لإدارة القضايا القانونية، مع دعم كامل للغة العربية وإمكانيات بحث متقدمة.

## Features الميزات

### 🔐 Authentication & Authorization
- JWT-based authentication with 12-hour token expiration
- Role-based access control (Admin/User)
- Secure password hashing with bcrypt
- Protected endpoints with proper permission levels

### 🏛️ Legal Case Management
- Complete CRUD operations for cases
- Case types management
- Session tracking (court sessions)
- Notes and observations system
- Previous judgment references
- Arabic judgment types support (حكم اول، حكم ثان، حكم ثالث)

### 🔍 Advanced Arabic Search
- Comprehensive Arabic text normalization
- Character variations handling (ه/ة, ي/ى, أ/إ/آ/ا)
- Diacritics removal (تشكيل)
- Case-insensitive search across all relevant fields

### 👥 User Management
- User creation and management (Admin only)
- User activation/deactivation
- Password management
- Audit trail for all operations

### 📊 Statistics & Reports
- Dashboard statistics
- Cases by type and judgment analysis
- User activity tracking
- Monthly trend reports
- Upcoming sessions tracking

### 🚀 Technical Features
- RESTful API design
- Comprehensive pagination (40 items per page)
- Proper error handling with Arabic messages
- CORS support for frontend integration
- Auto-generated API documentation
- Request/response validation
- Database audit trail

## Quick Start البدء السريع

### Prerequisites المتطلبات

- Python 3.8+
- SQLite3
- Virtual environment (recommended)

### Installation التثبيت

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   ```

4. **Ensure database exists:**
   ```bash
   cd ../database
   python schema.py
   cd ../backend
   ```

5. **Start the server:**
   ```bash
   ./start.sh
   # OR
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Default Access الدخول الافتراضي

- **Server:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Redoc Documentation:** http://localhost:8000/redoc

**Default Admin Login:**
- Username: `admin`
- Password: `admin123`

## API Endpoints نقاط النهاية

### Authentication المصادقة
```
POST /api/v1/auth/login          # User login
POST /api/v1/auth/logout         # User logout
POST /api/v1/auth/refresh        # Token refresh (placeholder)
```

### Users إدارة المستخدمين (Admin Only)
```
GET    /api/v1/users             # List users
POST   /api/v1/users             # Create user
GET    /api/v1/users/{id}        # Get user
PUT    /api/v1/users/{id}        # Update user
DELETE /api/v1/users/{id}        # Delete user
POST   /api/v1/users/{id}/activate   # Activate user
POST   /api/v1/users/{id}/deactivate # Deactivate user
PUT    /api/v1/users/{id}/password   # Change password
```

### Case Types أنواع القضايا
```
GET    /api/v1/case-types        # List case types
POST   /api/v1/case-types        # Create case type
GET    /api/v1/case-types/{id}   # Get case type
PUT    /api/v1/case-types/{id}   # Update case type
DELETE /api/v1/case-types/{id}   # Delete case type (Admin only)
```

### Cases القضايا
```
GET    /api/v1/cases             # List cases (with filters)
POST   /api/v1/cases             # Create case
GET    /api/v1/cases/{id}        # Get case
PUT    /api/v1/cases/{id}        # Update case
DELETE /api/v1/cases/{id}        # Delete case (Admin only)
GET    /api/v1/cases/{id}/full   # Get case with details
GET    /api/v1/cases/by-type/{type_id} # Cases by type
```

### Case Sessions جلسات القضايا
```
GET    /api/v1/cases/{case_id}/sessions     # List case sessions
POST   /api/v1/cases/{case_id}/sessions     # Create session
GET    /api/v1/case-sessions/{id}           # Get session
PUT    /api/v1/case-sessions/{id}           # Update session
DELETE /api/v1/case-sessions/{id}           # Delete session (Admin only)
```

### Case Notes ملاحظات القضايا
```
GET    /api/v1/cases/{case_id}/notes        # List case notes
POST   /api/v1/cases/{case_id}/notes        # Create note
GET    /api/v1/case-notes/{id}              # Get note
PUT    /api/v1/case-notes/{id}              # Update note
DELETE /api/v1/case-notes/{id}              # Delete note (Admin only)
```

### Statistics الإحصائيات
```
GET    /api/v1/stats/dashboard              # Dashboard stats
GET    /api/v1/stats/cases-by-type          # Cases by type
GET    /api/v1/stats/cases-by-judgment      # Cases by judgment
GET    /api/v1/stats/user-activity          # User activity
```

## Query Parameters معاملات الاستعلام

### Pagination التصفح
- `page`: Page number (default: 1)
- `size`: Items per page (default: 40, max: 100)

### Search البحث
- `search`: Arabic-aware search term
- Searches across relevant fields with normalization

### Filtering التصفية
- `case_type_id`: Filter by case type
- `judgment_type`: Filter by judgment type (حكم_اول, حكم_ثان, حكم_ثالث)

### Example أمثلة:
```
GET /api/v1/cases?page=1&size=20&search=أحمد&case_type_id=1
GET /api/v1/cases?judgment_type=حكم_اول
GET /api/v1/users?page=2&size=10&search=محمد
```

## Request/Response Examples أمثلة الطلبات والردود

### Login Request طلب تسجيل الدخول
```json
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

### Login Response رد تسجيل الدخول
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 43200,
  "user": {
    "id": 1,
    "username": "admin",
    "full_name": "مدير النظام",
    "user_type": "admin",
    "is_active": true,
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z"
  }
}
```

### Create Case Request إنشاء قضية جديدة
```json
POST /api/v1/cases
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "case_number": "2025/001",
  "plaintiff": "أحمد محمد علي",
  "defendant": "شركة المقاولات المصرية",
  "case_type_id": 1,
  "judgment_type": "حكم اول",
  "previous_judgment_id": null
}
```

### Paginated Response رد مقسم لصفحات
```json
{
  "items": [
    {
      "id": 1,
      "case_number": "2025/001",
      "plaintiff": "أحمد محمد علي",
      "defendant": "شركة المقاولات المصرية",
      "case_type": {
        "id": 1,
        "name": "مدني",
        "description": "قضايا مدنية"
      },
      "judgment_type": "حكم اول",
      "created_at": "2025-01-15T10:00:00Z",
      "created_by": {
        "id": 1,
        "full_name": "مدير النظام"
      }
    }
  ],
  "total": 150,
  "page": 1,
  "size": 40,
  "pages": 4
}
```

## Error Handling معالجة الأخطاء

### Error Response Format تنسيق رد الخطأ
```json
{
  "success": false,
  "detail": "رسالة الخطأ",
  "error_code": "ERROR_CODE",
  "field_errors": {
    "field_name": ["رسالة خطأ الحقل"]
  }
}
```

### Common Error Codes رموز الأخطاء الشائعة
- `VALIDATION_ERROR`: خطأ في البيانات المدخلة
- `HTTP_ERROR`: خطأ HTTP عام
- `INTERNAL_SERVER_ERROR`: خطأ داخلي في الخادم

## Security الأمان

### Authentication المصادقة
- JWT tokens with 12-hour expiration
- Secure password hashing (bcrypt)
- Protected endpoints with role-based access

### Authorization التفويض
- **Admin Users:** Full CRUD access to all resources
- **Regular Users:** Read/Create/Update access (no delete)
- **Public:** Login endpoint only

### Data Validation التحقق من البيانات
- Comprehensive input validation
- Arabic text validation
- SQL injection protection through parameterized queries

## Database Schema مخطط قاعدة البيانات

### Tables الجداول
1. **users** - User management
2. **case_types** - Case categories
3. **cases** - Legal cases
4. **case_sessions** - Court sessions
5. **case_notes** - Case observations

### Audit Trail سجل التدقيق
All tables include:
- `created_by` - User who created the record
- `updated_by` - User who last updated the record
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## Configuration التكوين

### Environment Variables متغيرات البيئة
```bash
# Application
APP_NAME="Legal Cases Management System"
DEBUG=true

# Security
SECRET_KEY="your-secret-key"
ACCESS_TOKEN_EXPIRE_HOURS=12

# Database
DATABASE_PATH="../database/legal_cases.db"

# Pagination
DEFAULT_PAGE_SIZE=40
MAX_PAGE_SIZE=100
```

## Development التطوير

### Project Structure هيكل المشروع
```
backend/
├── main.py                 # FastAPI application
├── requirements.txt        # Dependencies
├── .env                   # Environment variables
├── start.sh               # Startup script
├── config/                # Configuration
│   ├── database.py
│   └── settings.py
├── models/                # Pydantic models
├── routes/                # API endpoints
├── utils/                 # Utilities
├── dependencies/          # FastAPI dependencies
└── middleware/            # Custom middleware
```

### Adding New Features إضافة ميزات جديدة
1. Create Pydantic models in `models/`
2. Add database operations
3. Create API routes in `routes/`
4. Add tests if needed
5. Update documentation

## Deployment النشر

### Production إنتاج
1. Set `DEBUG=false` in `.env`
2. Use a strong `SECRET_KEY`
3. Configure proper CORS origins
4. Use a production WSGI server (e.g., Gunicorn)
5. Set up SSL/HTTPS
6. Configure logging and monitoring

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## API Testing اختبار واجهة برمجة التطبيقات

### Using curl استخدام curl
```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'

# Get cases with token
curl -X GET "http://localhost:8000/api/v1/cases" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### Using Python استخدام Python
```python
import requests

# Login
response = requests.post("http://localhost:8000/api/v1/auth/login", 
                        json={"username": "admin", "password": "admin123"})
token = response.json()["access_token"]

# Get cases
headers = {"Authorization": f"Bearer {token}"}
cases = requests.get("http://localhost:8000/api/v1/cases", headers=headers)
print(cases.json())
```

## Troubleshooting استكشاف الأخطاء

### Common Issues مشاكل شائعة

1. **Database not found**
   ```bash
   cd ../database
   python schema.py
   ```

2. **Import errors**
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

3. **Port already in use**
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

## Support الدعم

For issues and questions:
- Check the API documentation at `/docs`
- Review error messages in Arabic
- Check server logs for detailed error information
- Ensure database schema is up to date

---

## License الترخيص

This project is licensed under the MIT License.

**Built with ❤️ for Arabic legal case management**
