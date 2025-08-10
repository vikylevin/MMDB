import axios from 'axios';
import { setAuthState } from '../stores/auth';

// Use environment variable for API URL, fallback to production for safety
const API_URL = import.meta.env.VITE_API_BASE_URL || 'https://mmdb-backend.onrender.com/api';

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
      // Only redirect if we're not already on the login page
      if (window.location.pathname !== '/login') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        // Update reactive auth state
        setAuthState(false, null);
        // Use router instead of direct window.location for better SPA behavior
        import('../router/index.js').then(({ default: router }) => {
          router.push('/login');
        });
      }
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
  // Update reactive auth state
  setAuthState(true, user);
  return user;
};

export const register = async (username, email, password) => {
  const response = await api.post('/auth/register', { username, email, password });
  // Backend returns access_token and user data directly on successful registration
  const { access_token, user } = response.data;
  localStorage.setItem('access_token', access_token);
  localStorage.setItem('user', JSON.stringify(user));
  // Update reactive auth state
  setAuthState(true, user);
  return user;
};

export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  // Update reactive auth state
  setAuthState(false, null);
};

// User APIs
export const getProfile = async () => {
  const response = await api.get('/user/profile');
  return response.data;
};

export const getWatchLater = async () => {
  const response = await api.get('/user/watch-later');
  return response.data;
};

// Backward compatibility alias
export const getWatchlist = getWatchLater;

// Get user's liked movies
export const getLikes = async () => {
  const response = await api.get('/user/likes');
  return response.data;
};

// Get user's watched movies
export const getWatched = async () => {
  const response = await api.get('/user/watched');
  return response.data;
};

// Movie APIs
export const toggleWatchLater = async (movieId) => {
  const id = Number(movieId);
  if (!id || isNaN(id)) {
    throw new Error('Invalid movie id');
  }
  // Call the new watch-later endpoint
  const response = await api.post(`/movie/${id}/watch-later`);
  return response.data;
};

// Backward compatibility alias
export const toggleWatchlist = toggleWatchLater;

export const rateMovie = async (movieId, rating) => {
  const response = await api.post(`/movie/${movieId}/rate`, { rating });
  return response.data;
};

export const getMovieRating = async (movieId) => {
  const response = await api.get(`/movie/${movieId}/rating`);
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

// Get user's reviews
export const getUserReviews = async () => {
  const response = await api.get('/user/reviews');
  return response.data;
};

// Toggle watched status for a movie
export const toggleWatched = async (movieId) => {
  const id = Number(movieId);
  if (!id || isNaN(id)) {
    throw new Error('Invalid movie id');
  }
  const response = await api.post('/user/watched', { movie_id: id });
  return response.data;
};

// Toggle like for a movie
export const toggleLike = async (movieId) => {
  const id = Number(movieId);
  if (!id || isNaN(id)) {
    throw new Error('Invalid movie id');
  }
  const response = await api.post('/user/likes', { movie_id: id });
  return response.data;
};

// Review comment management
export const addReviewComment = async (reviewId, comment) => {
  const response = await api.post(`/movie/reviews/${reviewId}/comments`, { comment });
  return response.data;
};

export const getReviewComments = async (reviewId) => {
  const response = await api.get(`/movie/reviews/${reviewId}/comments`);
  return response.data;
};

// Toggle review like
export const toggleReviewLike = async (reviewId) => {
  const response = await api.post(`/movie/reviews/${reviewId}/like`);
  return response.data;
};

// Review management
export const updateReview = async (reviewId, reviewData) => {
  const response = await api.put(`/movie/reviews/${reviewId}`, reviewData);
  return response.data;
};

export const deleteReview = async (reviewId) => {
  const response = await api.delete(`/movie/reviews/${reviewId}`);
  return response.data;
};

// Submit a review for a movie
export const submitReview = async (movieId, reviewData) => {
  const response = await api.post(`/movie/${movieId}/reviews`, reviewData);
  return response.data;
};

// Get reviews for a movie
export const getMovieReviews = async (movieId) => {
  const response = await api.get(`/movie/${movieId}/reviews`);
  return response.data;
};
