import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_URL,
  timeout: 10000, // 10 seconds timeout
});

// Add response interceptor to handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received:', error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Request error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default {
  // Movies
  getPopularMovies() {
    return api.get('/movies/popular');
  },
  getTopRatedMovies() {
    return api.get('/movies/top-rated');
  },
  getUpcomingMovies() {
    return api.get('/movies/upcoming');
  },
  getTrendingMovies() {
    return api.get('/movies/trending');
  },
  getMovieDetails(id) {
    return api.get(`/movies/${id}`);
  },
  searchMovies(query) {
    return api.get(`/movies/search?query=${encodeURIComponent(query)}`);
  },

  // Test endpoints
  testApi() {
    return api.get('/test');
  },
  testTmdbDirectly() {
    // This directly uses the TMDB API to test if it's working
    return axios.get('https://api.themoviedb.org/3/movie/popular?api_key=4bd99769f8271938f81a8b9f9be62d7d&language=en-US');
  }
};
