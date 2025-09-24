// CaseDetails.js - Case details view based on GET /cases/{case_id} endpoint
import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import apiService from '../services/api';
import { formatDate, formatDateTime } from '../utils-helper';

const CaseDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [case_data, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCaseDetails();
  }, [id]);

  const loadCaseDetails = async () => {
    try {
      setLoading(true);
      // Using GET /cases/{case_id} endpoint from api-helper.js
      const data = await apiService.getCase(parseInt(id));
      setCaseData(data);
    } catch (error) {
      console.error('Error loading case details:', error);
      if (error.message.includes('404') || error.message.includes('غير موجود')) {
        toast.error('القضية غير موجودة');
        navigate('/cases');
      } else {
        toast.error('خطأ في تحميل تفاصيل القضية');
      }
    } finally {
      setLoading(false);
    }
  };

  // Get judgment label and badge class
  const getJudgmentInfo = (type) => {
    const info = {
      pending: { label: 'قيد النظر', class: 'bg-warning' },
      won: { label: 'كسب القضية', class: 'bg-success' },
      lost: { label: 'خسارة القضية', class: 'bg-danger' },
      settled: { label: 'تسوية', class: 'bg-info' }
    };
    return info[type] || { label: type, class: 'bg-secondary' };
  };

  if (loading) {
    return (
      <div className="main-content">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">جاري التحميل...</span>
          </div>
          <p className="mt-3 text-muted">جاري تحميل تفاصيل القضية...</p>
        </div>
      </div>
    );
  }

  if (!case_data) {
    return (
      <div className="main-content">
        <div className="text-center">
          <i className="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
          <h3>القضية غير موجودة</h3>
          <p className="text-muted">لم يتم العثور على القضية المطلوبة</p>
          <Link to="/cases" className="btn btn-primary">
            العودة إلى القضايا
          </Link>
        </div>
      </div>
    );
  }

  const judgmentInfo = getJudgmentInfo(case_data.judgment_type);

  return (
    <div className="main-content">
      
      {/* Page Header */}
      <div className="d-flex justify-content-between align-items-start mb-4">
        <div>
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item">
                <Link to="/cases" className="text-decoration-none">القضايا</Link>
              </li>
              <li className="breadcrumb-item active">{case_data.case_number}</li>
            </ol>
          </nav>
          <h2 className="fw-bold text-primary mb-1">
            <i className="fas fa-gavel ms-2"></i>
            قضية رقم {case_data.case_number}
          </h2>
          <p className="text-muted mb-0">عرض تفاصيل القضية الكاملة</p>
        </div>
        
        <div className="btn-group">
          <Link 
            to={`/cases/${case_data.id}/edit`}
            className="btn btn-outline-success"
          >
            <i className="fas fa-edit ms-1"></i>
            تعديل
          </Link>
          <button 
            onClick={() => window.print()}
            className="btn btn-outline-primary"
          >
            <i className="fas fa-print ms-1"></i>
            طباعة
          </button>
          <button 
            onClick={loadCaseDetails}
            className="btn btn-outline-secondary"
          >
            <i className="fas fa-sync-alt ms-1"></i>
            تحديث
          </button>
        </div>
      </div>

      <div className="row g-4">
        
        {/* Main Case Information */}
        <div className="col-md-8">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h5 className="card-title mb-0">
                <i className="fas fa-info-circle ms-2"></i>
                معلومات القضية الأساسية
              </h5>
            </div>
            <div className="card-body">
              <div className="row g-4">
                
                <div className="col-md-6">
                  <div className="border rounded p-3 h-100">
                    <h6 className="fw-bold text-primary mb-3">
                      <i className="fas fa-hashtag ms-1"></i>
                      رقم القضية
                    </h6>
                    <p className="h4 text-dark mb-0">{case_data.case_number}</p>
                  </div>
                </div>

                <div className="col-md-6">
                  <div className="border rounded p-3 h-100">
                    <h6 className="fw-bold text-primary mb-3">
                      <i className="fas fa-balance-scale ms-1"></i>
                      حالة القضية
                    </h6>
                    <span className={`badge ${judgmentInfo.class} fs-6`}>
                      {judgmentInfo.label}
                    </span>
                  </div>
                </div>

                <div className="col-md-6">
                  <div className="border rounded p-3 h-100">
                    <h6 className="fw-bold text-primary mb-3">
                      <i className="fas fa-user-tie ms-1"></i>
                      المدعي
                    </h6>
                    <p className="mb-0">{case_data.plaintiff}</p>
                  </div>
                </div>

                <div className="col-md-6">
                  <div className="border rounded p-3 h-100">
                    <h6 className="fw-bold text-primary mb-3">
                      <i className="fas fa-user ms-1"></i>
                      المدعى عليه
                    </h6>
                    <p className="mb-0">{case_data.defendant}</p>
                  </div>
                </div>

                <div className="col-12">
                  <div className="border rounded p-3">
                    <h6 className="fw-bold text-primary mb-3">
                      <i className="fas fa-folder ms-1"></i>
                      نوع القضية
                    </h6>
                    <div className="d-flex align-items-center">
                      <span className="badge bg-light text-dark fs-6 ms-3">
                        {case_data.case_type?.name || 'غير محدد'}
                      </span>
                      {case_data.case_type?.description && (
                        <p className="text-muted mb-0">{case_data.case_type.description}</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Previous Judgment Reference */}
                {case_data.previous_judgment_id && (
                  <div className="col-12">
                    <div className="border rounded p-3 bg-light">
                      <h6 className="fw-bold text-primary mb-2">
                        <i className="fas fa-link ms-1"></i>
                        مرتبطة بقضية سابقة
                      </h6>
                      <p className="text-muted mb-0">
                        القضية رقم: {case_data.previous_judgment_id}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Case Metadata */}
        <div className="col-md-4">
          
          {/* Creation Info */}
          <div className="card mb-4">
            <div className="card-header">
              <h6 className="card-title mb-0">
                <i className="fas fa-clock ms-2 text-primary"></i>
                معلومات الإنشاء
              </h6>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <small className="text-muted d-block">تاريخ الإنشاء:</small>
                <strong>{case_data.created_at ? formatDate(case_data.created_at) : 'غير محدد'}</strong>
              </div>
              
              {case_data.created_by && (
                <div className="mb-3">
                  <small className="text-muted d-block">أنشئ بواسطة:</small>
                  <strong>{case_data.created_by.full_name}</strong>
                </div>
              )}

              {case_data.updated_at !== case_data.created_at && (
                <div className="mb-3">
                  <small className="text-muted d-block">آخر تحديث:</small>
                  <strong>{case_data.updated_at ? formatDate(case_data.updated_at) : 'غير محدد'}</strong>
                </div>
              )}

              {case_data.updated_by && case_data.updated_at !== case_data.created_at && (
                <div className="mb-0">
                  <small className="text-muted d-block">حُدث بواسطة:</small>
                  <strong>{case_data.updated_by.full_name}</strong>
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <div className="card-header">
              <h6 className="card-title mb-0">
                <i className="fas fa-bolt ms-2 text-primary"></i>
                إجراءات سريعة
              </h6>
            </div>
            <div className="card-body">
              <div className="d-grid gap-2">
                
                <Link 
                  to={`/cases/${case_data.id}/sessions`}
                  className="btn btn-outline-primary btn-sm"
                >
                  <i className="fas fa-calendar-alt ms-1"></i>
                  عرض الجلسات
                </Link>

                <Link 
                  to={`/cases/${case_data.id}/notes`}
                  className="btn btn-outline-info btn-sm"
                >
                  <i className="fas fa-sticky-note ms-1"></i>
                  عرض الملاحظات
                </Link>

                <Link 
                  to={`/cases/${case_data.id}/documents`}
                  className="btn btn-outline-success btn-sm"
                >
                  <i className="fas fa-paperclip ms-1"></i>
                  المرفقات
                </Link>

                <hr className="my-2" />

                <Link 
                  to={`/cases/${case_data.id}/edit`}
                  className="btn btn-success btn-sm"
                >
                  <i className="fas fa-edit ms-1"></i>
                  تعديل القضية
                </Link>

                <button 
                  className="btn btn-outline-danger btn-sm"
                  onClick={() => {
                    if (window.confirm('هل أنت متأكد من حذف هذه القضية؟')) {
                      // TODO: Implement delete functionality
                      toast.info('سيتم تطبيق وظيفة الحذف في المرحلة التالية');
                    }
                  }}
                >
                  <i className="fas fa-trash ms-1"></i>
                  حذف القضية
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Action Tabs - Preview for future phases */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <ul className="nav nav-tabs card-header-tabs">
                <li className="nav-item">
                  <a className="nav-link active" href="#overview">
                    <i className="fas fa-eye ms-1"></i>
                    نظرة عامة
                  </a>
                </li>
                <li className="nav-item">
                  <a className="nav-link disabled" href="#sessions">
                    <i className="fas fa-calendar-alt ms-1"></i>
                    الجلسات (قريباً)
                  </a>
                </li>
                <li className="nav-item">
                  <a className="nav-link disabled" href="#notes">
                    <i className="fas fa-sticky-note ms-1"></i>
                    الملاحظات (قريباً)
                  </a>
                </li>
                <li className="nav-item">
                  <a className="nav-link disabled" href="#timeline">
                    <i className="fas fa-history ms-1"></i>
                    المخطط الزمني (قريباً)
                  </a>
                </li>
              </ul>
            </div>
            <div className="card-body">
              <div className="text-center py-5">
                <i className="fas fa-info-circle fa-3x text-primary mb-3"></i>
                <h4>تفاصيل القضية - المرحلة الأولى</h4>
                <p className="text-muted mb-0">
                  سيتم إضافة المزيد من التفاصيل والوظائف في المراحل القادمة
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CaseDetails;
