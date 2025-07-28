import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api'
});

// Add a request interceptor to automatically add the auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['X-Access-Token'] = token;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle common errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth data and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('login_time');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
