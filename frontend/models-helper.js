/**
 * DATA MODELS HELPER
 * Frontend data structures based on backend Pydantic models
 */

// ====================================================================
// BASE MODELS
// ====================================================================

/**
 * PaginatedResponse Structure
 * Used by all list endpoints
 */
const PaginatedResponse = {
  items: [],          // Array of data items
  total: 0,           // Total number of items
  page: 1,            // Current page number
  size: 10,           // Items per page
  total_pages: 1      // Total number of pages
};

/**
 * BaseResponse Structure
 * Used for simple API responses
 */
const BaseResponse = {
  success: true,
  message: "عملية ناجحة"
};

/**
 * ErrorResponse Structure
 * Used for API errors
 */
const ErrorResponse = {
  detail: "رسالة الخطأ هنا"
};

// ====================================================================
// USER MODELS
// ====================================================================

/**
 * User Model
 * Complete user information
 */
const User = {
  id: 1,
  username: "admin",
  full_name: "مدير النظام",
  user_type: "admin",        // "admin" or "user"
  is_active: true,
  created_at: "2024-01-01T00:00:00",
  updated_at: "2024-01-01T00:00:00"
};

/**
 * UserCreate Model
 * For creating new users
 */
const UserCreate = {
  username: "newuser",
  password: "password123",
  full_name: "اسم المستخدم الكامل",
  user_type: "user"          // "admin" or "user"
};

/**
 * UserUpdate Model  
 * For updating user information
 */
const UserUpdate = {
  full_name: "اسم جديد",
  user_type: "admin",
  is_active: false
};

/**
 * UserPasswordUpdate Model
 * For updating user password
 */
const UserPasswordUpdate = {
  new_password: "newpassword123"
};

// ====================================================================
// AUTHENTICATION MODELS
// ====================================================================

/**
 * LoginRequest Model
 */
const LoginRequest = {
  username: "admin",
  password: "password123"
};

/**
 * LoginResponse Model
 */
const LoginResponse = {
  access_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  token_type: "bearer",
  expires_in: 86400,         // seconds
  user: User                 // User object
};

// ====================================================================
// CASE TYPE MODELS
// ====================================================================

/**
 * CaseType Model
 */
const CaseType = {
  id: 1,
  name: "قضايا مدنية",
  description: "القضايا المدنية والتجارية",
  created_by: {
    id: 1,
    full_name: "مدير النظام"
  },
  updated_by: {
    id: 1, 
    full_name: "مدير النظام"
  },
  created_at: "2024-01-01T00:00:00",
  updated_at: "2024-01-01T00:00:00"
};

/**
 * CaseTypeCreate Model
 */
const CaseTypeCreate = {
  name: "قضايا تجارية",
  description: "وصف نوع القضية"
};

/**
 * CaseTypeUpdate Model
 */
const CaseTypeUpdate = {
  name: "اسم محدث",
  description: "وصف محدث"
};

// ====================================================================
// CASE MODELS
// ====================================================================

/**
 * JudgmentType Enum
 * Available judgment statuses
 */
const JudgmentType = {
  PENDING: "pending",
  WON: "won", 
  LOST: "lost",
  SETTLED: "settled"
};

/**
 * Case Model
 */
const Case = {
  id: 1,
  case_number: "2024/001",
  plaintiff: "محمد أحمد",
  defendant: "شركة الأمل", 
  judgment_type: "pending",      // JudgmentType enum
  previous_judgment_id: null,    // Optional reference
  case_type_id: 1,
  case_type: {                   // Populated case type info
    id: 1,
    name: "قضايا مدنية",
    description: "القضايا المدنية والتجارية"
  },
  created_by: {
    id: 1,
    full_name: "مدير النظام"
  },
  updated_by: {
    id: 1,
    full_name: "مدير النظام"  
  },
  created_at: "2024-01-01T00:00:00",
  updated_at: "2024-01-01T00:00:00"
};

/**
 * CaseCreate Model
 */
const CaseCreate = {
  case_number: "2024/002",
  plaintiff: "علي محمد",
  defendant: "شركة النور للتجارة",
  case_type_id: 1,
  judgment_type: "pending",
  previous_judgment_id: null     // Optional
};

/**
 * CaseUpdate Model
 */
const CaseUpdate = {
  plaintiff: "اسم مدعي محدث",
  defendant: "اسم مدعى عليه محدث",
  judgment_type: "won",
  case_type_id: 2
};

/**
 * CaseWithDetails Model  
 * Extended case information with related data
 */
const CaseWithDetails = {
  ...Case,                       // All Case fields
  sessions_count: 3,
  notes_count: 5,
  last_session_date: "2024-02-15T10:00:00",
  recent_sessions: [],           // Array of CaseSession
  recent_notes: []               // Array of CaseNote
};

// ====================================================================
// CASE SESSION MODELS
// ====================================================================

/**
 * CaseSession Model
 */
const CaseSession = {
  id: 1,
  case_id: 1,
  session_date: "2024-02-15T10:00:00",
  session_notes: "تم تأجيل الجلسة إلى موعد لاحق",
  created_by: {
    id: 1,
    full_name: "مدير النظام"
  },
  updated_by: {
    id: 1,
    full_name: "مدير النظام"
  },
  created_at: "2024-01-01T00:00:00",
  updated_at: "2024-01-01T00:00:00"
};

/**
 * CaseSessionCreate Model
 */
const CaseSessionCreate = {
  session_date: "2024-02-15T10:00:00",
  session_notes: "ملاحظات الجلسة"
};

/**
 * CaseSessionUpdate Model
 */
const CaseSessionUpdate = {
  session_date: "2024-02-20T14:00:00",
  session_notes: "ملاحظات محدثة"
};

// ====================================================================
// CASE NOTE MODELS
// ====================================================================

/**
 * CaseNote Model
 */
const CaseNote = {
  id: 1,
  case_id: 1,
  note_text: "نص الملاحظة هنا",
  created_by: {
    id: 1,
    full_name: "مدير النظام"
  },
  updated_by: {
    id: 1,
    full_name: "مدير النظام"
  },
  created_at: "2024-01-01T00:00:00",
  updated_at: "2024-01-01T00:00:00"
};

/**
 * CaseNoteCreate Model
 */
const CaseNoteCreate = {
  note_text: "نص الملاحظة الجديدة"
};

/**
 * CaseNoteUpdate Model
 */
const CaseNoteUpdate = {
  note_text: "نص الملاحظة المحدث"
};

// ====================================================================
// STATISTICS MODELS
// ====================================================================

/**
 * DashboardStats Model
 * Complete dashboard statistics structure
 */
const DashboardStats = {
  total_cases: 150,
  total_users: 5,
  total_case_types: 8,
  total_sessions: 75,
  total_notes: 200,
  cases_by_judgment: [
    {
      judgment_type: "pending",
      case_count: 80
    },
    {
      judgment_type: "won", 
      case_count: 45
    },
    {
      judgment_type: "lost",
      case_count: 15
    },
    {
      judgment_type: "settled",
      case_count: 10
    }
  ],
  cases_by_type: [
    {
      id: 1,
      name: "قضايا مدنية",
      description: "القضايا المدنية والتجارية",
      case_count: 60
    },
    {
      id: 2,
      name: "قضايا تجارية",
      description: "القضايا التجارية",
      case_count: 45
    }
  ],
  recent_cases: [
    {
      id: 1,
      case_number: "2024/001",
      plaintiff: "محمد أحمد",
      defendant: "شركة الأمل",
      case_type_name: "قضايا مدنية",
      judgment_type: "pending",
      created_at: "2024-01-01T00:00:00"
    }
  ],
  upcoming_sessions: [
    {
      case_number: "2024/001",
      plaintiff: "محمد أحمد",
      defendant: "شركة الأمل", 
      session_date: "2024-02-15T10:00:00",
      session_notes: "جلسة المرافعة النهائية"
    }
  ],
  monthly_trend: [
    {
      month: "2024-01",
      count: 25
    },
    {
      month: "2024-02",
      count: 30
    }
  ]
};

/**
 * CasesByTypeStats Model
 */
const CasesByTypeStats = [
  {
    id: 1,
    name: "قضايا مدنية",
    description: "القضايا المدنية والتجارية",
    case_count: 60
  }
];

/**
 * CasesByJudgmentStats Model
 */
const CasesByJudgmentStats = [
  {
    judgment_type: "pending",
    case_count: 80
  }
];

/**
 * MonthlyTrendStats Model
 */
const MonthlyTrendStats = [
  {
    month: "2024-01", 
    count: 25
  }
];

/**
 * UserActivityStats Model
 */
const UserActivityStats = [
  {
    user_id: 1,
    full_name: "مدير النظام",
    cases_created: 50,
    notes_created: 120,
    sessions_created: 30,
    last_activity: "2024-01-01T00:00:00"
  }
];

// ====================================================================
// VALIDATION PATTERNS
// ====================================================================

/**
 * Form Validation Patterns
 * Based on backend model validation
 */
const ValidationPatterns = {
  // Username validation
  username: {
    required: true,
    minLength: 3,
    maxLength: 50,
    pattern: /^[a-zA-Z0-9_]+$/,
    errorMessage: "اسم المستخدم يجب أن يحتوي على أحرف وأرقام فقط"
  },
  
  // Password validation
  password: {
    required: true,
    minLength: 6,
    errorMessage: "كلمة المرور يجب أن تحتوي على 6 أحرف على الأقل"
  },
  
  // Arabic text validation
  arabicText: {
    required: true,
    minLength: 2,
    maxLength: 255,
    errorMessage: "النص مطلوب ويجب أن يكون بين 2 و 255 حرف"
  },
  
  // Case number validation
  caseNumber: {
    required: true,
    pattern: /^\d{4}\/\d+$/,
    errorMessage: "رقم القضية يجب أن يكون بالشكل YYYY/NNN"
  },
  
  // Date validation
  date: {
    required: true,
    errorMessage: "التاريخ مطلوب"
  },
  
  // Email validation (if needed)
  email: {
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    errorMessage: "البريد الإلكتروني غير صحيح"
  }
};

// ====================================================================
// EXPORT ALL MODELS
// ====================================================================

module.exports = {
  // Base Models
  PaginatedResponse,
  BaseResponse, 
  ErrorResponse,
  
  // User Models
  User,
  UserCreate,
  UserUpdate,
  UserPasswordUpdate,
  
  // Auth Models
  LoginRequest,
  LoginResponse,
  
  // Case Type Models
  CaseType,
  CaseTypeCreate,
  CaseTypeUpdate,
  
  // Case Models
  JudgmentType,
  Case,
  CaseCreate,
  CaseUpdate,
  CaseWithDetails,
  
  // Case Session Models
  CaseSession,
  CaseSessionCreate,
  CaseSessionUpdate,
  
  // Case Note Models
  CaseNote,
  CaseNoteCreate,
  CaseNoteUpdate,
  
  // Statistics Models
  DashboardStats,
  CasesByTypeStats,
  CasesByJudgmentStats,
  MonthlyTrendStats,
  UserActivityStats,
  
  // Validation
  ValidationPatterns
};
