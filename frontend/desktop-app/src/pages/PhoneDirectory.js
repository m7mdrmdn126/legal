import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-toastify';
import apiService from '../services/api';
import { useAuth } from '../context/AuthContext';

// Utility function for debouncing
const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

const PhoneDirectory = () => {
  const { isAdmin } = useAuth();
  
  // State management
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    الاسم: '',
    الرقم: '',
    الجهه: ''
  });
  
  // Pagination state
  const [pagination, setPagination] = useState({
    page: 1,
    size: 10,
    total: 0,
    pages: 0
  });
  
  // Search filters
  const [filters, setFilters] = useState({
    search: '',
    الاسم: '',
    الرقم: '',
    الجهه: ''
  });
  
  const [activeFilter, setActiveFilter] = useState('all'); // 'all', 'name', 'phone', 'organization'

  // Load entries on component mount and when pagination/filters change
  useEffect(() => {
    loadEntries();
  }, [pagination.page, filters]);

  const loadEntries = async () => {
    try {
      setLoading(true);
      
      const params = {
        page: pagination.page,
        size: pagination.size,
        search: filters.search.trim(),
        الاسم: filters.الاسم.trim() || null,
        الرقم: filters.الرقم.trim() || null,
        الجهه: filters.الجهه.trim() || null
      };

      const response = await apiService.getPhoneDirectoryEntries(params);
      
      setEntries(response.items || []);
      setPagination(prev => ({
        ...prev,
        total: response.total || 0,
        pages: response.pages || 0
      }));
      
    } catch (error) {
      console.error('Error loading phone directory:', error);
      toast.error('خطأ في تحميل دليل التليفونات');
    } finally {
      setLoading(false);
    }
  };

  // Debounced search function
  const debouncedSearch = useCallback(
    debounce((searchTerm, filterType = 'search') => {
      setFilters(prev => ({ 
        ...prev, 
        [filterType]: searchTerm 
      }));
      setPagination(prev => ({ ...prev, page: 1 }));
    }, 300),
    []
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Basic validation - at least one field should be filled
    const hasData = formData.الاسم.trim() || formData.الرقم.trim() || formData.الجهه.trim();
    if (!hasData) {
      toast.error('يرجى ملء حقل واحد على الأقل');
      return;
    }

    try {
      setLoading(true);
      
      // Prepare data - remove empty strings
      const submitData = {};
      Object.keys(formData).forEach(key => {
        const value = formData[key].trim();
        if (value) {
          submitData[key] = value;
        }
      });
      
      if (editingId) {
        await apiService.updatePhoneDirectoryEntry(editingId, submitData);
        toast.success('تم تحديث الإدخال بنجاح');
      } else {
        await apiService.createPhoneDirectoryEntry(submitData);
        toast.success('تم إضافة الإدخال بنجاح');
      }
      
      resetForm();
      loadEntries();
    } catch (error) {
      console.error('Error saving entry:', error);
      toast.error(editingId ? 'فشل في تحديث الإدخال' : 'فشل في إضافة الإدخال');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (entry) => {
    setEditingId(entry.id);
    setFormData({
      الاسم: entry.الاسم || '',
      الرقم: entry.الرقم || '',
      الجهه: entry.الجهه || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (id, name) => {
    if (!isAdmin()) {
      toast.error('غير مسموح لك بحذف الإدخالات');
      return;
    }

    const displayName = name || 'هذا الإدخال';
    if (window.confirm(`هل أنت متأكد من حذف "${displayName}"؟`)) {
      try {
        await apiService.deletePhoneDirectoryEntry(id);
        toast.success('تم حذف الإدخال بنجاح');
        loadEntries();
      } catch (error) {
        console.error('Error deleting entry:', error);
        toast.error('فشل في حذف الإدخال');
      }
    }
  };

  const resetForm = () => {
    setEditingId(null);
    setFormData({ الاسم: '', الرقم: '', الجهه: '' });
    setShowModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePageChange = (newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }));
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      الاسم: '',
      الرقم: '',
      الجهه: ''
    });
    setActiveFilter('all');
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
      return new Date(dateString).toLocaleDateString('ar-SA');
    } catch {
      return '';
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="card-title mb-0">
                <i className="fas fa-phone-alt me-2"></i>
                دليل التليفونات
              </h5>
              <button 
                className="btn btn-primary"
                onClick={() => setShowModal(true)}
              >
                <i className="fas fa-plus me-1"></i>
                إضافة جهة اتصال
              </button>
            </div>
            
            <div className="card-body">
              {/* Search and Filter Section */}
              <div className="row mb-4">
                <div className="col-12">
                  {/* Filter Type Selector */}
                  <div className="mb-3">
                    <div className="btn-group" role="group">
                      <button 
                        type="button" 
                        className={`btn ${activeFilter === 'all' ? 'btn-primary' : 'btn-outline-primary'} btn-sm`}
                        onClick={() => setActiveFilter('all')}
                      >
                        بحث عام
                      </button>
                      <button 
                        type="button" 
                        className={`btn ${activeFilter === 'name' ? 'btn-primary' : 'btn-outline-primary'} btn-sm`}
                        onClick={() => setActiveFilter('name')}
                      >
                        بحث بالاسم
                      </button>
                      <button 
                        type="button" 
                        className={`btn ${activeFilter === 'phone' ? 'btn-primary' : 'btn-outline-primary'} btn-sm`}
                        onClick={() => setActiveFilter('phone')}
                      >
                        بحث بالرقم
                      </button>
                      <button 
                        type="button" 
                        className={`btn ${activeFilter === 'organization' ? 'btn-primary' : 'btn-outline-primary'} btn-sm`}
                        onClick={() => setActiveFilter('organization')}
                      >
                        بحث بالجهة
                      </button>
                    </div>
                  </div>
                  
                  {/* Search Inputs */}
                  <div className="row">
                    {activeFilter === 'all' && (
                      <div className="col-md-6">
                        <div className="input-group">
                          <input
                            type="text"
                            className="form-control"
                            placeholder="البحث في جميع الحقول..."
                            value={filters.search}
                            onChange={(e) => debouncedSearch(e.target.value, 'search')}
                          />
                          <span className="input-group-text">
                            <i className="fas fa-search"></i>
                          </span>
                        </div>
                      </div>
                    )}
                    
                    {activeFilter === 'name' && (
                      <div className="col-md-6">
                        <div className="input-group">
                          <input
                            type="text"
                            className="form-control"
                            placeholder="البحث بالاسم..."
                            value={filters.الاسم}
                            onChange={(e) => debouncedSearch(e.target.value, 'الاسم')}
                          />
                          <span className="input-group-text">
                            <i className="fas fa-user"></i>
                          </span>
                        </div>
                      </div>
                    )}
                    
                    {activeFilter === 'phone' && (
                      <div className="col-md-6">
                        <div className="input-group">
                          <input
                            type="text"
                            className="form-control"
                            placeholder="البحث بالرقم..."
                            value={filters.الرقم}
                            onChange={(e) => debouncedSearch(e.target.value, 'الرقم')}
                          />
                          <span className="input-group-text">
                            <i className="fas fa-phone"></i>
                          </span>
                        </div>
                      </div>
                    )}
                    
                    {activeFilter === 'organization' && (
                      <div className="col-md-6">
                        <div className="input-group">
                          <input
                            type="text"
                            className="form-control"
                            placeholder="البحث بالجهة..."
                            value={filters.الجهه}
                            onChange={(e) => debouncedSearch(e.target.value, 'الجهه')}
                          />
                          <span className="input-group-text">
                            <i className="fas fa-building"></i>
                          </span>
                        </div>
                      </div>
                    )}
                    
                    <div className="col-md-3">
                      <button 
                        className="btn btn-outline-secondary w-100"
                        onClick={clearFilters}
                      >
                        <i className="fas fa-times me-1"></i>
                        مسح المرشحات
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Results Summary */}
              <div className="mb-3">
                <div className="d-flex justify-content-between align-items-center">
                  <span className="text-muted">
                    عرض {entries.length} من أصل {pagination.total} إدخال
                  </span>
                  <small className="text-muted">
                    الصفحة {pagination.page} من {pagination.pages}
                  </small>
                </div>
              </div>

              {/* Phone Directory Table */}
              {loading ? (
                <div className="text-center py-5">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">جاري التحميل...</span>
                  </div>
                  <p className="mt-2 text-muted">جاري تحميل دليل التليفونات...</p>
                </div>
              ) : entries.length === 0 ? (
                <div className="text-center py-5">
                  <i className="fas fa-address-book fa-3x text-muted mb-3"></i>
                  <h5 className="text-muted">لا توجد جهات اتصال</h5>
                  <p className="text-muted mb-4">
                    {Object.values(filters).some(f => f.trim()) 
                      ? 'لا توجد نتائج تطابق البحث' 
                      : 'لم يتم إضافة أي جهات اتصال بعد'
                    }
                  </p>
                  <button 
                    className="btn btn-primary"
                    onClick={() => setShowModal(true)}
                  >
                    <i className="fas fa-plus me-1"></i>
                    إضافة أول جهة اتصال
                  </button>
                </div>
              ) : (
                <>
                  <div className="table-responsive">
                    <table className="table table-hover">
                      <thead className="table-light">
                        <tr>
                          <th>الاسم</th>
                          <th>رقم التليفون</th>
                          <th>الجهة</th>
                          <th>تاريخ الإضافة</th>
                          <th>الإجراءات</th>
                        </tr>
                      </thead>
                      <tbody>
                        {entries.map(entry => (
                          <tr key={entry.id}>
                            <td>
                              <div className="d-flex align-items-center">
                                <i className="fas fa-user-circle text-primary me-2"></i>
                                <span>{entry.الاسم || <em className="text-muted">غير محدد</em>}</span>
                              </div>
                            </td>
                            <td>
                              <div className="d-flex align-items-center">
                                <i className="fas fa-phone text-success me-2"></i>
                                <span className="font-monospace">
                                  {entry.الرقم || <em className="text-muted">غير محدد</em>}
                                </span>
                              </div>
                            </td>
                            <td>
                              <div className="d-flex align-items-center">
                                <i className="fas fa-building text-info me-2"></i>
                                <span>{entry.الجهه || <em className="text-muted">غير محدد</em>}</span>
                              </div>
                            </td>
                            <td>
                              <small className="text-muted">
                                {formatDate(entry.created_at)}
                              </small>
                            </td>
                            <td>
                              <div className="btn-group btn-group-sm" role="group">
                                <button
                                  className="btn btn-outline-primary"
                                  onClick={() => handleEdit(entry)}
                                  title="تعديل"
                                >
                                  <i className="fas fa-edit"></i>
                                </button>
                                {isAdmin() && (
                                  <button
                                    className="btn btn-outline-danger"
                                    onClick={() => handleDelete(entry.id, entry.الاسم)}
                                    title="حذف"
                                  >
                                    <i className="fas fa-trash"></i>
                                  </button>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Pagination */}
                  {pagination.pages > 1 && (
                    <nav className="mt-4" aria-label="pagination">
                      <ul className="pagination justify-content-center">
                        <li className={`page-item ${pagination.page === 1 ? 'disabled' : ''}`}>
                          <button 
                            className="page-link" 
                            onClick={() => handlePageChange(pagination.page - 1)}
                            disabled={pagination.page === 1}
                          >
                            السابق
                          </button>
                        </li>
                        
                        {/* Page numbers */}
                        {[...Array(Math.min(5, pagination.pages))].map((_, index) => {
                          const pageNumber = Math.max(1, Math.min(
                            pagination.pages - 4,
                            pagination.page - 2
                          )) + index;
                          
                          if (pageNumber <= pagination.pages) {
                            return (
                              <li 
                                key={pageNumber} 
                                className={`page-item ${pagination.page === pageNumber ? 'active' : ''}`}
                              >
                                <button 
                                  className="page-link" 
                                  onClick={() => handlePageChange(pageNumber)}
                                >
                                  {pageNumber}
                                </button>
                              </li>
                            );
                          }
                          return null;
                        })}
                        
                        <li className={`page-item ${pagination.page === pagination.pages ? 'disabled' : ''}`}>
                          <button 
                            className="page-link" 
                            onClick={() => handlePageChange(pagination.page + 1)}
                            disabled={pagination.page === pagination.pages}
                          >
                            التالي
                          </button>
                        </li>
                      </ul>
                    </nav>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Add/Edit Modal */}
      {showModal && (
        <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <form onSubmit={handleSubmit}>
                <div className="modal-header">
                  <h5 className="modal-title">
                    <i className="fas fa-address-book me-2"></i>
                    {editingId ? 'تعديل جهة الاتصال' : 'إضافة جهة اتصال جديدة'}
                  </h5>
                  <button 
                    type="button" 
                    className="btn-close" 
                    onClick={resetForm}
                  ></button>
                </div>
                
                <div className="modal-body">
                  <div className="row g-3">
                    <div className="col-md-6">
                      <label className="form-label">
                        <i className="fas fa-user me-1"></i>
                        الاسم
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        name="الاسم"
                        value={formData.الاسم}
                        onChange={handleChange}
                        placeholder="اكتب الاسم..."
                      />
                    </div>
                    
                    <div className="col-md-6">
                      <label className="form-label">
                        <i className="fas fa-phone me-1"></i>
                        رقم التليفون
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        name="الرقم"
                        value={formData.الرقم}
                        onChange={handleChange}
                        placeholder="اكتب رقم التليفون..."
                        dir="ltr"
                      />
                    </div>
                    
                    <div className="col-12">
                      <label className="form-label">
                        <i className="fas fa-building me-1"></i>
                        الجهة أو المؤسسة
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        name="الجهه"
                        value={formData.الجهه}
                        onChange={handleChange}
                        placeholder="اكتب اسم الجهة أو المؤسسة..."
                      />
                    </div>
                  </div>
                  
                  <div className="mt-3">
                    <div className="alert alert-info">
                      <i className="fas fa-info-circle me-2"></i>
                      <strong>ملاحظة:</strong> جميع الحقول اختيارية، يمكنك ملء الحقول المتاحة فقط.
                    </div>
                  </div>
                </div>
                
                <div className="modal-footer">
                  <button 
                    type="button" 
                    className="btn btn-secondary" 
                    onClick={resetForm}
                  >
                    إلغاء
                  </button>
                  <button 
                    type="submit" 
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-1"></span>
                        جاري الحفظ...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-save me-1"></i>
                        {editingId ? 'تحديث' : 'إضافة'}
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PhoneDirectory;
