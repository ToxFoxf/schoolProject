// API configuration and utilities
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const getAuthToken = () => {
  return localStorage.getItem('authToken');
};

const setAuthToken = (token) => {
  localStorage.setItem('authToken', token);
};

const clearAuthToken = () => {
  localStorage.removeItem('authToken');
};

const apiCall = async (endpoint, method = 'GET', data = null) => {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json'
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const options = {
    method,
    headers
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || 'API Error');
    }

    return result;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

// Auth API
export const authAPI = {
  register: (name, email, password, role) =>
    apiCall('/auth/register', 'POST', { name, email, password, role }),
  login: (email, password) =>
    apiCall('/auth/login', 'POST', { email, password }),
  verify: () =>
    apiCall('/auth/verify', 'GET'),
  logout: () => {
    clearAuthToken();
  }
};

// Users API
export const usersAPI = {
  getMe: () => apiCall('/users/me', 'GET'),
  getUser: (id) => apiCall(`/users/${id}`, 'GET'),
  updateProfile: (id, data) =>
    apiCall(`/users/${id}`, 'PUT', data),
  getAllUsers: () => apiCall('/users', 'GET')
};

// Projects API
export const projectsAPI = {
  getAll: () => apiCall('/projects', 'GET'),
  getById: (id) => apiCall(`/projects/${id}`, 'GET'),
  create: (data) => apiCall('/projects', 'POST', data),
  update: (id, data) => apiCall(`/projects/${id}`, 'PUT', data),
  delete: (id) => apiCall(`/projects/${id}`, 'DELETE')
};

// Issues API
export const issuesAPI = {
  getByProject: (projectId) =>
    apiCall(`/issues/project/${projectId}`, 'GET'),
  getById: (id) => apiCall(`/issues/${id}`, 'GET'),
  create: (data) => apiCall('/issues', 'POST', data),
  update: (id, data) => apiCall(`/issues/${id}`, 'PUT', data),
  updateStatus: (id, status) =>
    apiCall(`/issues/${id}/status`, 'PATCH', { status }),
  delete: (id) => apiCall(`/issues/${id}`, 'DELETE')
};

// Notifications API
export const notificationsAPI = {
  getAll: () => apiCall('/notifications', 'GET'),
  create: (data) => apiCall('/notifications', 'POST', data),
  markAsRead: (id) =>
    apiCall(`/notifications/${id}/read`, 'PATCH'),
  delete: (id) => apiCall(`/notifications/${id}`, 'DELETE')
};

// Helper to set auth token after login
export const setAuth = (token) => {
  setAuthToken(token);
};

export default apiCall;
