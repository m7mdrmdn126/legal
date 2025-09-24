// CasesList.js - Cases list with search based on GET /cases endpoint
import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import apiService from '../services/api';

const CasesList = () => {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    size: 10,
    total: 0,
    total_pages: 0
  });
  const [filters, setFilters] = useState({
    search: '',
    case_type_id: '',
    judgment_type: ''
  });
  const [caseTypes, setCaseTypes] = useState([]);

  // Load case types for filter dropdown
  useEffect(() => {
    loadCaseTypes();
  }, []);

  // Load cases when pagination or filters change
  useEffect(() => {
    loadCases();
  }, [pagination.page, filters]);

  const loadCaseTypes = async () => {
    try {
      // Using GET /case-types endpoint
      const response = await apiService.getCaseTypes(1, 100); // Get all case types
      setCaseTypes(response.items || []);
    } catch (error) {
      console.error('Error loading case types:', error);
    }
  };

  const loadCases = async () => {
    try {
      setLoading(true);
      
      // Using GET /cases endpoint with filters - based on api-helper.js
      const params = {
        page: pagination.page,
        size: pagination.size,
        search: filters.search.trim(),
        case_type_id: filters.case_type_id || null,
        judgment_type: filters.judgment_type || null
      };

      const response = await apiService.getCases(params);
      
      setCases(response.items || []);
      setPagination(prev => ({
        ...prev,
        total: response.total || 0,
        total_pages: response.total_pages || 0
      }));
      
    } catch (error) {
      console.error('Error loading cases:', error);
      toast.error('خطأ في تحميل القضايا');
    } finally {
      setLoading(false);
    }
  };

  // Debounced search function
  const debouncedSearch = useCallback(
    debounce((searchTerm) => {
      setFilters(prev => ({ ...prev, search: searchTerm }));
      setPagination(prev => ({ ...prev, page: 1 }));
    }, 300),
    []
  );

  const handleSearchChange = (e) => {
    const value = e.target.value;
    setFilters(prev => ({ ...prev, search: value }));
    debouncedSearch(value);
  };

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({ ...prev, [filterName]: value }));
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handlePageChange = (newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }));
  };

  // Judgment type labels - based on constants from utils-helper.js
  const getJudgmentLabel = (type) => {
    const labels = {
      pending: 'قيد النظر',
      won: 'كسب القضية',
      lost: 'خسارة القضية',
      settled: 'تسوية'
    };
    return labels[type] || type;
  };

  const getJudgmentBadgeClass = (type) => {
    const classes = {
      pending: 'bg-warning',
      won: 'bg-success',
      lost: 'bg-danger',
      settled: 'bg-info'
    };
    return classes[type] || 'bg-secondary';
  };

  return (
    <div className="main-content">
      
      {/* Page Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold text-primary mb-1">إدارة القضايا</h2>
          <p className="text-muted mb-0">عرض وإدارة جميع القضايا القانونية</p>
        </div>
        <Link to="/cases/new" className="btn btn-primary">
          <i className="fas fa-plus ms-1"></i>
          إضافة قضية جديدة
        </Link>
      </div>

      {/* Filters */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row g-3">
            
            {/* Search Input - supports Arabic search with diacritics */}
            <div className="col-md-4">
              <label className="form-label fw-semibold">البحث</label>
              <div className="input-group">
                <input
                  type="text"
                  className="form-control"
                  placeholder="البحث في رقم القضية، المدعي، المدعى عليه..."
                  value={filters.search}
                  onChange={handleSearchChange}
                />
                <span className="input-group-text">
                  <i className="fas fa-search text-muted"></i>
                </span>
              </div>
              <small className="form-text text-muted">
                يدعم البحث النص العربي مع علامات التشكيل
              </small>
            </div>

            {/* Case Type Filter */}
            <div className="col-md-3">
              <label className="form-label fw-semibold">نوع القضية</label>
              <select
                className="form-select"
                value={filters.case_type_id}
                onChange={(e) => handleFilterChange('case_type_id', e.target.value)}
              >
                <option value="">جميع الأنواع</option>
                {caseTypes.map(type => (
                  <option key={type.id} value={type.id}>
                    {type.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Judgment Type Filter */}
            <div className="col-md-3">
              <label className="form-label fw-semibold">حالة القضية</label>
              <select
                className="form-select"
                value={filters.judgment_type}
                onChange={(e) => handleFilterChange('judgment_type', e.target.value)}
              >
                <option value="">جميع الحالات</option>
                <option value="pending">قيد النظر</option>
                <option value="won">كسب القضية</option>
                <option value="lost">خسارة القضية</option>
                <option value="settled">تسوية</option>
              </select>
            </div>

            {/* Refresh Button */}
            <div className="col-md-2 d-flex align-items-end">
              <button 
                onClick={loadCases}
                className="btn btn-outline-primary w-100"
                disabled={loading}
              >
                <i className="fas fa-sync-alt ms-1"></i>
                تحديث
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Results Summary */}
      <div className="d-flex justify-content-between align-items-center mb-3">
        <div>
          <span className="text-muted">
            عرض {cases.length} من أصل {pagination.total} قضية
            {filters.search && (
              <span className="ms-2">
                - البحث عن: <strong>"{filters.search}"</strong>
              </span>
            )}
          </span>
        </div>
        
        {/* Page Size Selector */}
        <div className="d-flex align-items-center">
          <label className="form-label mb-0 ms-2">عرض:</label>
          <select
            className="form-select form-select-sm"
            style={{ width: 'auto' }}
            value={pagination.size}
            onChange={(e) => {
              setPagination(prev => ({ 
                ...prev, 
                size: parseInt(e.target.value),
                page: 1 
              }));
            }}
          >
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
          </select>
        </div>
      </div>

      {/* Cases Table */}
      <div className="card">
        <div className="table-responsive">
          <table className="table table-hover mb-0">
            <thead>
              <tr>
                <th>رقم القضية</th>
                <th>المدعي</th>
                <th>المدعى عليه</th>
                <th>نوع القضية</th>
                <th>الحالة</th>
                <th>تاريخ الإنشاء</th>
                <th>الإجراءات</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="7" className="text-center py-4">
                    <div className="spinner-border text-primary" role="status">
                      <span className="visually-hidden">جاري التحميل...</span>
                    </div>
                  </td>
                </tr>
              ) : cases.length > 0 ? (
                cases.map((case_item) => (
                  <tr key={case_item.id}>
                    <td>
                      <Link 
                        to={`/cases/${case_item.id}`}
                        className="text-primary text-decoration-none fw-semibold"
                      >
                        {case_item.case_number}
                      </Link>
                    </td>
                    <td>{case_item.plaintiff}</td>
                    <td>{case_item.defendant}</td>
                    <td>
                      <span className="badge bg-light text-dark">
                        {case_item.case_type?.name || 'غير محدد'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${getJudgmentBadgeClass(case_item.judgment_type)}`}>
                        {getJudgmentLabel(case_item.judgment_type)}
                      </span>
                    </td>
                    <td>
                      <small className="text-muted">
                        {new Date(case_item.created_at).toLocaleDateString('ar-SA')}
                      </small>
                    </td>
                    <td>
                      <div className="btn-group btn-group-sm">
                        <Link 
                          to={`/cases/${case_item.id}`}
                          className="btn btn-outline-primary"
                          title="عرض التفاصيل"
                        >
                          <i className="fas fa-eye"></i>
                        </Link>
                        <Link 
                          to={`/cases/${case_item.id}/edit`}
                          className="btn btn-outline-success"
                          title="تعديل"
                        >
                          <i className="fas fa-edit"></i>
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" className="text-center py-5">
                    <i className="fas fa-inbox fa-3x text-muted mb-3"></i>
                    <p className="text-muted mb-0">
                      {filters.search ? 'لا توجد قضايا تطابق البحث' : 'لا توجد قضايا'}
                    </p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {pagination.total_pages > 1 && (
          <div className="card-footer bg-transparent">
            <nav aria-label="تنقل بين الصفحات">
              <ul className="pagination justify-content-center mb-0">
                
                {/* Previous Button */}
                <li className={`page-item ${pagination.page === 1 ? 'disabled' : ''}`}>
                  <button 
                    className="page-link"
                    onClick={() => handlePageChange(pagination.page - 1)}
                    disabled={pagination.page === 1}
                  >
                    السابق
                  </button>
                </li>

                {/* Page Numbers */}
                {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                  let pageNum;
                  if (pagination.total_pages <= 5) {
                    pageNum = i + 1;
                  } else if (pagination.page <= 3) {
                    pageNum = i + 1;
                  } else if (pagination.page >= pagination.total_pages - 2) {
                    pageNum = pagination.total_pages - 4 + i;
                  } else {
                    pageNum = pagination.page - 2 + i;
                  }

                  return (
                    <li key={pageNum} className={`page-item ${pagination.page === pageNum ? 'active' : ''}`}>
                      <button 
                        className="page-link"
                        onClick={() => handlePageChange(pageNum)}
                      >
                        {pageNum}
                      </button>
                    </li>
                  );
                })}

                {/* Next Button */}
                <li className={`page-item ${pagination.page === pagination.total_pages ? 'disabled' : ''}`}>
                  <button 
                    className="page-link"
                    onClick={() => handlePageChange(pagination.page + 1)}
                    disabled={pagination.page === pagination.total_pages}
                  >
                    التالي
                  </button>
                </li>
              </ul>
            </nav>

            {/* Page Info */}
            <div className="text-center mt-2">
              <small className="text-muted">
                صفحة {pagination.page} من {pagination.total_pages} 
                ({pagination.total} قضية إجمالي)
              </small>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Debounce utility function
function debounce(func, wait) {
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

export default CasesList;
