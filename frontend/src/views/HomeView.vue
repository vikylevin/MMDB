<template>
  <div class="router-view-container">
    <el-row v-loading="loading" :gutter="20">
      <el-col
        v-for="movie in movies"
        :key="movie.id"
        :xs="24"
        :sm="12"
        :md="8"
        :lg="6"
        :xl="4"
      >
        <MovieCard :movie="movie" />
      </el-col>
    </el-row>

    <el-row justify="center" class="pagination-row">
      <el-pagination
        v-if="totalPages > 1"
        :current-page="currentPage"
        :page-size="18"
        :total="totalPages * 18"
        @current-change="handlePageChange"
        layout="prev, pager, next, jumper"
        :pager-count="7"
        background
      />
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import MovieCard from '../components/MovieCard.vue'

const router = useRouter()
const movies = ref([])
const loading = ref(false)
const currentPage = ref(1)
const totalPages = ref(0)

const fetchMovies = async (page = 1) => {
  try {
    loading.value = true
    const response = await axios.get('http://localhost:5000/api/movies/popular', {
      params: { page }
    })

    if (response.data && response.data.results) {
      movies.value = response.data.results.map(movie => ({
        id: movie.id,
        title: movie.title,
        year: movie.release_date ? new Date(movie.release_date).getFullYear() : 'Unknown',
        poster: movie.poster_path ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : '/placeholder.jpg',
        rating: Math.round(movie.vote_average * 10) / 10,
        starRating: Math.round((movie.vote_average / 2) * 10) / 10
      }))

      totalPages.value = response.data.total_pages
      currentPage.value = page
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  } catch (error) {
    console.error('Error fetching movies:', error)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  fetchMovies(page)
}

// 初始化加载
fetchMovies(1)
</script>

<style scoped>

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

.el-row {
  margin-bottom: 20px;
}
</style>