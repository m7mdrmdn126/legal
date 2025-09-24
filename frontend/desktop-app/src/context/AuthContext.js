// AuthContext.js - Based on backend auth endpoints from api-helper.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import { toast } from 'react-toastify';

const AuthContext = createContext();

// API Base URL - matching backend
const API_BASE_URL = 'http://localhost:8000/api/v1';

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);

  // Initialize auth state on app start
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = () => {
    try {
      const savedToken = localStorage.getItem('access_token');
      const savedUser = localStorage.getItem('user_data');
      const expiresAt = localStorage.getItem('token_expires_at');

      if (savedToken && savedUser && expiresAt) {
        // Check if token is still valid
        if (Date.now() < parseInt(expiresAt)) {
          setToken(savedToken);
          setUser(JSON.parse(savedUser));
        } else {
          // Token expired, clear data
          clearAuthData();
        }
      }
    } catch (error) {
      console.error('Error initializing auth:', error);
      clearAuthData();
    } finally {
      setLoading(false);
    }
  };

  // Login function - matches POST /auth/login endpoint
  const login = async (username, password) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username.trim(),
          password: password
        })
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        
        // Handle specific error from backend (401 status)
        if (response.status === 401) {
          throw new Error(error.detail || 'اسم المستخدم أو كلمة المرور غير صحيحة');
        }
        throw new Error(error.detail || 'خطأ في تسجيل الدخول');
      }

      const data = await response.json();
      
      // Save auth data - matching LoginResponse model
      const expiresAt = Date.now() + (data.expires_in * 1000);
      
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user_data', JSON.stringify(data.user));
      localStorage.setItem('token_expires_at', expiresAt.toString());

      setToken(data.access_token);
      setUser(data.user);
      
      toast.success(`مرحباً ${data.user.full_name}`);
      return { success: true, user: data.user };

    } catch (error) {
      console.error('Login error:', error);
      toast.error(error.message);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  // Logout function - matches POST /auth/logout endpoint
  const logout = async () => {
    try {
      // Call backend logout endpoint if token exists
      if (token) {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          }
        }).catch(() => {
          // Ignore network errors on logout
        });
      }
      
      toast.success('تم تسجيل الخروج بنجاح');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearAuthData();
    }
  };

  const clearAuthData = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('token_expires_at');
    setToken(null);
    setUser(null);
  };

  // Get auth headers for API requests
  const getAuthHeaders = () => {
    if (!token) return {};
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  };

  // Check if user is admin - based on User model user_type field
  const isAdmin = () => {
    return user && user.user_type === 'admin';
  };

  // Check if authenticated
  const isAuthenticated = () => {
    return !!token && !!user;
  };

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    getAuthHeaders,
    isAdmin,
    isAuthenticated
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
