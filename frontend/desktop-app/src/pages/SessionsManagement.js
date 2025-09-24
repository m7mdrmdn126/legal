import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import apiService from '../services/api';
import { formatDate, formatShortDate } from '../utils-helper';

const SessionsManagement = () => {
  const { caseId } = useParams();
  const navigate = useNavigate();
  const [sessions, setSessions] = useState([]);
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    session_date: '',
    session_notes: ''
  });



  useEffect(() => {
    if (caseId) {
      loadCaseData();
      loadSessions();
    }
  }, [caseId]);

  const loadCaseData = async () => {
    try {
      const case_data = await apiService.getCase(caseId);
      setCaseData(case_data);
    } catch (error) {
      toast.error('فشل في تحميل بيانات القضية');
      navigate('/cases');
    }
  };

  const loadSessions = async () => {
    try {
      setLoading(true);
      const response = await apiService.getSessions(caseId, 1, 50);
      setSessions(response.items || []);
    } catch (error) {
      toast.error('فشل في تحميل الجلسات');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.session_date) {
      toast.error('يرجى تحديد تاريخ الجلسة');
      return;
    }

    try {
      setLoading(true);
      
      const sessionData = {
        session_date: formData.session_date,
        session_notes: formData.session_notes || ''
      };

      if (editingId) {
        await apiService.updateSession(caseId, editingId, sessionData);
        toast.success('تم تحديث الجلسة بنجاح');
      } else {
        await apiService.createSession(caseId, sessionData);
        toast.success('تم إنشاء الجلسة بنجاح');
      }
      
      resetForm();
      loadSessions();
    } catch (error) {
      toast.error(editingId ? 'فشل في تحديث الجلسة' : 'فشل في إنشاء الجلسة');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (session) => {
    const sessionDate = session.session_date ? session.session_date.split('T')[0] : '';
    
    setEditingId(session.id);
    setFormData({
      session_date: sessionDate,
      session_notes: session.session_notes || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (id, sessionDate) => {
    if (window.confirm(`هل أنت متأكد من حذف جلسة ${sessionDate}؟`)) {
      try {
        await apiService.deleteSession(caseId, id);
        toast.success('تم حذف الجلسة بنجاح');
        loadSessions();
      } catch (error) {
        toast.error('فشل في حذف الجلسة');
      }
    }
  };

  const resetForm = () => {
    setEditingId(null);
    setFormData({
      session_date: '',
      session_notes: ''
    });
    setShowModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };



  if (!caseData) {
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
          {/* Case Info Header */}
          <div className="card mb-4">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h5 className="card-title mb-1">
                    <i className="bi bi-calendar-event me-2"></i>
                    جلسات القضية: {caseData.case_number}
                  </h5>
                  <p className="text-muted mb-0">
                    {caseData.plaintiff} ضد {caseData.defendant}
                  </p>
                </div>
                <div className="text-end">
                  <button 
                    className="btn btn-outline-secondary me-2"
                    onClick={() => navigate('/cases')}
                  >
                    <i className="bi bi-arrow-right me-1"></i>
                    العودة للقضايا
                  </button>
                  <button 
                    className="btn btn-primary"
                    onClick={() => setShowModal(true)}
                  >
                    <i className="bi bi-plus-lg me-1"></i>
                    إضافة جلسة جديدة
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Sessions List */}
          <div className="card">
            <div className="card-header">
              <h6 className="card-title mb-0">
                <i className="bi bi-list-ul me-2"></i>
                قائمة الجلسات ({sessions.length})
              </h6>
            </div>
            
            <div className="card-body">
              {loading ? (
                <div className="text-center py-4">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">جاري التحميل...</span>
                  </div>
                </div>
              ) : sessions.length === 0 ? (
                <div className="text-center py-5">
                  <i className="bi bi-calendar-x display-1 text-muted"></i>
                  <p className="text-muted mt-3">لا توجد جلسات مجدولة لهذه القضية</p>
                  <button 
                    className="btn btn-primary"
                    onClick={() => setShowModal(true)}
                  >
                    <i className="bi bi-plus-lg me-1"></i>
                    إضافة أول جلسة
                  </button>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead>
                      <tr>
                        <th>تاريخ الجلسة</th>
                        <th>الملاحظات</th>
                        <th>تاريخ الإنشاء</th>
                        <th>الإجراءات</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sessions.map((session) => (
                        <tr key={session.id}>
                          <td>
                            <strong>
                              {session.session_date ? 
                                formatDate(session.session_date) : 
                                'غير محدد'
                              }
                            </strong>
                          </td>
                          <td>
                            <div className="text-wrap" style={{maxWidth: '300px'}}>
                              {session.session_notes || '-'}
                            </div>
                          </td>
                          <td>
                            <small className="text-muted">
                              {session.created_at ? 
                                formatShortDate(session.created_at) : 
                                'غير محدد'
                              }
                            </small>
                          </td>
                          <td>
                            <div className="btn-group btn-group-sm">
                              <button 
                                className="btn btn-outline-primary"
                                onClick={() => handleEdit(session)}
                                title="تعديل"
                              >
                                <i className="bi bi-pencil"></i>
                              </button>
                              <button 
                                className="btn btn-outline-danger"
                                onClick={() => handleDelete(session.id, session.session_date ? new Date(session.session_date).toLocaleDateString('ar-EG') : 'الجلسة')}
                                title="حذف"
                              >
                                <i className="bi bi-trash"></i>
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
        </div>
      </div>

      {/* Session Form Modal */}
      {showModal && (
        <div className="modal fade show d-block" tabIndex="-1" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  {editingId ? 'تعديل الجلسة' : 'إضافة جلسة جديدة'}
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
                    <label htmlFor="session_date" className="form-label">
                      تاريخ ووقت الجلسة <span className="text-danger">*</span>
                    </label>
                    <input
                      type="datetime-local"
                      className="form-control"
                      id="session_date"
                      name="session_date"
                      value={formData.session_date}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  
                  <div className="mb-3">
                    <label htmlFor="session_notes" className="form-label">
                      ملاحظات الجلسة
                    </label>
                    <textarea
                      className="form-control"
                      id="session_notes"
                      name="session_notes"
                      rows="3"
                      value={formData.session_notes}
                      onChange={handleChange}
                      placeholder="ملاحظات حول الجلسة، نتائج، أو تطورات..."
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

export default SessionsManagement;
