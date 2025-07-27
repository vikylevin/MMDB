import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor: Add authorization token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: Handle token expiration
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const login = async (username, password) => {
  const response = await api.post('/auth/login', { username, password });
  const { access_token, user } = response.data;
  localStorage.setItem('access_token', access_token);
  localStorage.setItem('user', JSON.stringify(user));
  return user;
};

export const register = async (username, email, password) => {
  const response = await api.post('/auth/register', { username, email, password });
  const { access_token, user } = response.data;
  localStorage.setItem('access_token', access_token);
  localStorage.setItem('user', JSON.stringify(user));
  return user;
};

export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
};

// User APIs
export const getProfile = async () => {
  const response = await api.get('/user/profile');
  return response.data;
};

export const getWatchlist = async () => {
  const response = await api.get('/user/watchlist');
  return response.data;
};

// Movie APIs
export const toggleWatchlist = async (movieId) => {
  const response = await api.post(`/movies/${movieId}/watchlist`);
  return response.data;
};

export const rateMovie = async (movieId, rating) => {
  const response = await api.post(`/movies/${movieId}/rate`, { rating });
  return response.data;
};

export const getMovieRating = async (movieId) => {
  const response = await api.get(`/movies/${movieId}/rating`);
  return response.data;
};

// Check if user is authenticated
export const isAuthenticated = () => {
  return !!localStorage.getItem('access_token');
};

// Get current user information
export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};
