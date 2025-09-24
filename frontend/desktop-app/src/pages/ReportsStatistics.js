import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import apiService from '../services/api';
import { formatShortDate } from '../utils-helper';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const ReportsStatistics = () => {
  const [loading, setLoading] = useState(false);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [detailedStats, setDetailedStats] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [dateRange, setDateRange] = useState({
    start_date: '',
    end_date: ''
  });

  useEffect(() => {
    loadDashboardStats();
    loadDetailedStats();
  }, []);

  const loadDashboardStats = async () => {
    try {
      setLoading(true);
      const stats = await apiService.getDashboardStats();
      setDashboardStats(stats);
    } catch (error) {
      toast.error('فشل في تحميل الإحصائيات الأساسية');
    } finally {
      setLoading(false);
    }
  };

  const loadDetailedStats = async () => {
    try {
      const params = {};
      if (dateRange.start_date) params.start_date = dateRange.start_date;
      if (dateRange.end_date) params.end_date = dateRange.end_date;
      
      // Load additional statistics
      const [casesByType, casesByJudgment] = await Promise.all([
        apiService.getCasesByType(),
        apiService.getCasesByJudgment()
      ]);
      
      setDetailedStats({
        cases_by_type: casesByType,
        cases_by_judgment: casesByJudgment
      });
    } catch (error) {
      console.error('Error loading detailed stats:', error);
    }
  };

  const handleDateRangeChange = (e) => {
    const { name, value } = e.target;
    setDateRange(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const applyDateFilter = () => {
    loadDetailedStats();
  };

  const exportReport = async (format) => {
    try {
      setLoading(true);
      toast.info(`جاري تصدير التقرير بصيغة ${format}...`);
      
      const filters = {};
      if (dateRange.start_date) filters.date_from = dateRange.start_date;
      if (dateRange.end_date) filters.date_to = dateRange.end_date;
      
      let response;
      if (activeTab === 'general') {
        response = await apiService.exportSummaryReport(format.toLowerCase(), filters);
      } else if (activeTab === 'cases') {
        response = await apiService.exportCases(format.toLowerCase(), filters);
      } else if (activeTab === 'sessions') {
        response = await apiService.exportSessions(format.toLowerCase(), filters);
      } else {
        // Default to cases export
        response = await apiService.exportCases(format.toLowerCase(), filters);
      }
      
      if (response.ok) {
        // Create download link
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        // Get filename from response headers or create one
        const contentDisposition = response.headers.get('Content-Disposition');
        const filename = contentDisposition 
          ? contentDisposition.split('filename=')[1]?.replace(/"/g, '')
          : `تقرير_${activeTab}_${new Date().toISOString().split('T')[0]}.${format.toLowerCase()}`;
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        toast.success(`تم تصدير التقرير بنجاح`);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'فشل في تصدير التقرير');
      }
    } catch (error) {
      console.error('Export error:', error);
      toast.error(error.message || 'فشل في تصدير التقرير');
    } finally {
      setLoading(false);
    }
  };

  const printReport = () => {
    try {
      let printUrl;
      const filters = {};
      if (dateRange.start_date) filters.date_from = dateRange.start_date;
      if (dateRange.end_date) filters.date_to = dateRange.end_date;
      
      if (activeTab === 'general') {
        printUrl = apiService.getPrintDashboardUrl();
      } else if (activeTab === 'cases') {
        printUrl = apiService.getPrintCasesListUrl(filters);
      } else {
        printUrl = apiService.getPrintDashboardUrl();
      }
      
      // Open print page in new window
      const printWindow = window.open(printUrl, '_blank', 'width=800,height=600');
      if (printWindow) {
        toast.success('تم فتح نافذة الطباعة');
      } else {
        toast.error('تعذر فتح نافذة الطباعة');
      }
    } catch (error) {
      console.error('Print error:', error);
      toast.error('فشل في فتح نافذة الطباعة');
    }
  };

  // Chart configurations
  const casesByTypeChartData = {
    labels: dashboardStats?.cases_by_type?.slice(0, 10).map(item => item.name) || [],
    datasets: [
      {
        label: 'عدد القضايا',
        data: dashboardStats?.cases_by_type?.slice(0, 10).map(item => item.case_count) || [],
        backgroundColor: [
          '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
          '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
        ],
      },
    ],
  };

  const casesByJudgmentChartData = {
    labels: dashboardStats?.cases_by_judgment?.map(item => item.judgment_type) || [],
    datasets: [
      {
        label: 'عدد القضايا',
        data: dashboardStats?.cases_by_judgment?.map(item => item.case_count) || [],
        backgroundColor: ['#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0'],
      },
    ],
  };

  const monthlyTrendChartData = {
    labels: dashboardStats?.monthly_trend?.map(item => `${item.month}/${item.year}`) || [],
    datasets: [
      {
        label: 'القضايا الجديدة',
        data: dashboardStats?.monthly_trend?.map(item => item.new_cases) || [],
        backgroundColor: '#36A2EB',
      },
      {
        label: 'القضايا المنتهية',
        data: dashboardStats?.monthly_trend?.map(item => item.closed_cases) || [],
        backgroundColor: '#FF6384',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'إحصائيات القضايا',
      },
    },
  };

  if (loading && !dashboardStats) {
    return (
      <div className="container-fluid py-4">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">جاري التحميل...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid py-4">
      <div className="row">
        <div className="col-12">
          {/* Page Header */}
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h2 className="fw-bold text-primary mb-1">التقارير والإحصائيات</h2>
              <p className="text-muted mb-0">تحليل شامل لبيانات النظام والأداء</p>
            </div>
            <div className="d-flex gap-2">
              <button 
                className="btn btn-primary"
                onClick={printReport}
                title="طباعة التقرير"
              >
                <i className="bi bi-printer me-1"></i>
                طباعة
              </button>
              <div className="dropdown">
                <button 
                  className="btn btn-success dropdown-toggle" 
                  type="button" 
                  data-bs-toggle="dropdown"
                >
                  <i className="bi bi-download me-1"></i>
                  تصدير التقرير
                </button>
              <ul className="dropdown-menu">
                <li>
                  <button 
                    className="dropdown-item"
                    onClick={() => exportReport('PDF')}
                  >
                    <i className="bi bi-file-earmark-pdf me-2"></i>
                    PDF
                  </button>
                </li>
                <li>
                  <button 
                    className="dropdown-item"
                    onClick={() => exportReport('Excel')}
                  >
                    <i className="bi bi-file-earmark-excel me-2"></i>
                    Excel
                  </button>
                </li>
                <li>
                  <button 
                    className="dropdown-item"
                    onClick={() => exportReport('CSV')}
                  >
                    <i className="bi bi-file-earmark-text me-2"></i>
                    CSV
                  </button>
                </li>
                <li>
                  <button 
                    className="dropdown-item"
                    onClick={() => exportReport('JSON')}
                  >
                    <i className="bi bi-file-earmark-code me-2"></i>
                    JSON
                  </button>
                </li>
              </ul>
              </div>
            </div>
          </div>

          {/* Date Range Filter */}
          <div className="card mb-4">
            <div className="card-body">
              <div className="row align-items-end">
                <div className="col-md-3">
                  <label className="form-label">من تاريخ</label>
                  <input
                    type="date"
                    className="form-control"
                    name="start_date"
                    value={dateRange.start_date}
                    onChange={handleDateRangeChange}
                  />
                </div>
                <div className="col-md-3">
                  <label className="form-label">إلى تاريخ</label>
                  <input
                    type="date"
                    className="form-control"
                    name="end_date"
                    value={dateRange.end_date}
                    onChange={handleDateRangeChange}
                  />
                </div>
                <div className="col-md-2">
                  <button 
                    className="btn btn-primary w-100"
                    onClick={applyDateFilter}
                  >
                    تطبيق الفلتر
                  </button>
                </div>
                <div className="col-md-2">
                  <button 
                    className="btn btn-outline-secondary w-100"
                    onClick={() => {
                      setDateRange({ start_date: '', end_date: '' });
                      loadDetailedStats();
                    }}
                  >
                    إعادة تعيين
                  </button>
                </div>
                <div className="col-md-2">
                  <button 
                    className="btn btn-outline-primary w-100"
                    onClick={loadDashboardStats}
                    disabled={loading}
                  >
                    <i className="bi bi-arrow-clockwise me-1"></i>
                    تحديث
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Statistics Cards */}
          <div className="row mb-4">
            <div className="col-md-3">
              <div className="card bg-primary text-white">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <h4 className="fw-bold">{dashboardStats?.total_cases || 0}</h4>
                      <p className="mb-0">إجمالي القضايا</p>
                    </div>
                    <i className="bi bi-briefcase fs-1 opacity-50"></i>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="col-md-3">
              <div className="card bg-success text-white">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <h4 className="fw-bold">{dashboardStats?.total_users || 0}</h4>
                      <p className="mb-0">إجمالي المستخدمين</p>
                    </div>
                    <i className="bi bi-people fs-1 opacity-50"></i>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="col-md-3">
              <div className="card bg-info text-white">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <h4 className="fw-bold">{dashboardStats?.total_sessions || 0}</h4>
                      <p className="mb-0">إجمالي الجلسات</p>
                    </div>
                    <i className="bi bi-calendar-event fs-1 opacity-50"></i>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="col-md-3">
              <div className="card bg-warning text-white">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <h4 className="fw-bold">{dashboardStats?.total_notes || 0}</h4>
                      <p className="mb-0">إجمالي الملاحظات</p>
                    </div>
                    <i className="bi bi-journal-text fs-1 opacity-50"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Tabs Navigation */}
          <ul className="nav nav-tabs mb-4">
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                <i className="bi bi-pie-chart me-1"></i>
                نظرة عامة
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'cases' ? 'active' : ''}`}
                onClick={() => setActiveTab('cases')}
              >
                <i className="bi bi-briefcase me-1"></i>
                إحصائيات القضايا
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'trends' ? 'active' : ''}`}
                onClick={() => setActiveTab('trends')}
              >
                <i className="bi bi-graph-up me-1"></i>
                الاتجاهات الشهرية
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'details' ? 'active' : ''}`}
                onClick={() => setActiveTab('details')}
              >
                <i className="bi bi-table me-1"></i>
                تفاصيل مفصلة
              </button>
            </li>
          </ul>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div className="row">
              <div className="col-md-6 mb-4">
                <div className="card">
                  <div className="card-header">
                    <h6 className="card-title mb-0">توزيع القضايا حسب النوع</h6>
                  </div>
                  <div className="card-body">
                    {dashboardStats?.cases_by_type?.length > 0 ? (
                      <Pie data={casesByTypeChartData} options={chartOptions} />
                    ) : (
                      <div className="text-center py-4 text-muted">
                        لا توجد بيانات لعرضها
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="col-md-6 mb-4">
                <div className="card">
                  <div className="card-header">
                    <h6 className="card-title mb-0">توزيع القضايا حسب نوع الحكم</h6>
                  </div>
                  <div className="card-body">
                    {dashboardStats?.cases_by_judgment?.length > 0 ? (
                      <Pie data={casesByJudgmentChartData} options={chartOptions} />
                    ) : (
                      <div className="text-center py-4 text-muted">
                        لا توجد بيانات لعرضها
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'cases' && (
            <div className="row">
              <div className="col-12 mb-4">
                <div className="card">
                  <div className="card-header">
                    <h6 className="card-title mb-0">إحصائيات القضايا المفصلة</h6>
                  </div>
                  <div className="card-body">
                    <div className="table-responsive">
                      <table className="table table-striped">
                        <thead>
                          <tr>
                            <th>نوع القضية</th>
                            <th>عدد القضايا</th>
                            <th>النسبة المئوية</th>
                          </tr>
                        </thead>
                        <tbody>
                          {dashboardStats?.cases_by_type?.map((item, index) => (
                            <tr key={index}>
                              <td>{item.name}</td>
                              <td>
                                <span className="badge bg-primary">{item.case_count}</span>
                              </td>
                              <td>
                                {dashboardStats.total_cases > 0 
                                  ? `${((item.case_count / dashboardStats.total_cases) * 100).toFixed(1)}%`
                                  : '0%'
                                }
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'trends' && (
            <div className="row">
              <div className="col-12 mb-4">
                <div className="card">
                  <div className="card-header">
                    <h6 className="card-title mb-0">الاتجاهات الشهرية للقضايا</h6>
                  </div>
                  <div className="card-body">
                    {dashboardStats?.monthly_trend?.length > 0 ? (
                      <Bar data={monthlyTrendChartData} options={chartOptions} />
                    ) : (
                      <div className="text-center py-4 text-muted">
                        لا توجد بيانات اتجاهات شهرية
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'details' && (
            <div className="row">
              <div className="col-md-6 mb-4">
                <div className="card">
                  <div className="card-header">
                    <h6 className="card-title mb-0">الجلسات القادمة</h6>
                  </div>
                  <div className="card-body">
                    {dashboardStats?.upcoming_sessions?.length > 0 ? (
                      <div className="list-group list-group-flush">
                        {dashboardStats.upcoming_sessions.slice(0, 5).map((session, index) => (
                          <div key={index} className="list-group-item">
                            <div className="d-flex justify-content-between">
                              <span>{session.case_number}</span>
                              <small className="text-muted">
                                {new Date(session.session_datetime).toLocaleDateString('ar-EG')}
                              </small>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-4 text-muted">
                        لا توجد جلسات قادمة
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="col-md-6 mb-4">
                <div className="card">
                  <div className="card-header">
                    <h6 className="card-title mb-0">أحدث القضايا</h6>
                  </div>
                  <div className="card-body">
                    {dashboardStats?.recent_cases?.length > 0 ? (
                      <div className="list-group list-group-flush">
                        {dashboardStats.recent_cases.slice(0, 5).map((case_item, index) => (
                          <div key={index} className="list-group-item">
                            <div className="d-flex justify-content-between">
                              <div>
                                <strong>{case_item.case_number}</strong>
                                <br />
                                <small className="text-muted">{case_item.plaintiff}</small>
                              </div>
                              <small className="text-muted">
                                {new Date(case_item.created_at).toLocaleDateString('ar-EG')}
                              </small>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-4 text-muted">
                        لا توجد قضايا حديثة
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReportsStatistics;
