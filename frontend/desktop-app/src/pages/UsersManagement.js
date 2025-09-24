import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/api';

const UsersManagement = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    full_name: '',
    user_type: 'user'
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0
  });

  const userTypes = [
    { value: 'admin', label: 'مدير' },
    { value: 'user', label: 'مستخدم' }
  ];

  useEffect(() => {
    if (user?.user_type !== 'admin') {
      toast.error('ليس لديك صلاحية للوصول لهذه الصفحة');
      return;
    }
    loadUsers();
  }, [user, pagination.page, searchTerm]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await apiService.getUsers(
        pagination.page,
        pagination.limit,
        searchTerm
      );
      setUsers(response.items || []);
      setPagination(prev => ({
        ...prev,
        total: response.total || 0
      }));
    } catch (error) {
      toast.error('فشل في تحميل المستخدمين');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.username.trim() || !formData.full_name.trim()) {
      toast.error('يرجى ملء جميع الحقول المطلوبة');
      return;
    }

    if (!editingId && !formData.password.trim()) {
      toast.error('يرجى إدخال كلمة المرور للمستخدم الجديد');
      return;
    }

    try {
      setLoading(true);
      
      const submitData = {
        username: formData.username.trim(),
        full_name: formData.full_name.trim(),
        user_type: formData.user_type
      };

      if (!editingId || formData.password.trim()) {
        submitData.password = formData.password;
      }

      if (editingId) {
        await apiService.updateUser(editingId, submitData);
        toast.success('تم تحديث المستخدم بنجاح');
      } else {
        await apiService.createUser(submitData);
        toast.success('تم إنشاء المستخدم بنجاح');
      }
      
      resetForm();
      loadUsers();
    } catch (error) {
      if (error.message?.includes('username')) {
        toast.error('اسم المستخدم موجود بالفعل');
      } else {
        toast.error(editingId ? 'فشل في تحديث المستخدم' : 'فشل في إنشاء المستخدم');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (userData) => {
    setEditingId(userData.id);
    setFormData({
      username: userData.username,
      password: '',
      full_name: userData.full_name,
      user_type: userData.user_type
    });
    setShowModal(true);
  };

  const handleDelete = async (id, username) => {
    if (id === user.user_id) {
      toast.error('لا يمكن حذف حسابك الشخصي');
      return;
    }

    if (window.confirm(`هل أنت متأكد من حذف المستخدم "${username}"؟`)) {
      try {
        await apiService.deleteUser(id);
        toast.success('تم حذف المستخدم بنجاح');
        loadUsers();
      } catch (error) {
        toast.error('فشل في حذف المستخدم');
      }
    }
  };

  const resetForm = () => {
    setEditingId(null);
    setFormData({
      username: '',
      password: '',
      full_name: '',
      user_type: 'user'
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
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handlePageChange = (newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }));
  };

  if (user?.user_type !== 'admin') {
    return (
      <div className="container-fluid py-4">
        <div className="alert alert-warning text-center">
          <i className="bi bi-shield-exclamation me-2"></i>
          ليس لديك صلاحية للوصول لهذه الصفحة
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid py-4">
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="card-title mb-0">
                <i className="bi bi-people me-2"></i>
                إدارة المستخدمين
              </h5>
              <button 
                className="btn btn-primary"
                onClick={() => setShowModal(true)}
              >
                <i className="bi bi-plus-lg me-1"></i>
                إضافة مستخدم جديد
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
                      placeholder="البحث في المستخدمين..."
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

              {/* Users Table */}
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
                        <th>اسم المستخدم</th>
                        <th>الاسم الكامل</th>
                        <th>نوع المستخدم</th>
                        <th>تاريخ الإنشاء</th>
                        <th>آخر تحديث</th>
                        <th>الإجراءات</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.length === 0 ? (
                        <tr>
                          <td colSpan="7" className="text-center text-muted py-4">
                            لا توجد مستخدمين
                          </td>
                        </tr>
                      ) : (
                        users.map((userData, index) => (
                          <tr key={userData.id}>
                            <td>{(pagination.page - 1) * pagination.limit + index + 1}</td>
                            <td>
                              <strong>{userData.username}</strong>
                              {userData.id === user.user_id && (
                                <span className="badge bg-info ms-1">أنت</span>
                              )}
                            </td>
                            <td>{userData.full_name}</td>
                            <td>
                              <span className={`badge ${userData.user_type === 'admin' ? 'bg-primary' : 'bg-secondary'}`}>
                                {userTypes.find(type => type.value === userData.user_type)?.label || userData.user_type}
                              </span>
                            </td>
                            <td>
                              {userData.created_at ? 
                                new Date(userData.created_at).toLocaleDateString('ar-EG') : 
                                '-'
                              }
                            </td>
                            <td>
                              {userData.updated_at ? 
                                new Date(userData.updated_at).toLocaleDateString('ar-EG') : 
                                '-'
                              }
                            </td>
                            <td>
                              <div className="btn-group btn-group-sm" role="group">
                                <button 
                                  className="btn btn-outline-primary"
                                  onClick={() => handleEdit(userData)}
                                  title="تعديل"
                                >
                                  <i className="bi bi-pencil"></i>
                                </button>
                                {userData.id !== user.user_id && (
                                  <button 
                                    className="btn btn-outline-danger"
                                    onClick={() => handleDelete(userData.id, userData.username)}
                                    title="حذف"
                                  >
                                    <i className="bi bi-trash"></i>
                                  </button>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>

                  {/* Pagination */}
                  {Math.ceil(pagination.total / pagination.limit) > 1 && (
                    <nav className="mt-3">
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
                        
                        {Array.from({length: Math.ceil(pagination.total / pagination.limit)}).map((_, index) => {
                          const pageNum = index + 1;
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
                        
                        <li className={`page-item ${pagination.page >= Math.ceil(pagination.total / pagination.limit) ? 'disabled' : ''}`}>
                          <button 
                            className="page-link"
                            onClick={() => handlePageChange(pagination.page + 1)}
                            disabled={pagination.page >= Math.ceil(pagination.total / pagination.limit)}
                          >
                            التالي
                          </button>
                        </li>
                      </ul>
                    </nav>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Modal for Add/Edit User */}
      {showModal && (
        <div className="modal fade show d-block" tabIndex="-1" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  {editingId ? 'تعديل المستخدم' : 'إضافة مستخدم جديد'}
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
                    <label htmlFor="username" className="form-label">
                      اسم المستخدم <span className="text-danger">*</span>
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="username"
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      placeholder="اسم المستخدم (بالإنجليزية)"
                      required
                      disabled={editingId ? true : false}
                    />
                    {editingId && (
                      <div className="form-text text-muted">
                        لا يمكن تغيير اسم المستخدم بعد الإنشاء
                      </div>
                    )}
                  </div>
                  
                  <div className="mb-3">
                    <label htmlFor="password" className="form-label">
                      كلمة المرور {!editingId && <span className="text-danger">*</span>}
                    </label>
                    <input
                      type="password"
                      className="form-control"
                      id="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      placeholder={editingId ? "اتركها فارغة للاحتفاظ بكلمة المرور الحالية" : "كلمة المرور"}
                      required={!editingId}
                    />
                  </div>
                  
                  <div className="mb-3">
                    <label htmlFor="full_name" className="form-label">
                      الاسم الكامل <span className="text-danger">*</span>
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="full_name"
                      name="full_name"
                      value={formData.full_name}
                      onChange={handleChange}
                      placeholder="الاسم الكامل للمستخدم"
                      required
                    />
                  </div>
                  
                  <div className="mb-3">
                    <label htmlFor="user_type" className="form-label">
                      نوع المستخدم <span className="text-danger">*</span>
                    </label>
                    <select
                      className="form-select"
                      id="user_type"
                      name="user_type"
                      value={formData.user_type}
                      onChange={handleChange}
                      required
                    >
                      {userTypes.map(type => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
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

export default UsersManagement;
