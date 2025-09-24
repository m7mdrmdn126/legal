# Legal Cases Database - Final Schema

## Database Structure Overview

The legal cases database has been successfully created with the following tables:

### 1. **users** 👤
User management table with two types: admin and user
- `id` (Primary Key)
- `username` (Unique)
- `password_hash` (SHA256 hashed password)
- `full_name`
- `user_type` ('admin' or 'user')
- `is_active` (1 for active, 0 for inactive)
- `created_at`, `updated_at`

### 2. **case_types** 📁
Categories of legal cases
- `id` (Primary Key)
- `name` (Case type name - مدني، جنائي، تجاري، etc.)
- `description`
- `created_at`, `updated_at`

### 3. **cases** ⚖️
Main cases table (legal cases)
- `id` (Primary Key)
- `case_number` (رقم القضيه - Unique)
- `plaintiff` (المدعي)
- `defendant` (المدعي عليه)
- `case_type_id` (Foreign Key to case_types)
- `judgment_type` (الحكم: 'حكم اول' / 'حكم ثان' / 'حكم ثالث')
- `previous_judgment_id` (Foreign Key to cases - for حكم ثان/ثالث)
- `created_at`, `updated_at`

### 4. **case_sessions** 📅
Sessions and follow-ups (ميعاد الجلسه / المتابعة)
- `id` (Primary Key)
- `case_id` (Foreign Key to cases)
- `session_date` (ميعاد الجلسه)
- `session_notes` (المتابعة - text notes)
- `created_at`, `updated_at`

### 5. **case_notes** 📝
Notes and observations (الملاحظات)
- `id` (Primary Key)
- `case_id` (Foreign Key to cases)
- `note_text` (الملاحظات)
- `created_at`, `updated_at`

## Default Data Inserted

### Case Types:
- مدني (Civil cases)
- جنائي (Criminal cases)
- تجاري (Commercial cases)
- عمالي (Labor cases)
- أحوال شخصية (Personal status cases)
- إداري (Administrative cases)

### Default Admin User:
- **Username:** admin
- **Password:** admin123 (should be changed in production)
- **Full Name:** System Administrator
- **Type:** admin

## Database Features

✅ **Foreign Key Constraints** enabled
✅ **Indexes** created for performance optimization
✅ **Check constraints** for data validation
✅ **Automatic timestamps** (created_at, updated_at)
✅ **Cascade deletes** for related data
✅ **Password hashing** (SHA256)

## Files Created

1. **`schema.py`** - Database schema creation script
2. **`db_utils.py`** - Database utility class with CRUD operations
3. **`legal_cases.db`** - SQLite database file
4. **`README.md`** - This documentation file

## Usage

```python
from db_utils import LegalCasesDB

# Initialize database
db = LegalCasesDB("legal_cases.db")

# User authentication
user = db.authenticate_user("admin", "admin123")

# Get case types
case_types = db.get_case_types()

# Add a new case
case_id = db.add_case(
    case_number="2025/001",
    plaintiff="أحمد محمد",
    defendant="شركة المقاولات المصرية",
    case_type_id=1,  # مدني
    judgment_type="حكم اول"
)

# Add session
db.add_case_session(case_id, "2025-01-15 10:00:00", "الجلسة الأولى")

# Add note
db.add_case_note(case_id, "تم تقديم المستندات المطلوبة")
```

## Security Notes

⚠️ **Important**: Change the default admin password in production
🔒 Passwords are hashed using SHA256
🔑 Consider implementing more robust authentication (JWT tokens, etc.)
📊 Database includes proper indexing for performance

The database is now ready for use in your legal cases management application!
