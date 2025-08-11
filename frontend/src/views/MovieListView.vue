<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import MovieCard from '../components/MovieCard.vue';
import MovieFilters from '../components/MovieFilters.vue';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'https://mmdb-f1b3.onrender.com/api';
console.log('MovieListView API URL being used:', API_URL);

const route = useRoute();
const category = computed(() => route.params.category || 'popular');

const movies = ref([]);
const loading = ref(true);
const error = ref(null);
const currentPage = ref(1);
const totalPages = ref(1);
const filters = ref({});

const categoryTitles = {
  'popular': 'Popular Movies',
  'top-rated': 'Top Rated Movies',
  'upcoming': 'Upcoming Movies',
  'now-playing': 'Now Playing'
};

const categoryTitle = computed(() => {
  return categoryTitles[category.value] || 'Movies';
});

// Get current page of movies for display
const displayedMovies = computed(() => {
  return movies.value;
});

const handleFiltersChanged = (newFilters) => {
  filters.value = newFilters;
  fetchMovies(1); // Reset to first page when filters change
};

const fetchMovies = async (page = 1) => {
  try {
    loading.value = true;
    error.value = null;

    // Build query parameters
    const params = { page };
    
    if (filters.value.genres) {
      params.with_genres = filters.value.genres;
    }
    if (filters.value.ratingMin !== null && filters.value.ratingMin !== undefined) {
      params.vote_average_gte = filters.value.ratingMin;
    }
    if (filters.value.ratingMax !== null && filters.value.ratingMax !== undefined) {
      params.vote_average_lte = filters.value.ratingMax;
    }
    if (filters.value.language) {
      params.with_original_language = filters.value.language;
    }

    // All categories now use the same API endpoint pattern
    let endpoint = `${API_URL}/movie/category/${category.value}`;
    const response = await axios.get(endpoint, { params });

    if (response.data && response.data.results) {
      movies.value = response.data.results;
      totalPages.value = response.data.total_pages;
      currentPage.value = page;
    } else {
      throw new Error('Invalid response from server');
    }
  } catch (err) {
    console.error(`Error fetching ${category.value} movies:`, err);
    error.value = `Failed to load movies. Please try again later.`;
  } finally {
    loading.value = false;
  }
};

const handlePageChange = (page) => {
  fetchMovies(page);
  // Scroll to top when changing page
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

// Watch for category changes
watch(category, () => {
  filters.value = {}; // Clear filters when changing category
  fetchMovies(1);
});

onMounted(() => {
  fetchMovies(1);
});
</script>

<template>
  <div class="router-view-container">
    <h1 class="page-title">{{ categoryTitle }}</h1>

    <!-- Filter Section -->
    <div class="content-layout">
      <div class="filters-sidebar">
        <MovieFilters @filtersChanged="handleFiltersChanged" />
      </div>
      
      <div class="movies-content">
        <el-row v-if="error" justify="center">
          <el-col :span="24">
            <el-alert :title="error" type="error" />
          </el-col>
        </el-row>

        <div v-loading="loading" class="movies-grid">
          <div
            v-for="movie in displayedMovies"
            :key="movie.id"
            class="movie-item"
          >
            <MovieCard :movie="movie" />
          </div>
        </div>

        <el-row justify="center" class="pagination-row">
          <el-pagination
            v-if="totalPages > 1"
            :current-page="currentPage"
            :page-size="20"
            :total="totalPages * 20"
            @current-change="handlePageChange"
            layout="prev, pager, next, jumper"
            :pager-count="7"
            background
          />
        </el-row>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-title {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--text-color);
}

.content-layout {
  display: flex;
  gap: 16px; /* Reduced from 20px */
  align-items: flex-start;
}

.filters-sidebar {
  flex: 0 0 260px; /* Reduced from 280px */
  position: sticky;
  top: 20px;
}

.movies-content {
  flex: 1;
  min-width: 0;
}

.pagination-row {
  margin: 30px 0;
  padding-bottom: 20px;
  display: flex;
  justify-content: center;
}

:deep(.el-pagination) {
  --el-pagination-hover-color: var(--primary-color);
  --el-pagination-button-color: var(--text-color);
  --el-pagination-font-size: 14px;
}

:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background-color: var(--primary-color);
}

:deep(.el-pagination .el-input__inner) {
  text-align: center;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(4, 240px); /* Reduced fixed width from 250px */
  gap: 16px; /* Reduced from 24px */
  margin-bottom: 20px;
  min-height: 400px;
  padding: 0 5px; /* Reduced padding */
  justify-content: center;
}

.movie-item {
  display: flex;
  justify-content: center;
  width: 100%; /* Ensure item takes full column width */
}

/* Force override any inherited styles from HomeView */
.movies-content .movies-grid .movie-item :deep(.movie-card),
.movies-content .movies-grid .movie-item :deep(.movie-card.el-card),
.movies-content .movies-grid .movie-item :deep(.el-card.movie-card) {
  width: 240px !important; /* Reduced from 250px */
  min-width: 240px !important;
  max-width: 240px !important;
  height: 500px !important; /* Increased from 480px to provide more space for action buttons */
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden !important;
  box-sizing: border-box !important;
}

.movies-content .movies-grid .movie-item :deep(.poster-container) {
  height: 360px !important; /* Set to 2:3 aspect ratio (240px width : 360px height) for TMDB posters */
  flex: 0 0 360px !important;
  width: 100% !important;
  overflow: hidden !important;
  position: relative !important;
  border-radius: 12px 12px 0 0 !important;
  background-color: #1a1a1a !important; /* Dark background for better contrast */
}

.movies-content .movies-grid .movie-item :deep(.movie-poster) {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
  object-position: center top !important; /* Changed back to center top for better poster display */
  transition: transform 0.3s ease !important;
  border-radius: 12px 12px 0 0 !important;
}

/* Enhanced hover effect for list view */
.movies-content .movies-grid .movie-item:hover :deep(.movie-poster) {
  transform: scale(1.02) !important; /* Smaller scale for list view */
}

.movies-content .movies-grid .movie-item :deep(.poster-placeholder) {
  width: 100% !important;
  height: 100% !important;
}

.movies-content .movies-grid .movie-item :deep(.movie-info) {
  padding: 8px 12px !important; /* Further reduced padding */
  height: 160px !important; /* Further reduced from 200px to minimize space below buttons */
  display: flex !important;
  flex-direction: column !important;
  justify-content: flex-start !important;
  flex: 1 !important;
  overflow: hidden !important;
  gap: 0 !important; /* Remove gap completely */
}

.movies-content .movies-grid .movie-item :deep(.user-rating) {
  padding: 0 !important; /* Remove all padding */
  margin-bottom: 8px !important; /* Add spacing between rating and buttons */
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 8px !important;
  width: 100% !important;
}

.movies-content .movies-grid .movie-item :deep(.user-actions) {
  margin-top: auto !important;
  padding-top: 0 !important; /* Remove all padding */
  flex: 0 0 auto !important;
  display: flex !important;
  flex-direction: row !important;
  gap: 16px !important; /* Further increased gap between buttons from 12px to 16px */
  justify-content: center !important;
}

/* Force override Element Plus rate component styling */
.movies-content .movies-grid .movie-item :deep(.el-rate) {
  display: inline-flex !important;
  line-height: 1 !important;
  transition: all 0.3s ease !important;
  justify-content: center !important;
  margin: 0 !important;
  padding: 0 !important;
}

.movies-content .movies-grid .movie-item :deep(.el-button) {
  margin: 0 !important;
}

/* Allow some spacing between rating and actions */
.movies-content .movies-grid .movie-item :deep(.user-rating + .user-actions) {
  margin-top: 0 !important;
  padding-top: 0 !important;
}

.movies-content .movies-grid .movie-item :deep(.el-rate__icon) {
  font-size: 22px !important;
  margin-right: 6px !important; /* Further increased spacing between stars from 4px to 6px */
  transition: all 0.2s ease !important;
  color: #e0e0e0 !important; /* Gray for unrated stars */
}

/* Strong override for active/filled stars - multiple selectors for maximum coverage */
.movies-content .movies-grid .movie-item :deep(.el-rate__icon--on),
.movies-content .movies-grid .movie-item :deep(.el-rate__icon.is-filled),
.movies-content .movies-grid .movie-item :deep(.el-rate__item.is-active .el-rate__icon),
.movies-content .movies-grid .movie-item :deep(.el-rate__item:not(.is-disabled).is-active .el-rate__icon),
.movies-content .movies-grid .movie-item :deep(.el-rate .el-rate__item.is-active .el-icon),
.movies-content .movies-grid .movie-item :deep(.el-rate .el-rate__item.is-active .el-rate__icon),
.movies-content .movie-item :deep(.el-rate__item.is-active .el-rate__icon),
.movie-item :deep(.el-rate__item.is-active .el-rate__icon) {
  color: #ffd700 !important; /* Force yellow color for filled stars */
  transform: scale(1.1) !important;
}

/* Ultra-specific override to ensure yellow stars in movie list pages */
.movies-content :deep(.el-rate__item.is-active .el-rate__icon),
.movies-content :deep(.el-rate__icon--on),
.movies-content :deep(.el-rate__icon.is-filled) {
  color: #ffd700 !important;
}

/* Additional specific overrides */
.movies-content .movies-grid .movie-item :deep(.el-rate .el-icon) {
  color: inherit !important;
}

.movies-content .movies-grid .movie-item :deep(.el-rate__item:not(.is-disabled):not(.is-active) .el-rate__icon) {
  color: #e0e0e0 !important; /* Gray for unrated stars */
}

.el-row {
  margin-bottom: 20px;
}

/* Responsive design for movie grid - maintain consistent sizing */
@media (min-width: 1400px) {
  .movies-grid {
    grid-template-columns: repeat(4, 260px); /* Slightly larger for big screens */
    gap: 20px;
    padding: 0 10px;
    justify-content: center;
  }
  
  .movies-content .movies-grid .movie-item :deep(.movie-card) {
    width: 260px !important;
    min-width: 260px !important;
    max-width: 260px !important;
    height: 530px !important; /* Increased from 510px to provide more space for action buttons */
  }
}

@media (min-width: 1200px) and (max-width: 1399px) {
  .movies-grid {
    grid-template-columns: repeat(4, 240px);
    gap: 16px;
    padding: 0 8px;
    justify-content: center;
  }
  
  .movies-content .movies-grid .movie-item :deep(.movie-card) {
    width: 240px !important;
    min-width: 240px !important;
    max-width: 240px !important;
    height: 500px !important; /* Increased from 480px to provide more space for action buttons */
  }
}

@media (min-width: 992px) and (max-width: 1199px) {
  .movies-grid {
    grid-template-columns: repeat(3, 240px); /* 3 columns for medium screens */
    gap: 16px;
    padding: 0 5px;
    justify-content: center;
  }
  
  .movies-content .movies-grid .movie-item :deep(.movie-card) {
    width: 240px !important;
    min-width: 240px !important;
    max-width: 240px !important;
    height: 500px !important; /* Increased from 480px to provide more space for action buttons */
  }
  
  .content-layout {
    flex-direction: column;
  }
  
  .filters-sidebar {
    flex: none;
    position: static;
    width: 100%;
  }
}

@media (min-width: 768px) and (max-width: 991px) {
  .movies-grid {
    grid-template-columns: repeat(2, 240px); /* 2 columns for tablets */
    gap: 16px;
    padding: 0 5px;
    justify-content: center;
  }
  
  .movies-content .movies-grid .movie-item :deep(.movie-card) {
    width: 240px !important;
    min-width: 240px !important;
    max-width: 240px !important;
    height: 500px !important; /* Increased from 480px to provide more space for action buttons */
  }
  
  .content-layout {
    flex-direction: column;
  }
  
  .filters-sidebar {
    flex: none;
    position: static;
    width: 100%;
  }
}

@media (min-width: 576px) and (max-width: 767px) {
  .movies-grid {
    grid-template-columns: repeat(2, 220px); /* Smaller cards for small tablets */
    gap: 12px;
    padding: 0 5px;
    justify-content: center;
  }
  
  .movies-content .movies-grid .movie-item :deep(.movie-card) {
    width: 220px !important;
    min-width: 220px !important;
    max-width: 220px !important;
    height: 470px !important; /* Increased from 450px to provide more space for action buttons */
  }
  
  .content-layout {
    flex-direction: column;
  }
  
  .filters-sidebar {
    flex: none;
    position: static;
    width: 100%;
  }
}

@media (max-width: 575px) {
  .movies-grid {
    grid-template-columns: 240px; /* Single column for mobile */
    gap: 16px;
    padding: 0 5px;
    justify-content: center;
  }
  
  .movies-content .movies-grid .movie-item :deep(.movie-card) {
    width: 240px !important;
    min-width: 240px !important;
    max-width: 240px !important;
    height: 500px !important; /* Increased from 480px to provide more space for action buttons */
  }
  
  .content-layout {
    flex-direction: column;
  }
  
  .filters-sidebar {
    flex: none;
    position: static;
    width: 100%;
  }
  
  .page-title {
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
  }
}
</style>
