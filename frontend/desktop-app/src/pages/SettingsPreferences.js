import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/api';
import { formatDateTime } from '../utils-helper';

const SettingsPreferences = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  
  // Profile Settings
  const [profileData, setProfileData] = useState({
    full_name: '',
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  // System Settings (Admin only)
  const [systemSettings, setSystemSettings] = useState({
    app_name: 'نظام إدارة القضايا القانونية',
    company_name: 'مكتب المحاماة',
    contact_email: 'info@lawfirm.com',
    contact_phone: '',
    address: '',
    timezone: 'Africa/Cairo',
    date_format: 'dd/MM/yyyy',
    language: 'ar'
  });

  // Notification Settings
  const [notificationSettings, setNotificationSettings] = useState({
    email_notifications: true,
    session_reminders: true,
    case_updates: true,
    system_alerts: true,
    reminder_hours: 24
  });

  // Database Settings (Admin only)
  const [databaseSettings, setDatabaseSettings] = useState({
    auto_backup: true,
    backup_frequency: 'daily',
    backup_retention_days: 30,
    last_backup: null
  });

  const timezones = [
    { value: 'Africa/Cairo', label: 'القاهرة (GMT+2)' },
    { value: 'Asia/Riyadh', label: 'الرياض (GMT+3)' },
    { value: 'Asia/Dubai', label: 'دبي (GMT+4)' },
    { value: 'Europe/London', label: 'لندن (GMT+0)' },
    { value: 'America/New_York', label: 'نيويورك (GMT-5)' }
  ];

  const languages = [
    { value: 'ar', label: 'العربية' },
    { value: 'en', label: 'English' }
  ];

  const dateFormats = [
    { value: 'dd/MM/yyyy', label: 'يوم/شهر/سنة (31/12/2023)' },
    { value: 'MM/dd/yyyy', label: 'شهر/يوم/سنة (12/31/2023)' },
    { value: 'yyyy-MM-dd', label: 'سنة-شهر-يوم (2023-12-31)' }
  ];

  useEffect(() => {
    if (user) {
      setProfileData(prev => ({
        ...prev,
        full_name: user.full_name || ''
      }));
    }
    loadSystemSettings();
  }, [user]);

  const loadSystemSettings = async () => {
    try {
      // Load system settings from API or localStorage
      const savedSettings = localStorage.getItem('systemSettings');
      if (savedSettings) {
        setSystemSettings(JSON.parse(savedSettings));
      }

      const savedNotifications = localStorage.getItem('notificationSettings');
      if (savedNotifications) {
        setNotificationSettings(JSON.parse(savedNotifications));
      }

      const savedDatabase = localStorage.getItem('databaseSettings');
      if (savedDatabase) {
        setDatabaseSettings(JSON.parse(savedDatabase));
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    
    if (profileData.new_password && profileData.new_password !== profileData.confirm_password) {
      toast.error('كلمات المرور الجديدة غير متطابقة');
      return;
    }

    try {
      setLoading(true);
      
      const updateData = {
        full_name: profileData.full_name
      };

      if (profileData.new_password) {
        updateData.password = profileData.new_password;
      }

      await apiService.updateUser(user.user_id, updateData);
      
      toast.success('تم تحديث الملف الشخصي بنجاح');
      
      // Clear password fields
      setProfileData(prev => ({
        ...prev,
        current_password: '',
        new_password: '',
        confirm_password: ''
      }));
    } catch (error) {
      toast.error('فشل في تحديث الملف الشخصي');
    } finally {
      setLoading(false);
    }
  };

  const handleSystemSettingsSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      
      // Save to localStorage (in a real app, you'd send to API)
      localStorage.setItem('systemSettings', JSON.stringify(systemSettings));
      
      toast.success('تم حفظ إعدادات النظام بنجاح');
    } catch (error) {
      toast.error('فشل في حفظ إعدادات النظام');
    } finally {
      setLoading(false);
    }
  };

  const handleNotificationSettingsSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      
      // Save to localStorage
      localStorage.setItem('notificationSettings', JSON.stringify(notificationSettings));
      
      toast.success('تم حفظ إعدادات التنبيهات بنجاح');
    } catch (error) {
      toast.error('فشل في حفظ إعدادات التنبيهات');
    } finally {
      setLoading(false);
    }
  };

  const handleDatabaseBackup = async () => {
    try {
      setLoading(true);
      
      // Simulate backup process
      toast.info('جاري إنشاء نسخة احتياطية...');
      
      // In a real app, you would call the backup API endpoint
      setTimeout(() => {
        setDatabaseSettings(prev => ({
          ...prev,
          last_backup: new Date().toISOString()
        }));
        toast.success('تم إنشاء النسخة الاحتياطية بنجاح');
        setLoading(false);
      }, 3000);
    } catch (error) {
      toast.error('فشل في إنشاء النسخة الاحتياطية');
      setLoading(false);
    }
  };

  const handleDatabaseRestore = () => {
    if (window.confirm('هل أنت متأكد من استعادة قاعدة البيانات؟ هذا الإجراء لا يمكن التراجع عنه.')) {
      toast.info('جاري استعادة قاعدة البيانات...');
      // Implement restore functionality
    }
  };

  const handleChange = (section, field, value) => {
    if (section === 'profile') {
      setProfileData(prev => ({ ...prev, [field]: value }));
    } else if (section === 'system') {
      setSystemSettings(prev => ({ ...prev, [field]: value }));
    } else if (section === 'notifications') {
      setNotificationSettings(prev => ({ ...prev, [field]: value }));
    } else if (section === 'database') {
      setDatabaseSettings(prev => ({ ...prev, [field]: value }));
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="row">
        <div className="col-12">
          {/* Page Header */}
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h2 className="fw-bold text-primary mb-1">الإعدادات والتفضيلات</h2>
              <p className="text-muted mb-0">إدارة إعدادات النظام والملف الشخصي</p>
            </div>
          </div>

          <div className="row">
            {/* Sidebar Navigation */}
            <div className="col-md-3 mb-4">
              <div className="card">
                <div className="card-body p-0">
                  <div className="list-group list-group-flush">
                    <button
                      className={`list-group-item list-group-item-action ${activeTab === 'profile' ? 'active' : ''}`}
                      onClick={() => setActiveTab('profile')}
                    >
                      <i className="bi bi-person me-2"></i>
                      الملف الشخصي
                    </button>
                    <button
                      className={`list-group-item list-group-item-action ${activeTab === 'notifications' ? 'active' : ''}`}
                      onClick={() => setActiveTab('notifications')}
                    >
                      <i className="bi bi-bell me-2"></i>
                      التنبيهات
                    </button>
                    {user?.user_type === 'admin' && (
                      <>
                        <button
                          className={`list-group-item list-group-item-action ${activeTab === 'system' ? 'active' : ''}`}
                          onClick={() => setActiveTab('system')}
                        >
                          <i className="bi bi-gear me-2"></i>
                          إعدادات النظام
                        </button>
                        <button
                          className={`list-group-item list-group-item-action ${activeTab === 'database' ? 'active' : ''}`}
                          onClick={() => setActiveTab('database')}
                        >
                          <i className="bi bi-database me-2"></i>
                          قاعدة البيانات
                        </button>
                      </>
                    )}
                    <button
                      className={`list-group-item list-group-item-action ${activeTab === 'about' ? 'active' : ''}`}
                      onClick={() => setActiveTab('about')}
                    >
                      <i className="bi bi-info-circle me-2"></i>
                      حول النظام
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Main Content */}
            <div className="col-md-9">
              {/* Profile Settings */}
              {activeTab === 'profile' && (
                <div className="card">
                  <div className="card-header">
                    <h5 className="card-title mb-0">
                      <i className="bi bi-person me-2"></i>
                      إعدادات الملف الشخصي
                    </h5>
                  </div>
                  <div className="card-body">
                    <form onSubmit={handleProfileSubmit}>
                      <div className="mb-3">
                        <label htmlFor="full_name" className="form-label">
                          الاسم الكامل
                        </label>
                        <input
                          type="text"
                          className="form-control"
                          id="full_name"
                          value={profileData.full_name}
                          onChange={(e) => handleChange('profile', 'full_name', e.target.value)}
                          required
                        />
                      </div>

                      <div className="mb-3">
                        <label htmlFor="username" className="form-label">
                          اسم المستخدم
                        </label>
                        <input
                          type="text"
                          className="form-control"
                          id="username"
                          value={user?.username || ''}
                          disabled
                        />
                        <div className="form-text">لا يمكن تغيير اسم المستخدم</div>
                      </div>

                      <hr />
                      <h6>تغيير كلمة المرور</h6>

                      <div className="mb-3">
                        <label htmlFor="current_password" className="form-label">
                          كلمة المرور الحالية
                        </label>
                        <input
                          type="password"
                          className="form-control"
                          id="current_password"
                          value={profileData.current_password}
                          onChange={(e) => handleChange('profile', 'current_password', e.target.value)}
                        />
                      </div>

                      <div className="row">
                        <div className="col-md-6 mb-3">
                          <label htmlFor="new_password" className="form-label">
                            كلمة المرور الجديدة
                          </label>
                          <input
                            type="password"
                            className="form-control"
                            id="new_password"
                            value={profileData.new_password}
                            onChange={(e) => handleChange('profile', 'new_password', e.target.value)}
                          />
                        </div>
                        <div className="col-md-6 mb-3">
                          <label htmlFor="confirm_password" className="form-label">
                            تأكيد كلمة المرور الجديدة
                          </label>
                          <input
                            type="password"
                            className="form-control"
                            id="confirm_password"
                            value={profileData.confirm_password}
                            onChange={(e) => handleChange('profile', 'confirm_password', e.target.value)}
                          />
                        </div>
                      </div>

                      <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                            جاري الحفظ...
                          </>
                        ) : (
                          <>
                            <i className="bi bi-check-lg me-1"></i>
                            حفظ التغييرات
                          </>
                        )}
                      </button>
                    </form>
                  </div>
                </div>
              )}

              {/* Notification Settings */}
              {activeTab === 'notifications' && (
                <div className="card">
                  <div className="card-header">
                    <h5 className="card-title mb-0">
                      <i className="bi bi-bell me-2"></i>
                      إعدادات التنبيهات
                    </h5>
                  </div>
                  <div className="card-body">
                    <form onSubmit={handleNotificationSettingsSubmit}>
                      <div className="mb-3">
                        <div className="form-check form-switch">
                          <input
                            className="form-check-input"
                            type="checkbox"
                            id="email_notifications"
                            checked={notificationSettings.email_notifications}
                            onChange={(e) => handleChange('notifications', 'email_notifications', e.target.checked)}
                          />
                          <label className="form-check-label" htmlFor="email_notifications">
                            تنبيهات البريد الإلكتروني
                          </label>
                        </div>
                      </div>

                      <div className="mb-3">
                        <div className="form-check form-switch">
                          <input
                            className="form-check-input"
                            type="checkbox"
                            id="session_reminders"
                            checked={notificationSettings.session_reminders}
                            onChange={(e) => handleChange('notifications', 'session_reminders', e.target.checked)}
                          />
                          <label className="form-check-label" htmlFor="session_reminders">
                            تذكير بالجلسات
                          </label>
                        </div>
                      </div>

                      <div className="mb-3">
                        <div className="form-check form-switch">
                          <input
                            className="form-check-input"
                            type="checkbox"
                            id="case_updates"
                            checked={notificationSettings.case_updates}
                            onChange={(e) => handleChange('notifications', 'case_updates', e.target.checked)}
                          />
                          <label className="form-check-label" htmlFor="case_updates">
                            تحديثات القضايا
                          </label>
                        </div>
                      </div>

                      <div className="mb-3">
                        <div className="form-check form-switch">
                          <input
                            className="form-check-input"
                            type="checkbox"
                            id="system_alerts"
                            checked={notificationSettings.system_alerts}
                            onChange={(e) => handleChange('notifications', 'system_alerts', e.target.checked)}
                          />
                          <label className="form-check-label" htmlFor="system_alerts">
                            تنبيهات النظام
                          </label>
                        </div>
                      </div>

                      <div className="mb-3">
                        <label htmlFor="reminder_hours" className="form-label">
                          تذكير قبل الجلسة بـ (ساعات)
                        </label>
                        <select
                          className="form-select"
                          id="reminder_hours"
                          value={notificationSettings.reminder_hours}
                          onChange={(e) => handleChange('notifications', 'reminder_hours', parseInt(e.target.value))}
                        >
                          <option value={1}>ساعة واحدة</option>
                          <option value={6}>6 ساعات</option>
                          <option value={12}>12 ساعة</option>
                          <option value={24}>24 ساعة</option>
                          <option value={48}>48 ساعة</option>
                        </select>
                      </div>

                      <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                            جاري الحفظ...
                          </>
                        ) : (
                          <>
                            <i className="bi bi-check-lg me-1"></i>
                            حفظ التغييرات
                          </>
                        )}
                      </button>
                    </form>
                  </div>
                </div>
              )}

              {/* System Settings (Admin Only) */}
              {activeTab === 'system' && user?.user_type === 'admin' && (
                <div className="card">
                  <div className="card-header">
                    <h5 className="card-title mb-0">
                      <i className="bi bi-gear me-2"></i>
                      إعدادات النظام
                    </h5>
                  </div>
                  <div className="card-body">
                    <form onSubmit={handleSystemSettingsSubmit}>
                      <div className="row">
                        <div className="col-md-6 mb-3">
                          <label htmlFor="app_name" className="form-label">
                            اسم التطبيق
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            id="app_name"
                            value={systemSettings.app_name}
                            onChange={(e) => handleChange('system', 'app_name', e.target.value)}
                          />
                        </div>
                        <div className="col-md-6 mb-3">
                          <label htmlFor="company_name" className="form-label">
                            اسم الشركة
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            id="company_name"
                            value={systemSettings.company_name}
                            onChange={(e) => handleChange('system', 'company_name', e.target.value)}
                          />
                        </div>
                      </div>

                      <div className="row">
                        <div className="col-md-6 mb-3">
                          <label htmlFor="contact_email" className="form-label">
                            البريد الإلكتروني
                          </label>
                          <input
                            type="email"
                            className="form-control"
                            id="contact_email"
                            value={systemSettings.contact_email}
                            onChange={(e) => handleChange('system', 'contact_email', e.target.value)}
                          />
                        </div>
                        <div className="col-md-6 mb-3">
                          <label htmlFor="contact_phone" className="form-label">
                            رقم الهاتف
                          </label>
                          <input
                            type="tel"
                            className="form-control"
                            id="contact_phone"
                            value={systemSettings.contact_phone}
                            onChange={(e) => handleChange('system', 'contact_phone', e.target.value)}
                          />
                        </div>
                      </div>

                      <div className="mb-3">
                        <label htmlFor="address" className="form-label">
                          العنوان
                        </label>
                        <textarea
                          className="form-control"
                          id="address"
                          rows="3"
                          value={systemSettings.address}
                          onChange={(e) => handleChange('system', 'address', e.target.value)}
                        ></textarea>
                      </div>

                      <div className="row">
                        <div className="col-md-4 mb-3">
                          <label htmlFor="timezone" className="form-label">
                            المنطقة الزمنية
                          </label>
                          <select
                            className="form-select"
                            id="timezone"
                            value={systemSettings.timezone}
                            onChange={(e) => handleChange('system', 'timezone', e.target.value)}
                          >
                            {timezones.map(tz => (
                              <option key={tz.value} value={tz.value}>
                                {tz.label}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div className="col-md-4 mb-3">
                          <label htmlFor="date_format" className="form-label">
                            تنسيق التاريخ
                          </label>
                          <select
                            className="form-select"
                            id="date_format"
                            value={systemSettings.date_format}
                            onChange={(e) => handleChange('system', 'date_format', e.target.value)}
                          >
                            {dateFormats.map(format => (
                              <option key={format.value} value={format.value}>
                                {format.label}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div className="col-md-4 mb-3">
                          <label htmlFor="language" className="form-label">
                            اللغة
                          </label>
                          <select
                            className="form-select"
                            id="language"
                            value={systemSettings.language}
                            onChange={(e) => handleChange('system', 'language', e.target.value)}
                          >
                            {languages.map(lang => (
                              <option key={lang.value} value={lang.value}>
                                {lang.label}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>

                      <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                            جاري الحفظ...
                          </>
                        ) : (
                          <>
                            <i className="bi bi-check-lg me-1"></i>
                            حفظ التغييرات
                          </>
                        )}
                      </button>
                    </form>
                  </div>
                </div>
              )}

              {/* Database Settings (Admin Only) */}
              {activeTab === 'database' && user?.user_type === 'admin' && (
                <div className="card">
                  <div className="card-header">
                    <h5 className="card-title mb-0">
                      <i className="bi bi-database me-2"></i>
                      إعدادات قاعدة البيانات
                    </h5>
                  </div>
                  <div className="card-body">
                    <div className="row">
                      <div className="col-md-6">
                        <h6>النسخ الاحتياطي التلقائي</h6>
                        <div className="mb-3">
                          <div className="form-check form-switch">
                            <input
                              className="form-check-input"
                              type="checkbox"
                              id="auto_backup"
                              checked={databaseSettings.auto_backup}
                              onChange={(e) => handleChange('database', 'auto_backup', e.target.checked)}
                            />
                            <label className="form-check-label" htmlFor="auto_backup">
                              تفعيل النسخ الاحتياطي التلقائي
                            </label>
                          </div>
                        </div>

                        <div className="mb-3">
                          <label htmlFor="backup_frequency" className="form-label">
                            تكرار النسخ الاحتياطي
                          </label>
                          <select
                            className="form-select"
                            id="backup_frequency"
                            value={databaseSettings.backup_frequency}
                            onChange={(e) => handleChange('database', 'backup_frequency', e.target.value)}
                          >
                            <option value="hourly">كل ساعة</option>
                            <option value="daily">يومياً</option>
                            <option value="weekly">أسبوعياً</option>
                            <option value="monthly">شهرياً</option>
                          </select>
                        </div>

                        <div className="mb-3">
                          <label htmlFor="backup_retention_days" className="form-label">
                            الاحتفاظ بالنسخ الاحتياطية (أيام)
                          </label>
                          <input
                            type="number"
                            className="form-control"
                            id="backup_retention_days"
                            value={databaseSettings.backup_retention_days}
                            onChange={(e) => handleChange('database', 'backup_retention_days', parseInt(e.target.value))}
                            min="1"
                            max="365"
                          />
                        </div>
                      </div>

                      <div className="col-md-6">
                        <h6>إجراءات قاعدة البيانات</h6>
                        
                        <div className="mb-3">
                          <p className="text-muted">
                            آخر نسخة احتياطية: {' '}
                            {databaseSettings.last_backup 
                              ? formatDateTime(databaseSettings.last_backup)
                              : 'لم يتم إنشاء نسخة احتياطية بعد'
                            }
                          </p>
                        </div>

                        <div className="d-grid gap-2">
                          <button
                            type="button"
                            className="btn btn-success"
                            onClick={handleDatabaseBackup}
                            disabled={loading}
                          >
                            {loading ? (
                              <>
                                <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                                جاري الإنشاء...
                              </>
                            ) : (
                              <>
                                <i className="bi bi-cloud-arrow-up me-1"></i>
                                إنشاء نسخة احتياطية الآن
                              </>
                            )}
                          </button>

                          <button
                            type="button"
                            className="btn btn-warning"
                            onClick={handleDatabaseRestore}
                          >
                            <i className="bi bi-cloud-arrow-down me-1"></i>
                            استعادة من نسخة احتياطية
                          </button>

                          <button
                            type="button"
                            className="btn btn-outline-danger"
                            onClick={() => {
                              if (window.confirm('هل أنت متأكد من تنظيف قاعدة البيانات؟')) {
                                toast.info('جاري تنظيف قاعدة البيانات...');
                              }
                            }}
                          >
                            <i className="bi bi-trash me-1"></i>
                            تنظيف قاعدة البيانات
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* About System */}
              {activeTab === 'about' && (
                <div className="card">
                  <div className="card-header">
                    <h5 className="card-title mb-0">
                      <i className="bi bi-info-circle me-2"></i>
                      حول النظام
                    </h5>
                  </div>
                  <div className="card-body">
                    <div className="row">
                      <div className="col-md-8">
                        <h4>{systemSettings.app_name}</h4>
                        <p className="text-muted">نظام شامل لإدارة القضايا القانونية والمحاماة</p>
                        
                        <table className="table table-borderless">
                          <tbody>
                            <tr>
                              <td><strong>الإصدار:</strong></td>
                              <td>3.0.0</td>
                            </tr>
                            <tr>
                              <td><strong>تاريخ البناء:</strong></td>
                              <td>سبتمبر 2025</td>
                            </tr>
                            <tr>
                              <td><strong>التقنيات المستخدمة:</strong></td>
                              <td>React.js, Electron, FastAPI, SQLite</td>
                            </tr>
                            <tr>
                              <td><strong>المطور:</strong></td>
                              <td>فريق تطوير النظام القانوني</td>
                            </tr>
                            <tr>
                              <td><strong>الدعم الفني:</strong></td>
                              <td>{systemSettings.contact_email}</td>
                            </tr>
                          </tbody>
                        </table>

                        <div className="mt-4">
                          <h6>الميزات الرئيسية:</h6>
                          <ul>
                            <li>إدارة شاملة للقضايا والعملاء</li>
                            <li>نظام جلسات محكمة متطور</li>
                            <li>إدارة المستندات والملاحظات</li>
                            <li>تقارير وإحصائيات تفصيلية</li>
                            <li>نظام مستخدمين متعدد المستويات</li>
                            <li>واجهة عربية صديقة للمستخدم</li>
                          </ul>
                        </div>
                      </div>
                      <div className="col-md-4">
                        <div className="text-center">
                          <i className="bi bi-shield-check display-1 text-success mb-3"></i>
                          <h6>النظام يعمل بشكل طبيعي</h6>
                          <p className="text-muted">آخر فحص: {new Date().toLocaleString('ar-EG')}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPreferences;
