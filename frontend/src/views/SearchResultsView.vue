<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import MovieCard from '../components/MovieCard.vue';
import { Search } from '@element-plus/icons-vue';

const route = useRoute();
const searchQuery = ref(route.query.query || '');

const movies = ref([]);
const loading = ref(false);
const error = ref(null);
const currentPage = ref(1);
const totalPages = ref(1);
const totalResults = ref(0);

const searchMovies = async (page = 1) => {
  if (!searchQuery.value.trim()) return;

  try {
    loading.value = true;
    error.value = null;

    const response = await axios.get(`http://127.0.0.1:5000/api/movies/search`, {
      params: {
        query: searchQuery.value,
        page
      }
    });

    movies.value = response.data.results;
    totalPages.value = response.data.total_pages;
    totalResults.value = response.data.total_results;
    currentPage.value = page;
  } catch (err) {
    console.error('Error searching movies:', err);
    error.value = 'Failed to search movies. Please try again later.';
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    // Update URL with the search query
    const query = encodeURIComponent(searchQuery.value.trim());
    history.pushState(
      {}, 
      '', 
      `/search?query=${query}`
    );
    searchMovies(1);
  }
};

const handlePageChange = (page) => {
  searchMovies(page);
  // Scroll to top when changing page
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

onMounted(() => {
  if (searchQuery.value.trim()) {
    searchMovies(1);
  }
});
</script>

<template>
  <div class="search-results-view">
    <div class="search-header">
      <h1>Search Movies</h1>
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="Search for movies..."
          @keyup.enter="handleSearch"
          clearable
        >
          <template #append>
            <el-button :icon="Search" @click="handleSearch" />
          </template>
        </el-input>
      </div>
    </div>

    <!-- Results Summary -->
    <div v-if="!loading && searchQuery && totalResults > 0" class="results-summary">
      Found {{ totalResults }} results for "{{ searchQuery }}"
    </div>

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

    <!-- Empty Search -->
    <div v-if="!loading && !searchQuery" class="empty-search">
      <el-empty description="Enter a search term to find movies" />
    </div>

    <!-- No Results -->
    <div v-if="!loading && searchQuery && movies.length === 0 && !error" class="no-results">
      <el-empty :description="`No results found for '${searchQuery}'`" />
      <p>Try different keywords or check the spelling</p>
    </div>

    <!-- Search Results -->
    <div v-if="!loading && movies.length > 0" class="search-results">
      <div class="movie-grid">
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
.search-results-view {
  padding-bottom: 2rem;
}

.search-header {
  margin-bottom: 2rem;
}

.search-header h1 {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-color);
}

.search-bar {
  max-width: 600px;
}

.results-summary {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  color: var(--text-color);
  opacity: 0.8;
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

.empty-search, .no-results {
  padding: 3rem;
  text-align: center;
}

.no-results p {
  margin-top: 1rem;
  color: var(--text-color);
  opacity: 0.7;
}

@media (max-width: 768px) {
  .movie-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }

  .search-header h1 {
    font-size: 1.5rem;
  }

  .search-bar {
    max-width: 100%;
  }
}
</style>
