/**
 * FRONTEND UTILITIES HELPER
 * Common functions and utilities for the desktop application
 */

// ====================================================================
// ARABIC TEXT UTILITIES
// ====================================================================

/**
 * Arabic Text Helper Functions
 */
const ArabicUtils = {
  
  /**
   * Format Arabic text for display
   */
  formatText(text) {
    if (!text) return '';
    return text.trim();
  },
  
  /**
   * Check if text contains Arabic characters
   */
  hasArabic(text) {
    const arabicRegex = /[\u0600-\u06FF]/;
    return arabicRegex.test(text);
  },
  
  /**
   * Format date in Arabic (Miladi/Gregorian)
   */
  formatArabicDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-SA-u-ca-gregory', {
      calendar: 'gregory',
      year: 'numeric',
      month: 'long', 
      day: 'numeric'
    }) + ' (ميلادي)';
  },
  
  /**
   * Format date and time in Arabic (Miladi/Gregorian)
   */
  formatArabicDateTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString('ar-SA-u-ca-gregory', {
      calendar: 'gregory',
      year: 'numeric',
      month: 'long',
      day: 'numeric', 
      hour: '2-digit',
      minute: '2-digit'
    }) + ' (ميلادي)';
  },

  /**
   * Format short date in Arabic (Miladi/Gregorian) - for tables and lists
   */
  formatShortArabicDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-SA-u-ca-gregory', {
      calendar: 'gregory',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }) + ' (م)';
  },
  
  /**
   * Convert numbers to Arabic numerals
   */
  toArabicNumbers(text) {
    const arabicNumbers = '٠١٢٣٤٥٦٧٨٩';
    return text.toString().replace(/[0-9]/g, (match) => arabicNumbers[match]);
  },
  
  /**
   * Convert Arabic numerals to English
   */
  toEnglishNumbers(text) {
    const arabicNumbers = '٠١٢٣٤٥٦٧٨٩';
    return text.toString().replace(/[٠-٩]/g, (match) => arabicNumbers.indexOf(match));
  },
  
  /**
   * Truncate Arabic text with proper ellipsis
   */
  truncateText(text, maxLength = 50) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  }
};

// ====================================================================
// AUTHENTICATION UTILITIES
// ====================================================================

/**
 * Authentication Helper Functions
 */
const AuthUtils = {
  
  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    const token = localStorage.getItem('access_token');
    const expiry = localStorage.getItem('token_expires_at');
    
    if (!token || !expiry) return false;
    if (Date.now() > parseInt(expiry)) {
      this.logout();
      return false;
    }
    return true;
  },
  
  /**
   * Get current user from localStorage
   */
  getCurrentUser() {
    const userStr = localStorage.getItem('user_data');
    return userStr ? JSON.parse(userStr) : null;
  },
  
  /**
   * Check if current user is admin
   */
  isAdmin() {
    const user = this.getCurrentUser();
    return user && user.user_type === 'admin';
  },
  
  /**
   * Get authorization headers
   */
  getAuthHeaders() {
    return {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    };
  },
  
  /**
   * Save authentication data
   */
  saveAuthData(loginResponse) {
    localStorage.setItem('access_token', loginResponse.access_token);
    localStorage.setItem('user_data', JSON.stringify(loginResponse.user));
    localStorage.setItem('token_expires_at', Date.now() + (loginResponse.expires_in * 1000));
  },
  
  /**
   * Clear authentication data
   */
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('token_expires_at');
  }
};

// ====================================================================
// API UTILITIES
// ====================================================================

/**
 * API Helper Functions
 */
const APIUtils = {
  
  /**
   * Base API request function
   */
  async request(url, options = {}) {
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(AuthUtils.isAuthenticated() ? AuthUtils.getAuthHeaders() : {}),
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      
      // Handle authentication errors
      if (response.status === 401) {
        AuthUtils.logout();
        throw new Error('انتهت جلسة العمل، يرجى تسجيل الدخول مرة أخرى');
      }
      
      if (response.status === 403) {
        throw new Error('غير مسموح لك بتنفيذ هذا الإجراء');
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'خطأ في الشبكة' }));
        throw new Error(error.detail || `HTTP Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },
  
  /**
   * Build query string from object
   */
  buildQueryString(params) {
    return new URLSearchParams(
      Object.entries(params).filter(([_, value]) => value !== null && value !== undefined)
    ).toString();
  },
  
  /**
   * Handle API errors with user-friendly messages
   */
  handleError(error, context = '') {
    console.error(`API Error ${context}:`, error);
    
    // Return Arabic error messages
    if (error.message.includes('401')) {
      return 'انتهت جلسة العمل، يرجى تسجيل الدخول مرة أخرى';
    } else if (error.message.includes('403')) {
      return 'غير مسموح لك بتنفيذ هذا الإجراء';
    } else if (error.message.includes('404')) {
      return 'العنصر المطلوب غير موجود';
    } else if (error.message.includes('موجود بالفعل')) {
      return error.message;
    } else if (error.message.includes('غير موجود')) {
      return error.message;
    } else {
      return 'حدث خطأ غير متوقع، يرجى المحاولة مرة أخرى';
    }
  }
};

// ====================================================================
// FORM VALIDATION UTILITIES
// ====================================================================

/**
 * Form Validation Helper Functions
 */
const ValidationUtils = {
  
  /**
   * Validate required field
   */
  required(value, fieldName = 'الحقل') {
    if (!value || value.toString().trim() === '') {
      return `${fieldName} مطلوب`;
    }
    return null;
  },
  
  /**
   * Validate minimum length
   */
  minLength(value, min, fieldName = 'الحقل') {
    if (value && value.length < min) {
      return `${fieldName} يجب أن يحتوي على ${min} أحرف على الأقل`;
    }
    return null;
  },
  
  /**
   * Validate maximum length
   */
  maxLength(value, max, fieldName = 'الحقل') {
    if (value && value.length > max) {
      return `${fieldName} يجب أن لا يتجاوز ${max} حرف`;
    }
    return null;
  },
  
  /**
   * Validate username pattern
   */
  username(value) {
    const errors = [];
    
    const requiredError = this.required(value, 'اسم المستخدم');
    if (requiredError) errors.push(requiredError);
    
    const minError = this.minLength(value, 3, 'اسم المستخدم');
    if (minError) errors.push(minError);
    
    const maxError = this.maxLength(value, 50, 'اسم المستخدم');
    if (maxError) errors.push(maxError);
    
    if (value && !/^[a-zA-Z0-9_]+$/.test(value)) {
      errors.push('اسم المستخدم يجب أن يحتوي على أحرف وأرقام فقط');
    }
    
    return errors.length > 0 ? errors[0] : null;
  },
  
  /**
   * Validate password
   */
  password(value) {
    const errors = [];
    
    const requiredError = this.required(value, 'كلمة المرور');
    if (requiredError) errors.push(requiredError);
    
    const minError = this.minLength(value, 6, 'كلمة المرور');
    if (minError) errors.push(minError);
    
    return errors.length > 0 ? errors[0] : null;
  },
  
  /**
   * Validate case number format
   */
  caseNumber(value) {
    const requiredError = this.required(value, 'رقم القضية');
    if (requiredError) return requiredError;
    
    if (!/^\d{4}\/\d+$/.test(value)) {
      return 'رقم القضية يجب أن يكون بالشكل YYYY/NNN';
    }
    
    return null;
  },
  
  /**
   * Validate Arabic text
   */
  arabicText(value, fieldName = 'النص') {
    const requiredError = this.required(value, fieldName);
    if (requiredError) return requiredError;
    
    const minError = this.minLength(value, 2, fieldName);
    if (minError) return minError;
    
    const maxError = this.maxLength(value, 255, fieldName);
    if (maxError) return maxError;
    
    return null;
  },
  
  /**
   * Validate date
   */
  date(value, fieldName = 'التاريخ') {
    const requiredError = this.required(value, fieldName);
    if (requiredError) return requiredError;
    
    const date = new Date(value);
    if (isNaN(date.getTime())) {
      return `${fieldName} غير صحيح`;
    }
    
    return null;
  }
};

// ====================================================================
// UI UTILITIES
// ====================================================================

/**
 * UI Helper Functions
 */
const UIUtils = {
  
  /**
   * Show notification (can be implemented with toast library)
   */
  showNotification(message, type = 'info') {
    console.log(`${type.toUpperCase()}: ${message}`);
    // TODO: Implement with actual notification library
  },
  
  /**
   * Show success message
   */
  showSuccess(message) {
    this.showNotification(message, 'success');
  },
  
  /**
   * Show error message  
   */
  showError(message) {
    this.showNotification(message, 'error');
  },
  
  /**
   * Show warning message
   */
  showWarning(message) {
    this.showNotification(message, 'warning');
  },
  
  /**
   * Confirm dialog
   */
  async confirm(message) {
    return new Promise((resolve) => {
      // TODO: Implement with actual modal/dialog
      const result = window.confirm(message);
      resolve(result);
    });
  },
  
  /**
   * Format file size
   */
  formatFileSize(bytes) {
    if (bytes === 0) return '0 بايت';
    
    const k = 1024;
    const sizes = ['بايت', 'كيلوبايت', 'ميجابايت', 'جيجابايت'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },
  
  /**
   * Debounce function for search inputs
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
};

// ====================================================================
// LOCAL STORAGE UTILITIES
// ====================================================================

/**
 * Local Storage Helper Functions
 */
const StorageUtils = {
  
  /**
   * Set item in localStorage with JSON stringify
   */
  set(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  },
  
  /**
   * Get item from localStorage with JSON parse
   */
  get(key, defaultValue = null) {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return defaultValue;
    }
  },
  
  /**
   * Remove item from localStorage
   */
  remove(key) {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Error removing from localStorage:', error);
    }
  },
  
  /**
   * Clear all localStorage
   */
  clear() {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('Error clearing localStorage:', error);
    }
  }
};

// ====================================================================
// CONSTANTS
// ====================================================================

/**
 * Application Constants
 */
const Constants = {
  
  // API Configuration
  API_BASE_URL: 'http://localhost:8000/api',
  
  // Pagination
  DEFAULT_PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
  
  // Judgment Types (Arabic labels)
  JUDGMENT_TYPES: {
    pending: 'قيد النظر',
    won: 'كسب القضية', 
    lost: 'خسارة القضية',
    settled: 'تسوية'
  },
  
  // User Types (Arabic labels)
  USER_TYPES: {
    admin: 'مدير',
    user: 'مستخدم'
  },
  
  // Date Formats (Gregorian/Miladi)
  DATE_FORMAT: 'YYYY-MM-DD',
  DATETIME_FORMAT: 'YYYY-MM-DD HH:mm:ss',
  CALENDAR_TYPE: 'gregorian', // Explicit Gregorian calendar
  DATE_LOCALE: 'ar-SA-u-ca-gregory', // Arabic locale with Gregorian calendar
  DATE_SUFFIX: '(ميلادي)', // Gregorian indicator
  
  // Colors (Classic theme)
  COLORS: {
    primary: '#1e40af',      // Deep Blue
    secondary: '#f59e0b',    // Gold
    success: '#10b981',      // Green
    warning: '#f97316',      // Orange  
    error: '#ef4444',        // Red
    background: '#f8fafc',   // Light Gray
    text: '#1f2937'          // Dark Gray
  },
  
  // File Upload
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
  ALLOWED_FILE_TYPES: ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'],
  
  // Timeouts
  REQUEST_TIMEOUT: 30000,  // 30 seconds
  DEBOUNCE_DELAY: 300      // 300ms for search
};

// ====================================================================
// GLOBAL DATE FORMATTING FUNCTIONS
// ====================================================================

// Global date formatting functions for easy access
const formatDate = (dateString) => ArabicUtils.formatArabicDate(dateString);
const formatDateTime = (dateString) => ArabicUtils.formatArabicDateTime(dateString);
const formatShortDate = (dateString) => ArabicUtils.formatShortArabicDate(dateString);

// ====================================================================
// EXPORT ALL UTILITIES
// ====================================================================

module.exports = {
  ArabicUtils,
  AuthUtils,
  APIUtils,
  ValidationUtils,
  UIUtils,
  StorageUtils,
  Constants,
  // Quick access date functions
  formatDate,
  formatDateTime,
  formatShortDate
};
