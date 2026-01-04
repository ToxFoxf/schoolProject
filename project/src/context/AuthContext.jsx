// src/context/AuthContext.jsx

import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI, usersAPI, notificationsAPI, setAuth } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  // Initialize auth state on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('authToken');
      if (token) {
        try {
          const userData = await authAPI.verify();
          setUser(userData.user);
          setIsAuthenticated(true);
          
          // Fetch notifications
          const notifs = await notificationsAPI.getAll();
          setNotifications(notifs);
        } catch (error) {
          localStorage.removeItem('authToken');
          setIsAuthenticated(false);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const register = async (name, email, password, role) => {
    try {
      const result = await authAPI.register(name, email, password, role);
      setAuth(result.token);
      setUser(result.user);
      setIsAuthenticated(true);
      return { success: true, message: 'Registration successful' };
    } catch (error) {
      return { success: false, message: error.message };
    }
  };

  const login = async (email, password) => {
    try {
      const result = await authAPI.login(email, password);
      setAuth(result.token);
      setUser(result.user);
      setIsAuthenticated(true);
      
      // Fetch notifications after login
      const notifs = await notificationsAPI.getAll();
      setNotifications(notifs);
      
      return { success: true, message: 'Login successful' };
    } catch (error) {
      return { success: false, message: error.message };
    }
  };

  const logout = async () => {
    try {
      authAPI.logout();
      setUser(null);
      setIsAuthenticated(false);
      setNotifications([]);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const updateUser = async (updates) => {
    if (user) {
      try {
        const updated = await usersAPI.updateProfile(user.id, updates);
        setUser(updated);
      } catch (error) {
        console.error('Update user error:', error);
      }
    }
  };

  const addNotification = async (title, message, type) => {
    try {
      const newNotif = await notificationsAPI.create({ title, message, type });
      setNotifications([newNotif, ...notifications]);
    } catch (error) {
      console.error('Add notification error:', error);
    }
  };

  const clearNotification = async (id) => {
    try {
      await notificationsAPI.delete(id);
      setNotifications(notifications.filter(n => n.id !== id));
    } catch (error) {
      console.error('Delete notification error:', error);
    }
  };

  const markNotificationAsRead = async (id) => {
    try {
      await notificationsAPI.markAsRead(id);
      setNotifications(notifications.map(n =>
        n.id === id ? { ...n, read: true } : n
      ));
    } catch (error) {
      console.error('Mark read error:', error);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        notifications,
        loading,
        register,
        login,
        logout,
        updateUser,
        addNotification,
        clearNotification,
        markNotificationAsRead
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);