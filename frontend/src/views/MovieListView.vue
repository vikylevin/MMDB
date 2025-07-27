<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import MovieCard from '../components/MovieCard.vue';

const route = useRoute();
const category = computed(() => route.params.category || 'popular');

const movies = ref([]);
const loading = ref(true);
const error = ref(null);
const currentPage = ref(1);
const totalPages = ref(1);

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

const fetchMovies = async (page = 1) => {
  try {
    loading.value = true;
    error.value = null;

    // All categories now use the same API endpoint pattern
    let endpoint = `http://127.0.0.1:5000/api/movies/${category.value}`;
    const response = await axios.get(endpoint, {
      params: { page }
    });

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
  fetchMovies(1);
});

onMounted(() => {
  fetchMovies(1);
});
</script>

<template>
  <div class="router-view-container">
    <h1 class="page-title">{{ categoryTitle }}</h1>

    <el-row v-if="error" justify="center">
      <el-col :span="24">
        <el-alert :title="error" type="error" />
      </el-col>
    </el-row>

    <el-row v-loading="loading" :gutter="20" class="movies-grid">
      <el-col
        v-for="movie in displayedMovies"
        :key="movie.id"
        :xs="24"
        :sm="12"
        :md="6"
        :lg="4.8"
        :span="4.8"
      >
        <MovieCard :movie="movie" />
      </el-col>
    </el-row>

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
</template>

<style scoped>
.page-title {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--text-color);
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
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  justify-content: start;
  gap: 20px;
  width: 100%;
}

.movies-grid .el-col {
  flex: 0 0 calc(20% - 16px);
  max-width: calc(20% - 16px);
}

.el-row {
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .page-title {
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
  }
}
</style>
