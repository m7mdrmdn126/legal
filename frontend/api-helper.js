/**
 * API HELPER DOCUMENTATION
 * Legal Cases Management System - Frontend Integration Guide
 * 
 * This file contains all endpoint documentation, request/response examples,
 * and integration patterns based on backend routes, models, and testing insights.
 */

// ====================================================================
// BASE CONFIGURATION
// ====================================================================

const API_BASE_URL = 'http://localhost:8000/api';
const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
};

// Auth headers template
const getAuthHeaders = () => ({
  ...DEFAULT_HEADERS,
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`
});

// ====================================================================
// 🔐 AUTHENTICATION ENDPOINTS
// ====================================================================

/**
 * POST /auth/login
 * Purpose: User authentication and token retrieval
 * 
 * Request Body:
 * {
 *   "username": "admin",
 *   "password": "password123"
 * }
 * 
 * Success Response (200):
 * {
 *   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
 *   "token_type": "bearer",
 *   "expires_in": 86400,
 *   "user": {
 *     "id": 1,
 *     "username": "admin", 
 *     "full_name": "مدير النظام",
 *     "user_type": "admin",
 *     "is_active": true,
 *     "created_at": "2024-01-01T00:00:00"
 *   }
 * }
 * 
 * Error Response (401):
 * { "detail": "اسم المستخدم أو كلمة المرور غير صحيحة" }
 */

/**
 * POST /auth/logout  
 * Purpose: User logout (client-side token removal)
 * Headers: Authorization Bearer required
 * 
 * Success Response (200):
 * { "message": "تم تسجيل الخروج بنجاح" }
 */

// ====================================================================
// 👥 USERS ENDPOINTS (ADMIN ONLY)
// ====================================================================

/**
 * GET /users
 * Purpose: Get all users with pagination and search
 * Auth: Admin required
 * 
 * Query Parameters:
 * - page (int, default: 1): Page number
 * - size (int, default: 10, max: 100): Items per page  
 * - search (string, optional): Search in username and full_name
 * 
 * Success Response (200):
 * {
 *   "items": [
 *     {
 *       "id": 1,
 *       "username": "admin",
 *       "full_name": "مدير النظام", 
 *       "user_type": "admin",
 *       "is_active": true,
 *       "created_at": "2024-01-01T00:00:00",
 *       "updated_at": "2024-01-01T00:00:00"
 *     }
 *   ],
 *   "total": 1,
 *   "page": 1,
 *   "size": 10,
 *   "total_pages": 1
 * }
 * 
 * Error Response (403):
 * { "detail": "غير مسموح - مطلوب صلاحيات المدير" }
 */

/**
 * POST /users
 * Purpose: Create new user
 * Auth: Admin required
 * 
 * Request Body:
 * {
 *   "username": "newuser",
 *   "password": "securepassword",
 *   "full_name": "اسم المستخدم الكامل",
 *   "user_type": "user"  // "admin" or "user"
 * }
 * 
 * Error Response (400):
 * { "detail": "اسم المستخدم موجود بالفعل" }
 */

/**
 * GET /users/{user_id}
 * Purpose: Get specific user by ID
 * Auth: Admin required
 * 
 * Error Response (404):
 * { "detail": "المستخدم غير موجود" }
 */

/**
 * PUT /users/{user_id}
 * Purpose: Update user information  
 * Auth: Admin required
 * 
 * Request Body (all fields optional):
 * {
 *   "full_name": "اسم جديد",
 *   "user_type": "admin",
 *   "is_active": false
 * }
 */

/**
 * PUT /users/{user_id}/password
 * Purpose: Update user password
 * Auth: Admin required
 * 
 * Request Body:
 * {
 *   "new_password": "newpassword123"
 * }
 */

// ====================================================================
// 📁 CASE TYPES ENDPOINTS
// ====================================================================

/**
 * GET /case-types
 * Purpose: Get all case types with search
 * Auth: User/Admin required
 * 
 * Query Parameters:
 * - page (int): Page number
 * - size (int): Items per page
 * - search (string): Search in name and description (Arabic supported)
 * 
 * Success Response: Paginated list of case types
 * {
 *   "items": [
 *     {
 *       "id": 1,
 *       "name": "قضايا مدنية",
 *       "description": "القضايا المدنية والتجارية",
 *       "created_by": {"id": 1, "full_name": "مدير النظام"},
 *       "created_at": "2024-01-01T00:00:00"
 *     }
 *   ]
 * }
 */

/**
 * POST /case-types
 * Purpose: Create new case type
 * 
 * Request Body:
 * {
 *   "name": "قضايا تجارية",
 *   "description": "وصف نوع القضية"
 * }
 * 
 * Error Response (400):
 * { "detail": "نوع القضية موجود بالفعل" }
 */

/**
 * PUT /case-types/{case_type_id}
 * DELETE /case-types/{case_type_id}
 * Similar patterns as above
 */

// ====================================================================
// ⚖️ CASES ENDPOINTS (MAIN MODULE)  
// ====================================================================

/**
 * GET /cases
 * Purpose: Get all cases with advanced filtering and Arabic search
 * Auth: User/Admin required
 * 
 * Query Parameters:
 * - page (int): Page number
 * - size (int): Items per page  
 * - search (string): Search in case_number, plaintiff, defendant (Arabic with diacritics support)
 * - case_type_id (int): Filter by case type
 * - judgment_type (enum): "pending", "won", "lost", "settled"
 * 
 * Success Response:
 * {
 *   "items": [
 *     {
 *       "id": 1,
 *       "case_number": "2024/001",
 *       "plaintiff": "محمد أحمد", 
 *       "defendant": "شركة الأمل",
 *       "judgment_type": "pending",
 *       "previous_judgment_id": null,
 *       "case_type": {
 *         "id": 1,
 *         "name": "قضايا مدنية"
 *       },
 *       "created_by": {"id": 1, "full_name": "مدير النظام"},
 *       "created_at": "2024-01-01T00:00:00"
 *     }
 *   ]
 * }
 * 
 * ARABIC SEARCH EXAMPLES:
 * - search="محمد" matches "محمد", "مُحمد", "مَحمد" etc.
 * - search="أحمد" matches "أحمد", "احمد" etc. 
 * - search="شركة" matches all company variations
 */

/**
 * POST /cases
 * Purpose: Create new case
 * 
 * Request Body:
 * {
 *   "case_number": "2024/002",
 *   "plaintiff": "علي محمد",
 *   "defendant": "شركة النور للتجارة", 
 *   "case_type_id": 1,
 *   "judgment_type": "pending",
 *   "previous_judgment_id": null  // Optional reference to previous judgment
 * }
 * 
 * Error Responses:
 * - 400: { "detail": "رقم القضية موجود بالفعل" }
 * - 400: { "detail": "نوع القضية غير موجود" }
 * - 400: { "detail": "القضية المرجعية غير موجودة" }
 */

/**
 * GET /cases/{case_id}
 * PUT /cases/{case_id}  
 * DELETE /cases/{case_id}
 * 
 * Error Response (404):
 * { "detail": "القضية غير موجودة" }
 */

/**
 * GET /cases/{case_id}/details
 * Purpose: Get case with full details including related data
 */

// ====================================================================
// 📅 CASE SESSIONS ENDPOINTS
// ====================================================================

/**
 * GET /cases/{case_id}/sessions
 * Purpose: Get all sessions for specific case
 * 
 * Query Parameters:
 * - page, size: Pagination
 * 
 * Success Response: Sessions ordered by session_date DESC
 * {
 *   "items": [
 *     {
 *       "id": 1,
 *       "case_id": 1,
 *       "session_date": "2024-02-15T10:00:00",
 *       "session_notes": "تم تأجيل الجلسة إلى موعد لاحق",
 *       "created_by": {"id": 1, "full_name": "مدير النظام"},
 *       "created_at": "2024-01-01T00:00:00"
 *     }
 *   ]
 * }
 */

/**
 * POST /cases/{case_id}/sessions
 * Purpose: Add new session to case
 * 
 * Request Body:
 * {
 *   "session_date": "2024-02-15T10:00:00",
 *   "session_notes": "ملاحظات الجلسة"
 * }
 */

/**
 * GET /case-sessions/{session_id}
 * PUT /case-sessions/{session_id}
 * DELETE /case-sessions/{session_id}
 */

// ====================================================================
// 📝 CASE NOTES ENDPOINTS
// ====================================================================

/**
 * GET /cases/{case_id}/notes
 * Purpose: Get all notes for specific case with Arabic search
 * 
 * Query Parameters:
 * - page, size: Pagination
 * - search (string): Search in note_text (Arabic supported)
 * 
 * Success Response: Notes ordered by created_at DESC
 */

/**
 * POST /cases/{case_id}/notes
 * Purpose: Add new note to case
 * 
 * Request Body:
 * {
 *   "note_text": "نص الملاحظة هنا"
 * }
 */

/**
 * GET /case-notes/{note_id}
 * PUT /case-notes/{note_id}  
 * DELETE /case-notes/{note_id}
 */

// ====================================================================
// 📊 STATISTICS ENDPOINTS
// ====================================================================

/**
 * GET /stats/dashboard
 * Purpose: Get comprehensive dashboard statistics
 * 
 * Success Response:
 * {
 *   "total_cases": 150,
 *   "total_users": 5,
 *   "total_case_types": 8,
 *   "total_sessions": 75,
 *   "total_notes": 200,
 *   "cases_by_judgment": [
 *     {"judgment_type": "pending", "case_count": 80},
 *     {"judgment_type": "won", "case_count": 45}
 *   ],
 *   "cases_by_type": [
 *     {"name": "قضايا مدنية", "case_count": 60}
 *   ],
 *   "recent_cases": [...],
 *   "upcoming_sessions": [...],
 *   "monthly_trend": [
 *     {"month": "2024-01", "count": 25}
 *   ]
 * }
 */

/**
 * GET /stats/cases-by-type
 * GET /stats/cases-by-judgment
 * GET /stats/monthly-trend
 * GET /stats/user-activity
 */

// ====================================================================
// 🔧 FRONTEND INTEGRATION PATTERNS
// ====================================================================

/**
 * ERROR HANDLING PATTERNS (Based on Testing):
 * 
 * Status 401: Token expired -> Redirect to login
 * Status 403: Permission denied -> Show Arabic error message
 * Status 404: Resource not found -> Show specific Arabic message
 * Status 400: Validation error -> Show field-specific Arabic message
 */

/**
 * ARABIC TEXT HANDLING:
 * - All Arabic text is UTF-8 encoded
 * - Search supports diacritics automatically
 * - Use RTL CSS for proper text direction
 * - Dates are in Gregorian calendar (Miladi)
 */

/**
 * PAGINATION PATTERN:
 * - Default page size: 10
 * - Maximum page size: 100
 * - Always handle total_pages for UI pagination
 */

/**
 * AUTHENTICATION FLOW:
 * 1. POST /auth/login -> Store access_token
 * 2. Include Bearer token in all subsequent requests
 * 3. Handle 401 responses by redirecting to login
 * 4. POST /auth/logout -> Clear local token
 */

/**
 * COMMON REQUEST EXAMPLES:
 */

// Login Example
const loginExample = {
  url: '/api/auth/login',
  method: 'POST',
  body: { username: 'admin', password: 'password123' }
};

// Get Cases with Arabic Search Example  
const searchCasesExample = {
  url: '/api/cases?search=محمد&page=1&size=10',
  method: 'GET',
  headers: { 'Authorization': 'Bearer TOKEN' }
};

// Create Case Example
const createCaseExample = {
  url: '/api/cases',
  method: 'POST',
  headers: { 'Authorization': 'Bearer TOKEN' },
  body: {
    case_number: '2024/001',
    plaintiff: 'محمد أحمد',
    defendant: 'شركة الأمل',
    case_type_id: 1,
    judgment_type: 'pending'
  }
};

// Dashboard Stats Example
const dashboardStatsExample = {
  url: '/api/stats/dashboard',
  method: 'GET', 
  headers: { 'Authorization': 'Bearer TOKEN' }
};

// ====================================================================
// 📝 TESTING INSIGHTS APPLIED
// ====================================================================

/**
 * Key findings from 97% test success rate:
 * 
 * 1. Statistics endpoint returns 403 (not 401) for permission errors
 * 2. Arabic search works with character normalization and diacritics
 * 3. Duplicate case numbers are properly handled with Arabic error messages
 * 4. Timestamp-based unique naming prevents test data conflicts
 * 5. All endpoints support Arabic text encoding properly
 * 6. Pagination is consistent across all list endpoints
 * 7. User authentication state is properly maintained
 */
