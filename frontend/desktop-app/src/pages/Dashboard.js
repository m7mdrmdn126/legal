// Dashboard.js - Main dashboard based on GET /stats/dashboard endpoint
import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';
import apiService from '../services/api';
import { formatDate, formatShortDate } from '../utils-helper';
import useElectronChartResize from '../hooks/useElectronChartResize';
import '../styles/electron-charts.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const judgmentChartRef = useRef(null);
  const caseTypesChartRef = useRef(null);

  // Use custom hook for Electron chart resizing
  useElectronChartResize([judgmentChartRef, caseTypesChartRef], [stats]);

  useEffect(() => {
    loadDashboardStats();
  }, []);

  const loadDashboardStats = async () => {
    try {
      setLoading(true);
      // Using GET /stats/dashboard endpoint from api-helper.js
      const data = await apiService.getDashboardStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading dashboard stats:', error);
      toast.error('خطأ في تحميل إحصائيات لوحة التحكم');
    } finally {
      setLoading(false);
    }
  };

  // Chart data for judgment types - based on DashboardStats model
  const judgmentChartData = stats ? {
    labels: stats.cases_by_judgment?.map(item => {
      const labels = {
        pending: 'قيد النظر',
        won: 'كسب القضية',
        lost: 'خسارة القضية', 
        settled: 'تسوية'
      };
      return labels[item.judgment_type] || item.judgment_type;
    }) || [],
    datasets: [{
      data: stats.cases_by_judgment?.map(item => item.case_count) || [],
      backgroundColor: [
        '#f59e0b', // Gold for pending
        '#10b981', // Green for won
        '#ef4444', // Red for lost
        '#3b82f6'  // Blue for settled
      ],
      borderWidth: 0
    }]
  } : null;

  // Chart data for case types
  const caseTypesChartData = stats ? {
    labels: stats.cases_by_type?.map(item => item.name) || [],
    datasets: [{
      label: 'عدد القضايا',
      data: stats.cases_by_type?.map(item => item.case_count) || [],
      backgroundColor: '#1e40af',
      borderRadius: 4
    }]
  } : null;

  if (loading) {
    return (
      <div className="main-content">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">جاري التحميل...</span>
          </div>
          <p className="mt-3 text-muted">جاري تحميل لوحة التحكم...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="main-content">
      
      {/* Page Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold text-primary mb-1">لوحة التحكم</h2>
          <p className="text-muted mb-0">نظرة عامة على النشاط والإحصائيات</p>
        </div>
        <button 
          onClick={loadDashboardStats}
          className="btn btn-outline-primary"
          disabled={loading}
        >
          <i className="fas fa-sync-alt ms-1"></i>
          تحديث
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="row g-4 mb-5">
        <div className="col-md-6 col-lg-3">
          <div className="stat-card card h-100">
            <div className="card-body text-center">
              <div className="d-flex align-items-center justify-content-center mb-3">
                <div className="bg-primary bg-opacity-10 rounded-circle p-3">
                  <i className="fas fa-gavel fa-2x text-primary"></i>
                </div>
              </div>
              <h3 className="fw-bold text-primary mb-1">{stats?.total_cases || 0}</h3>
              <p className="text-muted mb-0">إجمالي القضايا</p>
            </div>
          </div>
        </div>

        <div className="col-md-6 col-lg-3">
          <div className="stat-card card h-100">
            <div className="card-body text-center">
              <div className="d-flex align-items-center justify-content-center mb-3">
                <div className="bg-success bg-opacity-10 rounded-circle p-3">
                  <i className="fas fa-users fa-2x text-success"></i>
                </div>
              </div>
              <h3 className="fw-bold text-success mb-1">{stats?.total_users || 0}</h3>
              <p className="text-muted mb-0">المستخدمين النشطين</p>
            </div>
          </div>
        </div>

        <div className="col-md-6 col-lg-3">
          <div className="stat-card card h-100">
            <div className="card-body text-center">
              <div className="d-flex align-items-center justify-content-center mb-3">
                <div className="bg-warning bg-opacity-10 rounded-circle p-3">
                  <i className="fas fa-calendar-alt fa-2x text-warning"></i>
                </div>
              </div>
              <h3 className="fw-bold text-warning mb-1">{stats?.total_sessions || 0}</h3>
              <p className="text-muted mb-0">جلسات المحكمة</p>
            </div>
          </div>
        </div>

        <div className="col-md-6 col-lg-3">
          <div className="stat-card card h-100">
            <div className="card-body text-center">
              <div className="d-flex align-items-center justify-content-center mb-3">
                <div className="bg-info bg-opacity-10 rounded-circle p-3">
                  <i className="fas fa-sticky-note fa-2x text-info"></i>
                </div>
              </div>
              <h3 className="fw-bold text-info mb-1">{stats?.total_notes || 0}</h3>
              <p className="text-muted mb-0">ملاحظات القضايا</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="row g-4 mb-5">
        
        {/* Judgment Types Chart */}
        <div className="col-md-6">
          <div className="card h-100">
            <div className="card-header bg-transparent border-bottom">
              <h5 className="card-title mb-0">
                <i className="fas fa-chart-pie ms-2 text-primary"></i>
                حالة القضايا
              </h5>
            </div>
            <div className="card-body chart-container pie-chart-container">
              {judgmentChartData && (
                <Pie 
                  ref={judgmentChartRef}
                  data={judgmentChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'bottom',
                      }
                    },
                    // Electron-specific optimizations
                    animation: {
                      duration: 0
                    },
                    layout: {
                      padding: 10
                    }
                  }}
                />
              )}
            </div>
          </div>
        </div>

        {/* Case Types Chart */}
        <div className="col-md-6">
          <div className="card h-100">
            <div className="card-header bg-transparent border-bottom">
              <h5 className="card-title mb-0">
                <i className="fas fa-chart-bar ms-2 text-primary"></i>
                أنواع القضايا
              </h5>
            </div>
            <div className="card-body chart-container bar-chart-container">
              {caseTypesChartData && (
                <Bar 
                  ref={caseTypesChartRef}
                  data={caseTypesChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        display: false
                      }
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        ticks: {
                          maxTicksLimit: 10,
                          // Remove stepSize: 1 to let Chart.js auto-calculate appropriate intervals
                          callback: function(value) {
                            // Only show integer values
                            return Number.isInteger(value) ? value : '';
                          }
                        }
                      }
                    },
                    // Electron-specific optimizations
                    animation: {
                      duration: 0
                    },
                    layout: {
                      padding: 10
                    }
                  }}
                />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="row g-4">
        
        {/* Recent Cases */}
        <div className="col-md-6">
          <div className="card">
            <div className="card-header bg-transparent border-bottom d-flex justify-content-between align-items-center">
              <h5 className="card-title mb-0">
                <i className="fas fa-clock ms-2 text-primary"></i>
                أحدث القضايا
              </h5>
              <Link to="/cases" className="btn btn-sm btn-outline-primary">
                عرض الكل
              </Link>
            </div>
            <div className="card-body p-0">
              {stats?.recent_cases?.length > 0 ? (
                <div className="list-group list-group-flush">
                  {stats.recent_cases.slice(0, 5).map((case_item) => (
                    <div key={case_item.id} className="list-group-item">
                      <div className="d-flex justify-content-between">
                        <div>
                          <h6 className="mb-1 text-primary">{case_item.case_number}</h6>
                          <p className="mb-1 small">{case_item.plaintiff} ضد {case_item.defendant}</p>
                          <small className="text-muted">{case_item.case_type_name}</small>
                        </div>
                        <div className="text-end">
                          <span className={`badge ${
                            case_item.judgment_type === 'pending' ? 'bg-warning' :
                            case_item.judgment_type === 'won' ? 'bg-success' :
                            case_item.judgment_type === 'lost' ? 'bg-danger' : 'bg-info'
                          }`}>
                            {case_item.judgment_type === 'pending' ? 'قيد النظر' :
                             case_item.judgment_type === 'won' ? 'كسب' :
                             case_item.judgment_type === 'lost' ? 'خسارة' : 'تسوية'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <i className="fas fa-inbox fa-2x text-muted mb-3"></i>
                  <p className="text-muted">لا توجد قضايا حديثة</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Upcoming Sessions */}
        <div className="col-md-6">
          <div className="card">
            <div className="card-header bg-transparent border-bottom d-flex justify-content-between align-items-center">
              <h5 className="card-title mb-0">
                <i className="fas fa-calendar-check ms-2 text-primary"></i>
                الجلسات القادمة
              </h5>
              <Link to="/cases" className="btn btn-sm btn-outline-primary">
                عرض الكل
              </Link>
            </div>
            <div className="card-body p-0">
              {stats?.upcoming_sessions?.length > 0 ? (
                <div className="list-group list-group-flush">
                  {stats.upcoming_sessions.slice(0, 5).map((session, index) => (
                    <div key={index} className="list-group-item">
                      <div className="d-flex justify-content-between">
                        <div>
                          <h6 className="mb-1 text-primary">{session.case_number}</h6>
                          <p className="mb-1 small">{session.plaintiff} ضد {session.defendant}</p>
                          <small className="text-muted">{session.session_notes}</small>
                        </div>
                        <div className="text-end">
                          <small className="text-muted">
                            {formatShortDate(session.session_date)}
                          </small>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <i className="fas fa-calendar-times fa-2x text-muted mb-3"></i>
                  <p className="text-muted">لا توجد جلسات قادمة</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};

export default Dashboard;
