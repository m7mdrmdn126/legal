// App.js - Main application component with routing
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

// Components
import Login from './components/Login';
import Layout from './components/Layout';

// Pages
import Dashboard from './pages/Dashboard';
import CasesList from './pages/CasesList';
import CaseDetails from './pages/CaseDetails';
import CaseForm from './pages/CaseForm';
import CaseTypesManagement from './pages/CaseTypesManagement';
import PhoneDirectory from './pages/PhoneDirectory';
import UsersManagement from './pages/UsersManagement';
// Phase 3 - Advanced Features
import SessionsManagement from './pages/SessionsManagement';
import NotesManagement from './pages/NotesManagement';
import ReportsStatistics from './pages/ReportsStatistics';
import SettingsPreferences from './pages/SettingsPreferences';

// Loading Component
const LoadingScreen = () => (
  <div className="vh-100 d-flex align-items-center justify-content-center">
    <div className="text-center">
      <div className="spinner-border text-primary mb-3" role="status" style={{ width: '3rem', height: '3rem' }}>
        <span className="visually-hidden">جاري التحميل...</span>
      </div>
      <p className="text-muted">جاري تحميل النظام...</p>
    </div>
  </div>
);

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <LoadingScreen />;
  }
  
  return isAuthenticated() ? children : <Navigate to="/login" replace />;
};

// Public Route Component (redirect to dashboard if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <LoadingScreen />;
  }
  
  return !isAuthenticated() ? children : <Navigate to="/dashboard" replace />;
};

const App = () => {
  return (
    <div className="App">
      <Routes>
        
        {/* Public Routes */}
        <Route 
          path="/login" 
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          } 
        />
        
        {/* Protected Routes */}
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          {/* Default redirect to dashboard */}
          <Route index element={<Navigate to="/dashboard" replace />} />
          
          {/* Phase 1 Routes */}
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="cases" element={<CasesList />} />
          <Route path="cases/:id" element={<CaseDetails />} />
          
          {/* Phase 2 Routes - Management Features */}
          <Route path="cases/new" element={<CaseForm />} />
          <Route path="cases/:id/edit" element={<CaseForm />} />
          <Route path="case-types" element={<CaseTypesManagement />} />
          <Route path="phone-directory" element={<PhoneDirectory />} />
          <Route path="users" element={<UsersManagement />} />
          
          {/* Phase 3 Routes - Advanced Features */}
          <Route path="cases/:caseId/sessions" element={<SessionsManagement />} />
          <Route path="cases/:caseId/notes" element={<NotesManagement />} />
          <Route path="reports" element={<ReportsStatistics />} />
          <Route path="settings" element={<SettingsPreferences />} />
          
          {/* Catch all - 404 */}
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </div>
  );
};

// Placeholder component for future phases
const PlaceholderPage = ({ title }) => (
  <div className="main-content">
    <div className="text-center py-5">
      <i className="fas fa-tools fa-4x text-muted mb-4"></i>
      <h2 className="text-muted mb-3">{title}</h2>
      <p className="text-muted mb-4">هذه الصفحة قيد التطوير وستكون متاحة في المراحل القادمة</p>
      <div className="alert alert-info d-inline-block">
        <i className="fas fa-info-circle ms-2"></i>
        <strong>المرحلة الأولى:</strong> تم تطبيق لوحة التحكم، عرض القضايا، وتفاصيل القضايا
      </div>
    </div>
  </div>
);

// 404 Not Found component
const NotFoundPage = () => (
  <div className="main-content">
    <div className="text-center py-5">
      <i className="fas fa-exclamation-triangle fa-4x text-warning mb-4"></i>
      <h2 className="text-warning mb-3">404 - الصفحة غير موجودة</h2>
      <p className="text-muted mb-4">لم يتم العثور على الصفحة المطلوبة</p>
      <div className="btn-group">
        <button onClick={() => window.history.back()} className="btn btn-outline-primary">
          <i className="fas fa-arrow-right ms-1"></i>
          العودة
        </button>
        <Navigate to="/dashboard" className="btn btn-primary">
          <i className="fas fa-home ms-1"></i>
          لوحة التحكم
        </Navigate>
      </div>
    </div>
  </div>
);

export default App;
