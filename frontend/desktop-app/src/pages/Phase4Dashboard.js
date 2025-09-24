import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import apiService from '../services/api';

const Phase4Dashboard = () => {
  const [systemMetrics, setSystemMetrics] = useState(null);
  const [backups, setBackups] = useState([]);
  const [performanceLogs, setPerformanceLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadSystemData();
  }, []);

  const loadSystemData = async () => {
    setLoading(true);
    try {
      // Load system metrics
      const metricsResponse = await apiService.getSystemMetrics();
      setSystemMetrics(metricsResponse);

      // Load backups
      const backupsResponse = await apiService.listBackups();
      setBackups(backupsResponse.backups || []);

      // Load performance logs
      const logsResponse = await apiService.getPerformanceLogs(20);
      setPerformanceLogs(logsResponse.logs || []);

    } catch (error) {
      console.error('Error loading system data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBackup = async () => {
    try {
      setLoading(true);
      await apiService.createDatabaseBackup();
      toast.success('تم إنشاء النسخة الاحتياطية بنجاح');
      loadSystemData(); // Refresh data
    } catch (error) {
      toast.error('فشل في إنشاء النسخة الاحتياطية');
    } finally {
      setLoading(false);
    }
  };

  const handleOptimizeSystem = async () => {
    try {
      setLoading(true);
      await apiService.optimizeSystem();
      toast.success('تم بدء تحسين النظام');
    } catch (error) {
      toast.error('فشل في تحسين النظام');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format, type) => {
    try {
      let response;
      
      if (type === 'cases') {
        response = await apiService.exportCases(format);
      } else if (type === 'sessions') {
        response = await apiService.exportSessions(format);
      }
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${type}_export.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success(`تم تصدير ${type} بصيغة ${format}`);
    } catch (error) {
      toast.error('فشل في التصدير');
    }
  };

  const handlePrint = (type) => {
    let printUrl;
    
    if (type === 'dashboard') {
      printUrl = apiService.getPrintDashboardUrl();
    } else if (type === 'cases') {
      printUrl = apiService.getPrintCasesListUrl();
    }
    
    window.open(printUrl, '_blank');
  };

  return (
    <div className="container-fluid py-4">
      <div className="row">
        <div className="col-12">
          {/* Header */}
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h2 className="fw-bold text-primary mb-1">لوحة تحكم النظام المتقدمة</h2>
              <p className="text-muted mb-0">Phase 4 - إدارة متقدمة ومراقبة الأداء</p>
            </div>
            <div>
              <button 
                className="btn btn-outline-primary me-2"
                onClick={loadSystemData}
                disabled={loading}
              >
                <i className="bi bi-arrow-clockwise me-1"></i>
                تحديث البيانات
              </button>
            </div>
          </div>

          {/* Navigation Tabs */}
          <ul className="nav nav-tabs mb-4">
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                <i className="bi bi-speedometer2 me-1"></i>
                نظرة عامة
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'backups' ? 'active' : ''}`}
                onClick={() => setActiveTab('backups')}
              >
                <i className="bi bi-shield-check me-1"></i>
                النسخ الاحتياطية
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'export' ? 'active' : ''}`}
                onClick={() => setActiveTab('export')}
              >
                <i className="bi bi-download me-1"></i>
                التصدير والطباعة
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'performance' ? 'active' : ''}`}
                onClick={() => setActiveTab('performance')}
              >
                <i className="bi bi-graph-up me-1"></i>
                مراقبة الأداء
              </button>
            </li>
          </ul>

          {/* Tab Content */}
          {activeTab === 'overview' && systemMetrics && (
            <div className="row">
              <div className="col-md-3 mb-3">
                <div className="card text-center">
                  <div className="card-body">
                    <h5 className="card-title text-info">استخدام المعالج</h5>
                    <h2 className="text-primary">{systemMetrics.cpu_percent}%</h2>
                  </div>
                </div>
              </div>
              <div className="col-md-3 mb-3">
                <div className="card text-center">
                  <div className="card-body">
                    <h5 className="card-title text-warning">استخدام الذاكرة</h5>
                    <h2 className="text-primary">{systemMetrics.memory_percent}%</h2>
                  </div>
                </div>
              </div>
              <div className="col-md-3 mb-3">
                <div className="card text-center">
                  <div className="card-body">
                    <h5 className="card-title text-success">استخدام القرص</h5>
                    <h2 className="text-primary">{systemMetrics.disk_usage_percent}%</h2>
                  </div>
                </div>
              </div>
              <div className="col-md-3 mb-3">
                <div className="card text-center">
                  <div className="card-body">
                    <h5 className="card-title text-secondary">حجم قاعدة البيانات</h5>
                    <h2 className="text-primary">{systemMetrics.database_size_mb} MB</h2>
                  </div>
                </div>
              </div>
              
              <div className="col-12">
                <div className="card">
                  <div className="card-header">
                    <h5 className="card-title mb-0">
                      <i className="bi bi-tools me-2"></i>
                      أدوات إدارة النظام
                    </h5>
                  </div>
                  <div className="card-body">
                    <div className="row">
                      <div className="col-md-4 mb-3">
                        <button 
                          className="btn btn-success w-100"
                          onClick={handleCreateBackup}
                          disabled={loading}
                        >
                          <i className="bi bi-shield-plus me-2"></i>
                          إنشاء نسخة احتياطية
                        </button>
                      </div>
                      <div className="col-md-4 mb-3">
                        <button 
                          className="btn btn-warning w-100"
                          onClick={handleOptimizeSystem}
                          disabled={loading}
                        >
                          <i className="bi bi-gear-fill me-2"></i>
                          تحسين النظام
                        </button>
                      </div>
                      <div className="col-md-4 mb-3">
                        <button 
                          className="btn btn-info w-100"
                          onClick={() => handlePrint('dashboard')}
                        >
                          <i className="bi bi-printer me-2"></i>
                          طباعة لوحة التحكم
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'backups' && (
            <div className="card">
              <div className="card-header d-flex justify-content-between">
                <h5 className="card-title mb-0">النسخ الاحتياطية</h5>
                <button 
                  className="btn btn-primary btn-sm"
                  onClick={handleCreateBackup}
                  disabled={loading}
                >
                  <i className="bi bi-plus me-1"></i>
                  إنشاء نسخة جديدة
                </button>
              </div>
              <div className="card-body">
                {backups.length === 0 ? (
                  <div className="text-center py-4">
                    <i className="bi bi-archive display-1 text-muted"></i>
                    <p className="text-muted mt-3">لا توجد نسخ احتياطية</p>
                  </div>
                ) : (
                  <div className="table-responsive">
                    <table className="table">
                      <thead>
                        <tr>
                          <th>اسم النسخة</th>
                          <th>الحجم</th>
                          <th>تاريخ الإنشاء</th>
                          <th>المنشئ</th>
                          <th>الإجراءات</th>
                        </tr>
                      </thead>
                      <tbody>
                        {backups.map(backup => (
                          <tr key={backup.id}>
                            <td>{backup.backup_name}</td>
                            <td>{backup.size_mb} MB</td>
                            <td>{new Date(backup.created_at).toLocaleString('ar-EG')}</td>
                            <td>{backup.creator_name}</td>
                            <td>
                              <div className="btn-group btn-group-sm">
                                <button 
                                  className="btn btn-outline-primary"
                                  onClick={() => window.open(apiService.downloadBackup(backup.id))}
                                >
                                  <i className="bi bi-download"></i>
                                </button>
                                <button 
                                  className="btn btn-outline-success"
                                  onClick={() => {
                                    if (window.confirm('هل تريد استعادة هذه النسخة؟')) {
                                      // Handle restore
                                    }
                                  }}
                                >
                                  <i className="bi bi-arrow-clockwise"></i>
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'export' && (
            <div className="row">
              <div className="col-md-6">
                <div className="card">
                  <div className="card-header">
                    <h5 className="card-title mb-0">تصدير البيانات</h5>
                  </div>
                  <div className="card-body">
                    <h6>تصدير القضايا</h6>
                    <div className="btn-group mb-3">
                      <button 
                        className="btn btn-outline-primary"
                        onClick={() => handleExport('csv', 'cases')}
                      >
                        CSV
                      </button>
                      <button 
                        className="btn btn-outline-primary"
                        onClick={() => handleExport('json', 'cases')}
                      >
                        JSON
                      </button>
                      <button 
                        className="btn btn-outline-primary"
                        onClick={() => handleExport('excel', 'cases')}
                      >
                        Excel
                      </button>
                    </div>
                    
                    <h6>تصدير الجلسات</h6>
                    <div className="btn-group">
                      <button 
                        className="btn btn-outline-success"
                        onClick={() => handleExport('csv', 'sessions')}
                      >
                        CSV
                      </button>
                      <button 
                        className="btn btn-outline-success"
                        onClick={() => handleExport('json', 'sessions')}
                      >
                        JSON
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="col-md-6">
                <div className="card">
                  <div className="card-header">
                    <h5 className="card-title mb-0">طباعة التقارير</h5>
                  </div>
                  <div className="card-body">
                    <div className="d-grid gap-2">
                      <button 
                        className="btn btn-info"
                        onClick={() => handlePrint('dashboard')}
                      >
                        <i className="bi bi-printer me-2"></i>
                        طباعة لوحة التحكم
                      </button>
                      <button 
                        className="btn btn-info"
                        onClick={() => handlePrint('cases')}
                      >
                        <i className="bi bi-printer me-2"></i>
                        طباعة قائمة القضايا
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'performance' && (
            <div className="card">
              <div className="card-header">
                <h5 className="card-title mb-0">سجلات الأداء</h5>
              </div>
              <div className="card-body">
                {performanceLogs.length === 0 ? (
                  <div className="text-center py-4">
                    <i className="bi bi-graph-up display-1 text-muted"></i>
                    <p className="text-muted mt-3">لا توجد سجلات أداء</p>
                  </div>
                ) : (
                  <div className="table-responsive">
                    <table className="table table-sm">
                      <thead>
                        <tr>
                          <th>الوقت</th>
                          <th>نوع العملية</th>
                          <th>المدة (مللي ثانية)</th>
                          <th>استخدام الذاكرة</th>
                          <th>استخدام المعالج</th>
                        </tr>
                      </thead>
                      <tbody>
                        {performanceLogs.slice(0, 10).map((log, index) => (
                          <tr key={index}>
                            <td>{new Date(log.timestamp).toLocaleTimeString('ar-EG')}</td>
                            <td>{log.operation_type}</td>
                            <td>{log.duration_ms}</td>
                            <td>{log.memory_usage_mb?.toFixed(1)} MB</td>
                            <td>{log.cpu_percent}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          {loading && (
            <div className="position-fixed top-50 start-50 translate-middle">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">جاري التحميل...</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Phase4Dashboard;
