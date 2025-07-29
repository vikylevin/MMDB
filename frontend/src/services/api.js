// Toggle watched status for a movie
export const toggleWatched = async (movieId) => {
  const id = Number(movieId);
  if (!id || isNaN(id)) {
    throw new Error('Invalid movie id');
  }
  const response = await api.post('/user/watched', { movie_id: id });
  return response.data;
};
// Toggle favorite (like/unlike) for a movie
export const toggleFavorite = async (movieId) => {
  const id = Number(movieId);
  if (!id || isNaN(id)) {
    throw new Error('Invalid movie id');
  }
  const response = await api.post('/user/favorites', { movie_id: id });
  return response.data;
};
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
  // If registration is successful, automatically log in
  if (response.data && response.data.message === 'User registered successfully') {
    // Call login API to get token and user info
    return await login(username, password);
  } else {
    // Registration failed, return error
    throw new Error(response.data?.error || 'Registration failed');
  }
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

// Get user's liked (favorite) movies
export const getFavorites = async () => {
  const response = await api.get('/user/favorites');
  return response.data;
};

// Get user's watched movies
export const getWatched = async () => {
  const response = await api.get('/user/watched');
  return response.data;
};

// Movie APIs
export const toggleWatchlist = async (movieId) => {
  const id = Number(movieId);
  if (!id || isNaN(id)) {
    throw new Error('Invalid movie id');
  }
  // 直接调用后端统一的 toggle watchlist 路由
  const response = await api.post(`/movie/${id}/watchlist`);
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
