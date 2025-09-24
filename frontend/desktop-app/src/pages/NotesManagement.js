import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import apiService from '../services/api';

const NotesManagement = () => {
  const { caseId } = useParams();
  const navigate = useNavigate();
  const [notes, setNotes] = useState([]);
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    content: ''
  });
  const [searchTerm, setSearchTerm] = useState('');



  useEffect(() => {
    if (caseId) {
      loadCaseData();
      loadNotes();
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

  const loadNotes = async () => {
    try {
      setLoading(true);
      const response = await apiService.getNotes(caseId, 1, 50, searchTerm);
      setNotes(response.items || []);
    } catch (error) {
      toast.error('فشل في تحميل الملاحظات');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.content.trim()) {
      toast.error('يرجى ملء محتوى الملاحظة');
      return;
    }

    try {
      setLoading(true);
      
      const noteData = {
        note_text: formData.content.trim()
      };

      if (editingId) {
        await apiService.updateNote(caseId, editingId, noteData);
        toast.success('تم تحديث الملاحظة بنجاح');
      } else {
        await apiService.createNote(caseId, noteData);
        toast.success('تم إنشاء الملاحظة بنجاح');
      }
      
      resetForm();
      loadNotes();
    } catch (error) {
      toast.error(editingId ? 'فشل في تحديث الملاحظة' : 'فشل في إنشاء الملاحظة');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (note) => {
    setEditingId(note.id);
    setFormData({
      content: note.note_text || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (id, noteText) => {
    if (window.confirm(`هل أنت متأكد من حذف الملاحظة "${noteText.substring(0, 50)}..."؟`)) {
      try {
        await apiService.deleteNote(caseId, id);
        toast.success('تم حذف الملاحظة بنجاح');
        loadNotes();
      } catch (error) {
        toast.error('فشل في حذف الملاحظة');
      }
    }
  };

  const resetForm = () => {
    setEditingId(null);
    setFormData({
      content: ''
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

  const handleSearch = () => {
    loadNotes();
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
                    <i className="bi bi-journal-text me-2"></i>
                    ملاحظات القضية: {caseData.case_number}
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
                    إضافة ملاحظة جديدة
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Search and Filter */}
          <div className="card mb-4">
            <div className="card-body">
              <div className="row">
                <div className="col-md-8">
                  <div className="input-group">
                    <input
                      type="text"
                      className="form-control"
                      placeholder="البحث في الملاحظات..."
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
            </div>
          </div>

          {/* Notes List */}
          <div className="card">
            <div className="card-header">
              <h6 className="card-title mb-0">
                <i className="bi bi-list-ul me-2"></i>
                قائمة الملاحظات ({notes.length})
              </h6>
            </div>
            
            <div className="card-body">
              {loading ? (
                <div className="text-center py-4">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">جاري التحميل...</span>
                  </div>
                </div>
              ) : notes.length === 0 ? (
                <div className="text-center py-5">
                  <i className="bi bi-journal-x display-1 text-muted"></i>
                  <p className="text-muted mt-3">لا توجد ملاحظات لهذه القضية</p>
                  <button 
                    className="btn btn-primary"
                    onClick={() => setShowModal(true)}
                  >
                    <i className="bi bi-plus-lg me-1"></i>
                    إضافة أول ملاحظة
                  </button>
                </div>
              ) : (
                <div className="row">
                  {notes.map((note) => (
                    <div key={note.id} className="col-md-6 col-lg-4 mb-3">
                      <div className="card h-100 border-start border-primary border-3">
                        <div className="card-header pb-2">
                          <div className="d-flex justify-content-between align-items-start">
                            <div className="flex-grow-1">
                              <h6 className="card-title mb-1 text-truncate" title={note.note_text}>
                                ملاحظة #{note.id}
                              </h6>
                              <small className="text-muted">
                                <i className="bi bi-calendar3 me-1"></i>
                                {note.created_at ? 
                                  new Date(note.created_at).toLocaleDateString('ar-EG', {
                                    year: 'numeric',
                                    month: 'short',
                                    day: 'numeric'
                                  }) : 
                                  'غير محدد'
                                }
                              </small>
                            </div>
                            <div className="dropdown">
                              <button 
                                className="btn btn-sm btn-outline-secondary dropdown-toggle" 
                                type="button" 
                                data-bs-toggle="dropdown"
                              >
                                <i className="bi bi-three-dots"></i>
                              </button>
                              <ul className="dropdown-menu">
                                <li>
                                  <button 
                                    className="dropdown-item"
                                    onClick={() => handleEdit(note)}
                                  >
                                    <i className="bi bi-pencil me-2"></i>
                                    تعديل
                                  </button>
                                </li>
                                <li><hr className="dropdown-divider" /></li>
                                <li>
                                  <button 
                                    className="dropdown-item text-danger"
                                    onClick={() => handleDelete(note.id, note.note_text)}
                                  >
                                    <i className="bi bi-trash me-2"></i>
                                    حذف
                                  </button>
                                </li>
                              </ul>
                            </div>
                          </div>
                        </div>
                        <div className="card-body pt-2">
                          <p className="card-text" style={{fontSize: '0.95rem', lineHeight: '1.5'}}>
                            {note.note_text && note.note_text.length > 200 
                              ? `${note.note_text.substring(0, 200)}...` 
                              : note.note_text || 'لا يوجد نص للملاحظة'
                            }
                          </p>
                        </div>
                        <div className="card-footer bg-transparent border-0 pt-0">
                          <small className="text-muted">
                            <i className="bi bi-clock me-1"></i>
                            {note.created_at ? 
                              new Date(note.created_at).toLocaleDateString('ar-EG', {
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                              }) : 
                              'غير محدد'
                            }
                          </small>
                          {note.created_by && (
                            <>
                              <br />
                              <small className="text-muted">
                                <i className="bi bi-person me-1"></i>
                                {note.created_by.full_name}
                              </small>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Note Form Modal */}
      {showModal && (
        <div className="modal fade show d-block" tabIndex="-1" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  {editingId ? 'تعديل الملاحظة' : 'إضافة ملاحظة جديدة'}
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
                    <label htmlFor="content" className="form-label">
                      نص الملاحظة <span className="text-danger">*</span>
                    </label>
                    <textarea
                      className="form-control"
                      id="content"
                      name="content"
                      rows="8"
                      value={formData.content}
                      onChange={handleChange}
                      placeholder="اكتب نص الملاحظة هنا... (5-2000 حرف)"
                      required
                      minLength={5}
                      maxLength={2000}
                    ></textarea>
                    <div className="form-text">
                      الحد الأدنى 5 أحرف والحد الأقصى 2000 حرف. ({formData.content.length}/2000)
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

export default NotesManagement;
