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

const fetchMovies = async (page = 1) => {
  try {
    loading.value = true;
    error.value = null;

    let endpoint = `http://127.0.0.1:5000/api/movies/${category.value}`;
    const response = await axios.get(endpoint, {
      params: { page }
    });

    movies.value = response.data.results;
    totalPages.value = response.data.total_pages;
    currentPage.value = page;
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
  <div class="movie-list-view">
    <h1 class="page-title">{{ categoryTitle }}</h1>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="movie-grid">
        <div v-for="i in 12" :key="i" class="movie-skeleton">
          <el-skeleton animated>
            <template #template>
              <div style="width: 100%;">
                <el-skeleton-item variant="image" style="width: 100%; height: 300px" />
                <div style="padding: 14px;">
                  <el-skeleton-item variant="h3" style="width: 80%" />
                  <el-skeleton-item variant="text" style="width: 50%; margin-top: 8px;" />
                  <el-skeleton-item variant="text" style="width: 100%; margin-top: 8px;" />
                </div>
              </div>
            </template>
          </el-skeleton>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      <el-alert :title="error" type="error" show-icon />
    </div>

    <!-- Movies Grid -->
    <div v-if="!loading && !error" class="movie-content">
      <div v-if="movies.length === 0" class="no-results">
        <el-empty description="No movies found" />
      </div>

      <div v-else class="movie-grid">
        <div v-for="movie in movies" :key="movie.id" class="movie-item">
          <MovieCard :movie="movie" />
        </div>
      </div>

      <!-- Pagination -->
      <div class="pagination-container" v-if="totalPages > 1">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="20"
          :total="totalPages * 20"
          :pager-count="5"
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.movie-list-view {
  padding-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 2rem;
  color: var(--text-color);
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.movie-skeleton {
  border-radius: 8px;
  overflow: hidden;
  background-color: var(--card-bg);
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.loading-state {
  opacity: 0.7;
}

.error-message {
  margin: 2rem 0;
}

.no-results {
  padding: 3rem;
  text-align: center;
}

@media (max-width: 768px) {
  .movie-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }

  .page-title {
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
  }
}
</style>
