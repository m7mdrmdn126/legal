// Login.js - Authentication component based on POST /auth/login endpoint
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-toastify';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Basic validation
    if (!formData.username.trim() || !formData.password) {
      toast.error('يرجى إدخال اسم المستخدم وكلمة المرور');
      return;
    }

    setLoading(true);
    
    try {
      const result = await login(formData.username, formData.password);
      
      if (result.success) {
        // Login successful, AuthContext will handle the redirect
        console.log('Login successful:', result.user);
      }
      // Error handling is done in AuthContext
      
    } catch (error) {
      console.error('Login error:', error);
      toast.error('حدث خطأ غير متوقع');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center" 
         style={{ background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)' }}>
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-md-6 col-lg-4">
            <div className="card shadow-lg border-0" style={{ borderRadius: '15px' }}>
              <div className="card-body p-5">
                
                {/* Logo/Title */}
                <div className="text-center mb-4">
                  <i className="fas fa-gavel fa-3x text-primary mb-3"></i>
                  <h3 className="fw-bold text-primary">إدارة القضايا القانونية</h3>
                  <p className="text-muted">تسجيل الدخول إلى النظام</p>
                </div>

                {/* Login Form */}
                <form onSubmit={handleSubmit}>
                  <div className="mb-3">
                    <label htmlFor="username" className="form-label fw-semibold">
                      <i className="fas fa-user ms-2"></i>
                      اسم المستخدم
                    </label>
                    <input
                      type="text"
                      className="form-control form-control-lg"
                      id="username"
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      placeholder="أدخل اسم المستخدم"
                      required
                      disabled={loading}
                      style={{ borderRadius: '10px' }}
                    />
                  </div>

                  <div className="mb-4">
                    <label htmlFor="password" className="form-label fw-semibold">
                      <i className="fas fa-lock ms-2"></i>
                      كلمة المرور
                    </label>
                    <input
                      type="password"
                      className="form-control form-control-lg"
                      id="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="أدخل كلمة المرور"
                      required
                      disabled={loading}
                      style={{ borderRadius: '10px' }}
                    />
                  </div>

                  <button
                    type="submit"
                    className="btn btn-primary btn-lg w-100 fw-semibold"
                    disabled={loading}
                    style={{ borderRadius: '10px' }}
                  >
                    {loading ? (
                      <>
                        <span className="loading-spinner ms-2"></span>
                        جاري تسجيل الدخول...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-sign-in-alt ms-2"></i>
                        تسجيل الدخول
                      </>
                    )}
                  </button>
                </form>

                {/* Footer */}
                <div className="text-center mt-4">
                  <small className="text-muted">
                    نظام إدارة القضايا القانونية - الإصدار 1.0
                  </small>
                </div>

              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
