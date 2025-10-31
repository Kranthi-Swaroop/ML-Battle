/**
 * API Service - Axios HTTP client for backend communication
 */
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_URL}/auth/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: (username, password) =>
    api.post('/auth/login/', { username, password }),
  
  register: (userData) =>
    api.post('/users/register/', userData),
  
  refreshToken: (refreshToken) =>
    api.post('/auth/refresh/', { refresh: refreshToken }),
  
  getCurrentUser: () =>
    api.get('/users/me/'),
};

// Users API
export const usersAPI = {
  getAll: (params) =>
    api.get('/users/', { params }),
  
  getById: (id) =>
    api.get(`/users/${id}/`),
  
  getRatingHistory: (id) =>
    api.get(`/users/${id}/rating_history/`),
  
  getSubmissions: (id) =>
    api.get(`/users/${id}/submissions/`),
  
  update: (id, data) =>
    api.patch(`/users/${id}/`, data),
};

// Competitions API
export const competitionsAPI = {
  getAll: (params) =>
    api.get('/competitions/', { params }),
  
  getById: (id) =>
    api.get(`/competitions/${id}/`),
  
  getOngoing: () =>
    api.get('/competitions/ongoing/'),
  
  getUpcoming: () =>
    api.get('/competitions/upcoming/'),
  
  getCompleted: () =>
    api.get('/competitions/completed/'),
  
  getLeaderboard: (id) =>
    api.get(`/competitions/${id}/leaderboard/`),
  
  register: (id) =>
    api.post(`/competitions/${id}/register/`),
  
  create: (data) =>
    api.post('/competitions/', data),
  
  update: (id, data) =>
    api.patch(`/competitions/${id}/`, data),
  
  delete: (id) =>
    api.delete(`/competitions/${id}/`),
};

// Submissions API
export const submissionsAPI = {
  getAll: (params) =>
    api.get('/submissions/', { params }),
  
  getById: (id) =>
    api.get(`/submissions/${id}/`),
};

// Leaderboard API
export const leaderboardAPI = {
  getAll: (params) =>
    api.get('/leaderboard/', { params }),
  
  getByCompetition: (competitionId) =>
    api.get('/leaderboard/', { params: { competition: competitionId } }),
  
  getByUser: (userId) =>
    api.get('/leaderboard/', { params: { user: userId } }),
};

// Ratings API
export const ratingsAPI = {
  getAll: (params) =>
    api.get('/ratings/', { params }),
  
  getByUser: (userId) =>
    api.get('/ratings/', { params: { user: userId } }),
  
  getByCompetition: (competitionId) =>
    api.get('/ratings/', { params: { competition: competitionId } }),
};

export default api;
