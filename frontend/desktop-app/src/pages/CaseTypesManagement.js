import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import apiService from '../services/api';
import { formatShortDate } from '../utils-helper';

const CaseTypesManagement = () => {
  const [caseTypes, setCaseTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadCaseTypes();
  }, []);

  const loadCaseTypes = async () => {
    try {
      setLoading(true);
      const response = await apiService.getCaseTypes(1, 50, searchTerm);
      setCaseTypes(response.items || []);
    } catch (error) {
      toast.error('فشل في تحميل أنواع القضايا');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      toast.error('يرجى إدخال اسم نوع القضية');
      return;
    }

    try {
      setLoading(true);
      
      if (editingId) {
        await apiService.updateCaseType(editingId, formData);
        toast.success('تم تحديث نوع القضية بنجاح');
      } else {
        await apiService.createCaseType(formData);
        toast.success('تم إنشاء نوع القضية بنجاح');
      }
      
      resetForm();
      loadCaseTypes();
    } catch (error) {
      toast.error(editingId ? 'فشل في تحديث نوع القضية' : 'فشل في إنشاء نوع القضية');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (caseType) => {
    setEditingId(caseType.id);
    setFormData({
      name: caseType.name,
      description: caseType.description || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (id, name) => {
    if (window.confirm(`هل أنت متأكد من حذف نوع القضية "${name}"؟`)) {
      try {
        await apiService.deleteCaseType(id);
        toast.success('تم حذف نوع القضية بنجاح');
        loadCaseTypes();
      } catch (error) {
        toast.error('فشل في حذف نوع القضية');
      }
    }
  };

  const resetForm = () => {
    setEditingId(null);
    setFormData({ name: '', description: '' });
    setShowModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSearch = () => {
    loadCaseTypes();
  };

  return (
    <div className="container-fluid py-4">
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="card-title mb-0">
                <i className="bi bi-tags me-2"></i>
                إدارة أنواع القضايا
              </h5>
              <button 
                className="btn btn-primary"
                onClick={() => setShowModal(true)}
              >
                <i className="bi bi-plus-lg me-1"></i>
                إضافة نوع جديد
              </button>
            </div>
            
            <div className="card-body">
              {/* Search Bar */}
              <div className="row mb-3">
                <div className="col-md-6">
                  <div className="input-group">
                    <input
                      type="text"
                      className="form-control"
                      placeholder="البحث في أنواع القضايا..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    />
                    <button 
                      className="btn btn-outline-secondary" 
                      type="button"
                      onClick={handleSearch}
                    >
                      <i className="bi bi-search"></i>
                    </button>
                  </div>
                </div>
              </div>

              {/* Case Types Table */}
              {loading ? (
                <div className="text-center py-4">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">جاري التحميل...</span>
                  </div>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-striped">
                    <thead>
                      <tr>
                        <th>الرقم</th>
                        <th>اسم نوع القضية</th>
                        <th>الوصف</th>
                        <th>تاريخ الإنشاء</th>
                        <th>الإجراءات</th>
                      </tr>
                    </thead>
                    <tbody>
                      {caseTypes.length === 0 ? (
                        <tr>
                          <td colSpan="5" className="text-center text-muted py-4">
                            لا توجد أنواع قضايا
                          </td>
                        </tr>
                      ) : (
                        caseTypes.map((caseType, index) => (
                          <tr key={caseType.id}>
                            <td>{index + 1}</td>
                            <td>
                              <strong>{caseType.name}</strong>
                            </td>
                            <td>
                              {caseType.description ? (
                                <span className="text-muted">{caseType.description}</span>
                              ) : (
                                <span className="text-muted fst-italic">لا يوجد وصف</span>
                              )}
                            </td>
                            <td>
                              {caseType.created_at ? 
                                formatShortDate(caseType.created_at) : 
                                '-'
                              }
                            </td>
                            <td>
                              <div className="btn-group btn-group-sm" role="group">
                                <button 
                                  className="btn btn-outline-primary"
                                  onClick={() => handleEdit(caseType)}
                                  title="تعديل"
                                >
                                  <i className="bi bi-pencil"></i>
                                </button>
                                <button 
                                  className="btn btn-outline-danger"
                                  onClick={() => handleDelete(caseType.id, caseType.name)}
                                  title="حذف"
                                >
                                  <i className="bi bi-trash"></i>
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Modal for Add/Edit Case Type */}
      {showModal && (
        <div className="modal fade show d-block" tabIndex="-1" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  {editingId ? 'تعديل نوع القضية' : 'إضافة نوع قضية جديد'}
                </h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={resetForm}
                ></button>
              </div>
              <form onSubmit={handleSubmit}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label htmlFor="name" className="form-label">
                      اسم نوع القضية <span className="text-danger">*</span>
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      placeholder="مثال: مدني، جنائي، تجاري"
                      required
                    />
                  </div>
                  
                  <div className="mb-3">
                    <label htmlFor="description" className="form-label">
                      الوصف
                    </label>
                    <textarea
                      className="form-control"
                      id="description"
                      name="description"
                      rows="3"
                      value={formData.description}
                      onChange={handleChange}
                      placeholder="وصف مختصر لنوع القضية (اختياري)"
                    ></textarea>
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
                        <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                        جاري الحفظ...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-check-lg me-1"></i>
                        {editingId ? 'تحديث' : 'حفظ'}
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

export default CaseTypesManagement;
