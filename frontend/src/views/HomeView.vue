<template>
  <div class="router-view-container">
    <!-- Popular Movies Sectio// Fetch top rated mov// Fetch upcoming movies
const fetchUpcomingMovies = async () => {
  try {
    loadingUpcoming.value = true
    const response = await axios.get(`${API_URL}/movie/upcoming`, {
      params: { page: 1, limit: 10 }
    })nst fetchTopRatedMovies = async () => {
  try {
    loadingTopRated.value = true
    const response = await axios.get(`${API_URL}/movie/top_rated`, {
      params: { page: 1, limit: 10 }
    })    <div class="movie-section">
      <div class="section-header">
        <h2>Popular Movies</h2>
        <el-button text @click="router.push('/movies/popular')">View All</el-button>
      </div>
      <div class="scrollable-container" v-loading="loadingPopular">
        <div class="movies-row">
          <MovieCard v-for="movie in popularMovies" :key="movie.id" :movie="movie" />
        </div>
      </div>
    </div>

    <!-- Top Rated Movies Section -->
    <div class="movie-section">
      <div class="section-header">
        <h2>Top Rated Movies</h2>
        <el-button text @click="router.push('/movies/top-rated')">View All</el-button>
      </div>
      <div class="scrollable-container" v-loading="loadingTopRated">
        <div class="movies-row">
          <MovieCard v-for="movie in topRatedMovies" :key="movie.id" :movie="movie" />
        </div>
      </div>
    </div>

    <!-- Upcoming Movies Section -->
    <div class="movie-section">
      <div class="section-header">
        <h2>Upcoming Movies</h2>
        <el-button text @click="router.push('/movies/upcoming')">View All</el-button>
      </div>
      <div class="scrollable-container" v-loading="loadingUpcoming">
        <div class="movies-row">
          <MovieCard v-for="movie in upcomingMovies" :key="movie.id" :movie="movie" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import MovieCard from '../components/MovieCard.vue'

const router = useRouter()

// Use the same API_URL logic as in api.js
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

// Movie lists for different sections
const popularMovies = ref([])
const topRatedMovies = ref([])
const upcomingMovies = ref([])

// Loading states for each section
const loadingPopular = ref(false)
const loadingTopRated = ref(false)
const loadingUpcoming = ref(false)

// Fetch popular movies
const fetchPopularMovies = async () => {
  try {
    loadingPopular.value = true
    const response = await axios.get(`${API_URL}/movie/popular`, {
      params: { page: 1, limit: 10 }
    })
    if (response.data && response.data.results) {
      popularMovies.value = response.data.results
    }
  } catch (error) {
    console.error('Error fetching popular movies:', error)
  } finally {
    loadingPopular.value = false
  }
}

// Fetch top rated movies
const fetchTopRatedMovies = async () => {
  try {
    loadingTopRated.value = true
    const response = await axios.get(`${API_URL}/movie/category/top-rated`, {
      params: { page: 1, limit: 10 }
    })
    if (response.data && response.data.results) {
      topRatedMovies.value = response.data.results
    }
  } catch (error) {
    console.error('Error fetching top rated movies:', error)
  } finally {
    loadingTopRated.value = false
  }
}

// Fetch upcoming movies
const fetchUpcomingMovies = async () => {
  try {
    loadingUpcoming.value = true
    const response = await axios.get(`${API_URL}/movie/category/upcoming`, {
      params: { page: 1, limit: 10 }
    })
    if (response.data && response.data.results) {
      upcomingMovies.value = response.data.results
    }
  } catch (error) {
    console.error('Error fetching upcoming movies:', error)
  } finally {
    loadingUpcoming.value = false
  }
}

// Initialize all sections
onMounted(() => {
  fetchPopularMovies()
  fetchTopRatedMovies()
  fetchUpcomingMovies()
})
</script>

<style scoped>
.movie-section {
  margin-bottom: 40px;
  position: relative; /* For scroll buttons positioning */
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  font-size: 1.5em;
  color: var(--el-text-color-primary);
}

.scrollable-container {
  width: 100%;
  overflow-x: auto;
  padding: 20px 20px 25px 20px; /* Increased bottom padding for scrollbar */
  scroll-behavior: smooth;
  /* Enable touch scrolling on mobile */
  -webkit-overflow-scrolling: touch;
}

/* Custom scrollbar styles */
.scrollable-container::-webkit-scrollbar {
  height: 8px; /* Height of the horizontal scrollbar */
  width: auto;
}

.scrollable-container::-webkit-scrollbar-track {
  background: var(--el-fill-color-lighter);
  border-radius: 4px;
}

.scrollable-container::-webkit-scrollbar-thumb {
  background: var(--el-color-primary-light-5);
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.scrollable-container::-webkit-scrollbar-thumb:hover {
  background: var(--el-color-primary);
}

/* Firefox scrollbar styles */
.scrollable-container {
  scrollbar-width: thin;
  scrollbar-color: var(--el-color-primary-light-5) var(--el-fill-color-lighter);
}

.movies-row {
  display: flex;
  gap: 20px;
  /* Allow content to be wider than container for scrolling */
  width: max-content;
  padding-bottom: 5px; /* Add some space for the scrollbar */
  align-items: stretch; /* Ensure all cards stretch to the same height */
}

/* Home page specific movie card styling */
.movies-row :deep(.movie-card) {
  width: 200px;
  min-width: 200px;
  max-width: 200px;
  height: 460px; /* Increased from 440px to provide more space for action buttons */
}

.movies-row :deep(.poster-container) {
  height: 300px; /* Set to 2:3 aspect ratio (200px width : 300px height) for TMDB posters */
}

.movies-row :deep(.movie-info) {
  padding: 10px;
  min-height: 120px; /* Reduced to make room for larger poster */
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.movies-row :deep(.user-rating) {
  margin-bottom: 6px; /* Add spacing between rating and buttons */
  padding: 0; /* Remove any padding */
}

.movies-row :deep(.user-actions) {
  gap: 14px; /* Further increased gap between buttons for better spacing */
  margin-top: auto; /* Push buttons to bottom */
  padding-top: 0; /* Remove padding */
}

.movies-row :deep(.watchlist-btn),
.movies-row :deep(.like-btn),
.movies-row :deep(.watched-btn) {
  width: 32px;
  height: 32px;
  min-width: 32px;
  max-width: 32px;
}

.movies-row :deep(.el-rate__icon) {
  font-size: 16px;
  margin-right: 5px; /* Further increased spacing between stars for better visual */
}

/* Ensure rating stars are yellow in home view */
.movies-row :deep(.el-rate__icon--on) {
  color: #ffd700 !important; /* Force yellow color for filled stars */
}

.movies-row :deep(.el-rate__item.is-active .el-rate__icon) {
  color: #ffd700 !important; /* Force yellow color for active stars */
}

.movies-row :deep(.el-rate__item:not(.is-disabled) .el-rate__icon) {
  color: #e0e0e0; /* Gray for unrated stars */
}

.movies-row :deep(.el-rate__item:not(.is-disabled).is-active .el-rate__icon) {
  color: #ffd700 !important; /* Yellow for rated stars */
}

/* Add fade effect to indicate more content */
.scrollable-container::after {
  content: '';
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  width: 50px;
  background: linear-gradient(to right, transparent, var(--el-bg-color) 95%);
  pointer-events: none;
}
</style>