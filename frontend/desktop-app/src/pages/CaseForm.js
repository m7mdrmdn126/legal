import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import apiService from '../services/api';

const CaseForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = !!id;
  
  const [loading, setLoading] = useState(false);
  const [caseTypes, setCaseTypes] = useState([]);
  const [previousCases, setPreviousCases] = useState([]);
  
  const [formData, setFormData] = useState({
    case_number: '',
    plaintiff: '',
    defendant: '',
    case_type_id: '',
    judgment_type: 'حكم اول',
    previous_judgment_id: null
  });

  const judgmentTypes = [
    'حكم اول',
    'حكم ثان',
    'حكم ثالث'
  ];

  useEffect(() => {
    loadCaseTypes();
    if (isEdit) {
      loadCase();
    }
    loadPreviousCases();
  }, [id]);

  const loadCaseTypes = async () => {
    try {
      const response = await apiService.getCaseTypes(1, 100, '');
      setCaseTypes(response.items || []);
    } catch (error) {
      toast.error('فشل في تحميل أنواع القضايا');
    }
  };

  const loadPreviousCases = async () => {
    try {
      const response = await apiService.getCases({ limit: 100 });
      setPreviousCases(response.items || []);
    } catch (error) {
      console.error('فشل في تحميل القضايا السابقة');
    }
  };

  const loadCase = async () => {
    try {
      setLoading(true);
      const caseData = await apiService.getCase(id);
      setFormData({
        case_number: caseData.case_number || '',
        plaintiff: caseData.plaintiff || '',
        defendant: caseData.defendant || '',
        case_type_id: caseData.case_type_id || '',
        judgment_type: caseData.judgment_type || 'حكم اول',
        previous_judgment_id: caseData.previous_judgment_id || null
      });
    } catch (error) {
      toast.error('فشل في تحميل بيانات القضية');
      navigate('/cases');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.case_number || !formData.plaintiff || !formData.defendant || !formData.case_type_id) {
      toast.error('يرجى ملء جميع الحقول المطلوبة');
      return;
    }

    try {
      setLoading(true);
      
      const submitData = {
        ...formData,
        case_type_id: parseInt(formData.case_type_id),
        previous_judgment_id: formData.previous_judgment_id ? parseInt(formData.previous_judgment_id) : null
      };

      if (isEdit) {
        await apiService.updateCase(id, submitData);
        toast.success('تم تحديث القضية بنجاح');
      } else {
        await apiService.createCase(submitData);
        toast.success('تم إنشاء القضية بنجاح');
      }
      
      navigate('/cases');
    } catch (error) {
      toast.error(isEdit ? 'فشل في تحديث القضية' : 'فشل في إنشاء القضية');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  if (loading && isEdit) {
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
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="card-title mb-0">
                <i className="bi bi-file-earmark-text me-2"></i>
                {isEdit ? 'تعديل القضية' : 'إنشاء قضية جديدة'}
              </h5>
              <button 
                type="button" 
                className="btn btn-outline-secondary"
                onClick={() => navigate('/cases')}
              >
                <i className="bi bi-arrow-right me-1"></i>
                العودة
              </button>
            </div>
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label htmlFor="case_number" className="form-label">
                      رقم القضية <span className="text-danger">*</span>
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="case_number"
                      name="case_number"
                      value={formData.case_number}
                      onChange={handleChange}
                      placeholder="أدخل رقم القضية"
                      required
                    />
                  </div>
                  
                  <div className="col-md-6 mb-3">
                    <label htmlFor="case_type_id" className="form-label">
                      نوع القضية <span className="text-danger">*</span>
                    </label>
                    <select
                      className="form-select"
                      id="case_type_id"
                      name="case_type_id"
                      value={formData.case_type_id}
                      onChange={handleChange}
                      required
                    >
                      <option value="">اختر نوع القضية</option>
                      {caseTypes.map(type => (
                        <option key={type.id} value={type.id}>
                          {type.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label htmlFor="plaintiff" className="form-label">
                      المدعي <span className="text-danger">*</span>
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="plaintiff"
                      name="plaintiff"
                      value={formData.plaintiff}
                      onChange={handleChange}
                      placeholder="اسم المدعي"
                      required
                    />
                  </div>
                  
                  <div className="col-md-6 mb-3">
                    <label htmlFor="defendant" className="form-label">
                      المدعى عليه <span className="text-danger">*</span>
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="defendant"
                      name="defendant"
                      value={formData.defendant}
                      onChange={handleChange}
                      placeholder="اسم المدعى عليه"
                      required
                    />
                  </div>
                </div>

                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label htmlFor="judgment_type" className="form-label">
                      نوع الحكم
                    </label>
                    <select
                      className="form-select"
                      id="judgment_type"
                      name="judgment_type"
                      value={formData.judgment_type}
                      onChange={handleChange}
                    >
                      {judgmentTypes.map(type => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="col-md-6 mb-3">
                    <label htmlFor="previous_judgment_id" className="form-label">
                      القضية السابقة (للأحكام الثانية والثالثة)
                    </label>
                    <select
                      className="form-select"
                      id="previous_judgment_id"
                      name="previous_judgment_id"
                      value={formData.previous_judgment_id || ''}
                      onChange={handleChange}
                    >
                      <option value="">لا يوجد</option>
                      {previousCases.map(caseItem => (
                        <option key={caseItem.id} value={caseItem.id}>
                          {caseItem.case_number} - {caseItem.plaintiff}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="d-flex justify-content-end gap-2">
                  <button 
                    type="button" 
                    className="btn btn-outline-secondary"
                    onClick={() => navigate('/cases')}
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
                        {isEdit ? 'تحديث' : 'حفظ'}
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CaseForm;
