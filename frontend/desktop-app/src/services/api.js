// api.js - API service based on backend endpoints from api-helper.js

// Default API base URL (will be updated from config)
let API_BASE_URL = 'http://localhost:8000/api/v1';

// Function to initialize API configuration
const initializeApiConfig = async () => {
  try {
    // Check if we're in Electron environment
    if (typeof window !== 'undefined' && window.electronAPI) {
      API_BASE_URL = await window.electronAPI.getServerConfig();
    }
    // Fallback for development/web environment
    else if (process.env.REACT_APP_SERVER_IP && process.env.REACT_APP_SERVER_PORT) {
      API_BASE_URL = `http://${process.env.REACT_APP_SERVER_IP}:${process.env.REACT_APP_SERVER_PORT}/api/v1`;
    }
  } catch (error) {
    console.warn('Could not load server configuration, using default:', error);
  }
};

// Initialize configuration when module loads (only once)
let configInitPromise = null;
if (typeof window !== 'undefined') {
  configInitPromise = initializeApiConfig();
}

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.configInitialized = false;
    this.initializeConfig();
  }

  async initializeConfig() {
    if (!this.configInitialized) {
      // Wait for the initial config promise if it exists
      if (configInitPromise) {
        await configInitPromise;
      } else {
        await initializeApiConfig();
      }
      this.baseURL = API_BASE_URL;
      this.configInitialized = true;
    }
  }

  // Get auth headers from localStorage
  getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  // Generic request method with error handling
  async request(endpoint, options = {}) {
    // Ensure configuration is loaded
    await this.initializeConfig();
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: this.getAuthHeaders(),
      ...options
    };

    try {
      const response = await fetch(url, config);
      
      // Handle auth errors - based on testing insights
      if (response.status === 401) {
        // Token expired, clear auth data and redirect
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');
        localStorage.removeItem('token_expires_at');
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
      console.error(`API Error on ${endpoint}:`, error);
      throw error;
    }
  }

  // GET request with query parameters
  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(
      Object.entries(params).filter(([_, value]) => value !== null && value !== undefined)
    ).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(url);
  }

  // POST request
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  // PUT request
  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  // DELETE request
  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE'
    });
  }

  // =============================================================
  // STATISTICS ENDPOINTS - Based on GET /stats/dashboard
  // =============================================================
  
  async getDashboardStats() {
    return this.get('/stats/dashboard');
  }

  async getCasesByType() {
    return this.get('/stats/cases-by-type');
  }

  async getCasesByJudgment() {
    return this.get('/stats/cases-by-judgment');
  }

  // =============================================================
  // CASES ENDPOINTS - Based on GET /cases with filtering
  // =============================================================
  
  async getCases(filters = {}) {
    const { 
      page = 1, 
      size = 10, 
      search = '', 
      case_type_id = null, 
      judgment_type = null 
    } = filters;
    
    return this.get('/cases', {
      page,
      size,
      search,
      case_type_id,
      judgment_type
    });
  }

  async getCase(caseId) {
    return this.get(`/cases/${caseId}`);
  }

  async createCase(caseData) {
    return this.post('/cases', caseData);
  }

  async updateCase(caseId, updateData) {
    return this.put(`/cases/${caseId}`, updateData);
  }

  async deleteCase(caseId) {
    return this.delete(`/cases/${caseId}`);
  }

  // =============================================================
  // CASE TYPES ENDPOINTS - Based on GET /case-types
  // =============================================================
  
  async getCaseTypes(page = 1, size = 50, search = '') {
    return this.get('/case-types', { page, size, search });
  }

  async createCaseType(caseTypeData) {
    return this.post('/case-types', caseTypeData);
  }

  async getCaseType(caseTypeId) {
    return this.get(`/case-types/${caseTypeId}`);
  }

  async updateCaseType(caseTypeId, updateData) {
    return this.put(`/case-types/${caseTypeId}`, updateData);
  }

  async deleteCaseType(caseTypeId) {
    return this.delete(`/case-types/${caseTypeId}`);
  }

  // =============================================================
  // USERS ENDPOINTS - Admin only, based on GET /users
  // =============================================================
  
  async getUsers(page = 1, size = 10, search = '') {
    return this.get('/users', { page, size, search });
  }

  async createUser(userData) {
    return this.post('/users', userData);
  }

  async getUser(userId) {
    return this.get(`/users/${userId}`);
  }

  async updateUser(userId, updateData) {
    return this.put(`/users/${userId}`, updateData);
  }

  async deleteUser(userId) {
    return this.delete(`/users/${userId}`);
  }

  async updateUserPassword(userId, passwordData) {
    return this.put(`/users/${userId}/password`, passwordData);
  }

  // =============================================================
  // SESSIONS ENDPOINTS - Phase 3
  // =============================================================
  
  async getSessions(caseId, page = 1, size = 10) {
    return this.get(`/cases/${caseId}/sessions`, { page, size });
  }

  async createSession(caseId, sessionData) {
    return this.post(`/cases/${caseId}/sessions`, sessionData);
  }

  async getSession(caseId, sessionId) {
    return this.get(`/sessions/${sessionId}`);
  }

  async updateSession(caseId, sessionId, updateData) {
    return this.put(`/sessions/${sessionId}`, updateData);
  }

  async deleteSession(caseId, sessionId) {
    return this.delete(`/sessions/${sessionId}`);
  }

  // =============================================================
  // NOTES ENDPOINTS - Phase 3
  // =============================================================
  
  async getNotes(caseId, page = 1, size = 10, search = '', category = '') {
    return this.get(`/cases/${caseId}/notes`, { page, size, search, category });
  }

  async createNote(caseId, noteData) {
    return this.post(`/cases/${caseId}/notes`, noteData);
  }

  async getNote(caseId, noteId) {
    return this.get(`/notes/${noteId}`);
  }

  async updateNote(caseId, noteId, updateData) {
    return this.put(`/notes/${noteId}`, updateData);
  }

  async deleteNote(caseId, noteId) {
    return this.delete(`/notes/${noteId}`);
  }

  // =============================================================
  // REPORTS ENDPOINTS - Phase 3
  // =============================================================
  
  async getReportsData(dateFrom, dateTo) {
    return this.get('/stats/reports', { date_from: dateFrom, date_to: dateTo });
  }

  async getCasesReport(dateFrom, dateTo, status = '', caseType = '') {
    return this.get('/stats/cases-report', { 
      date_from: dateFrom, 
      date_to: dateTo, 
      status, 
      case_type: caseType 
    });
  }

  async getSessionsReport(dateFrom, dateTo) {
    return this.get('/stats/sessions-report', { date_from: dateFrom, date_to: dateTo });
  }

  async getUsersReport() {
    return this.get('/stats/users-report');
  }

  async exportReport(reportType, format = 'pdf', dateFrom, dateTo) {
    const params = { format, date_from: dateFrom, date_to: dateTo };
    return this.get(`/stats/export/${reportType}`, params);
  }

  // =============================================================
  // SETTINGS ENDPOINTS - Phase 3
  // =============================================================
  
  async getSystemSettings() {
    return this.get('/settings');
  }

  async updateSystemSettings(settingsData) {
    return this.put('/settings', settingsData);
  }

  async createBackup() {
    return this.post('/settings/backup');
  }

  async restoreBackup(backupFile) {
    return this.post('/settings/restore', backupFile);
  }

  // =============================================================
  // PHASE 4 - POLISH FEATURES ENDPOINTS
  // =============================================================

  // Backup System Endpoints
  async createDatabaseBackup() {
    return this.post('/backup/create');
  }

  async listBackups() {
    return this.get('/backup/list');
  }

  async restoreDatabaseBackup(backupId) {
    return this.post(`/backup/restore/${backupId}`);
  }

  async downloadBackup(backupId) {
    const response = await fetch(`${this.baseURL}/backup/download/${backupId}`, {
      headers: this.getAuthHeaders()
    });
    return response;
  }

  async deleteBackup(backupId) {
    return this.delete(`/backup/delete/${backupId}`);
  }

  async getBackupOperations() {
    return this.get('/backup/operations');
  }

  // Export Endpoints
  async exportCases(format, filters = {}) {
    const params = { format, ...filters };
    const response = await fetch(`${this.baseURL}/export/cases?${new URLSearchParams(params)}`, {
      headers: this.getAuthHeaders()
    });
    return response;
  }

  async exportSessions(format, filters = {}) {
    const params = { format, ...filters };
    const response = await fetch(`${this.baseURL}/export/sessions?${new URLSearchParams(params)}`, {
      headers: this.getAuthHeaders()
    });
    return response;
  }

  async exportSummaryReport(format, filters = {}) {
    const params = { format, ...filters };
    const response = await fetch(`${this.baseURL}/export/summary?${new URLSearchParams(params)}`, {
      headers: this.getAuthHeaders()
    });
    return response;
  }

  async getSupportedExportFormats() {
    return this.get('/export/formats');
  }

  // Print Endpoints
  getPrintCaseUrl(caseId) {
    return `${this.baseURL}/print/case/${caseId}`;
  }

  getPrintCasesListUrl(filters = {}) {
    const params = new URLSearchParams(filters);
    return `${this.baseURL}/print/cases${params.toString() ? '?' + params.toString() : ''}`;
  }

  getPrintDashboardUrl() {
    return `${this.baseURL}/print/dashboard`;
  }

  // Performance Endpoints
  async getSystemMetrics() {
    return this.get('/performance/metrics');
  }

  async getDatabasePerformance() {
    return this.get('/performance/database');
  }

  async optimizeSystem() {
    return this.post('/performance/optimize');
  }

  async optimizeSystemSync() {
    return this.post('/performance/optimize/sync');
  }

  async clearCache() {
    return this.post('/performance/cache/clear');
  }

  async getCacheInfo() {
    return this.get('/performance/cache');
  }

  async getPerformanceTrends(hours = 24) {
    return this.get('/performance/trends', { hours });
  }

  async getPerformanceLogs(limit = 100) {
    return this.get('/performance/logs', { limit });
  }

  async performHealthCheck() {
    return this.get('/performance/health');
  }

  // =============================================================
  // PHONE DIRECTORY ENDPOINTS - دليل التليفونات
  // =============================================================
  
  async getPhoneDirectoryEntries(filters = {}) {
    const { 
      page = 1, 
      size = 10, 
      search = '', 
      الاسم = null,
      الرقم = null,
      الجهه = null
    } = filters;
    
    return this.get('/phone-directory', {
      page,
      size,
      search,
      الاسم,
      الرقم,
      الجهه
    });
  }

  async getPhoneDirectoryEntry(entryId) {
    return this.get(`/phone-directory/${entryId}`);
  }

  async createPhoneDirectoryEntry(entryData) {
    return this.post('/phone-directory', entryData);
  }

  async updatePhoneDirectoryEntry(entryId, updateData) {
    return this.put(`/phone-directory/${entryId}`, updateData);
  }

  async deletePhoneDirectoryEntry(entryId) {
    return this.delete(`/phone-directory/${entryId}`);
  }

  async searchPhoneDirectoryEntries(searchData) {
    return this.post('/phone-directory/search', searchData);
  }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;
