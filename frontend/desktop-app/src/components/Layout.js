// Layout.js - Main application layout with navigation
import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useLocation, Outlet } from 'react-router-dom';

const Layout = () => {
  const { user, logout, isAdmin } = useAuth();
  const location = useLocation();

  const handleLogout = () => {
    if (window.confirm('هل أنت متأكد من تسجيل الخروج؟')) {
      logout();
    }
  };

  // Navigation items based on user role
  const navItems = [
    {
      path: '/dashboard',
      icon: 'fas fa-tachometer-alt',
      label: 'لوحة التحكم',
      roles: ['admin', 'user']
    },
    {
      path: '/cases',
      icon: 'fas fa-gavel',
      label: 'القضايا',
      roles: ['admin', 'user']
    },
    {
      path: '/case-types',
      icon: 'fas fa-folder',
      label: 'أنواع القضايا',
      roles: ['admin', 'user']
    },
    {
      path: '/phone-directory',
      icon: 'fas fa-phone-alt',
      label: 'دليل التليفونات',
      roles: ['admin', 'user']
    },
    {
      path: '/users',
      icon: 'fas fa-users',
      label: 'المستخدمين',
      roles: ['admin'] // Admin only
    },
    {
      path: '/reports',
      icon: 'fas fa-chart-bar',
      label: 'التقارير والإحصائيات',
      roles: ['admin', 'user']
    },
    {
      path: '/settings',
      icon: 'fas fa-cog',
      label: 'الإعدادات',
      roles: ['admin', 'user']
    }
  ];

  // Filter navigation items based on user role
  const filteredNavItems = navItems.filter(item => 
    item.roles.includes(user?.user_type || 'user')
  );

  return (
    <div className="d-flex vh-100">
      
      {/* Sidebar */}
      <div className="sidebar" style={{ width: '280px', flexShrink: 0 }}>
        <div className="p-3">
          
          {/* Logo/Brand */}
          <div className="text-center mb-4 pt-3">
            <i className="fas fa-gavel fa-2x text-white mb-2"></i>
            <h5 className="text-white fw-bold mb-0">إدارة القضايا</h5>
            <small className="text-white-50">النظام القانوني</small>
          </div>

          {/* User Info */}
          <div className="card bg-white bg-opacity-10 border-0 mb-4">
            <div className="card-body p-3 text-center">
              <i className="fas fa-user-circle fa-2x text-white mb-2"></i>
              <h6 className="text-white mb-1">{user?.full_name}</h6>
              <small className="text-white-50">
                {user?.user_type === 'admin' ? 'مدير النظام' : 'مستخدم'}
              </small>
            </div>
          </div>

          {/* Navigation */}
          <nav className="nav flex-column">
            {filteredNavItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link d-flex align-items-center ${
                  location.pathname === item.path ? 'active' : ''
                }`}
              >
                <i className={`${item.icon} ms-3`} style={{ width: '20px' }}></i>
                {item.label}
              </Link>
            ))}
            
            {/* Logout */}
            <button
              onClick={handleLogout}
              className="nav-link d-flex align-items-center bg-transparent border-0 w-100 text-start mt-3"
              style={{ color: 'rgba(255,255,255,0.8)' }}
            >
              <i className="fas fa-sign-out-alt ms-3" style={{ width: '20px' }}></i>
              تسجيل الخروج
            </button>
          </nav>

        </div>
      </div>

      {/* Main Content */}
      <div className="flex-grow-1 d-flex flex-column">
        
        {/* Top Header */}
        <header className="bg-white border-bottom px-4 py-3">
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h4 className="mb-0 text-dark fw-semibold">
                {navItems.find(item => item.path === location.pathname)?.label || 'النظام'}
              </h4>
              <small className="text-muted">
                مرحباً {user?.full_name} - {new Date().toLocaleDateString('ar-SA')}
              </small>
            </div>
            
            <div className="d-flex align-items-center">
              <span className="badge bg-primary ms-2">
                {user?.user_type === 'admin' ? 'مدير' : 'مستخدم'}
              </span>
              
              <div className="dropdown">
                <button 
                  className="btn btn-outline-primary btn-sm dropdown-toggle"
                  type="button" 
                  data-bs-toggle="dropdown"
                >
                  <i className="fas fa-user ms-1"></i>
                  الحساب
                </button>
                <ul className="dropdown-menu">
                  <li>
                    <Link className="dropdown-item" to="/settings">
                      <i className="fas fa-cog ms-2"></i>
                      الإعدادات
                    </Link>
                  </li>
                  <li><hr className="dropdown-divider" /></li>
                  <li>
                    <button className="dropdown-item" onClick={handleLogout}>
                      <i className="fas fa-sign-out-alt ms-2"></i>
                      تسجيل الخروج
                    </button>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-grow-1 overflow-auto">
          <Outlet />
        </main>

      </div>
    </div>
  );
};

export default Layout;
