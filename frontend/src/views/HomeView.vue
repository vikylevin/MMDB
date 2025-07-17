<template>
  <div class="home">
    <el-container>
      <el-main>
        <el-row :gutter="20" justify="center">
          <el-col :span="16">
            <el-input
              v-model="searchQuery"
              placeholder="Search movies..."
              class="search-input"
              @keyup.enter="searchMovies"
            >
              <template #append>
                <el-button @click="searchMovies">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
          </el-col>
        </el-row>

        <el-row :gutter="20" class="movie-grid">
          <el-col
            v-for="movie in movies"
            :key="movie.id"
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
            :xl="4"
          >
            <el-card :body-style="{ padding: '0px' }" class="movie-card">
              <img :src="movie.poster" class="movie-poster" />
              <div class="movie-info">
                <h3>{{ movie.title }}</h3>
                <p>{{ movie.year }}</p>
                <div class="rating-section">
                  <el-rate
                    v-model="movie.starRating"
                    disabled
                    text-color="#ff9900"
                  />
                  <span class="rating-text">{{ movie.rating }}</span>
                </div>
                <el-button
                  type="primary"
                  @click="goToDetail(movie.id)"
                  class="detail-button"
                >
                  View Details
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const searchQuery = ref('')
const movies = ref([])

const searchMovies = async () => {
  if (!searchQuery.value) return
  try {
    const response = await axios.get(`http://localhost:5000/api/movies/search?query=${encodeURIComponent(searchQuery.value)}`)
    movies.value = response.data.results.map(movie => ({
      id: movie.id,
      title: movie.title,
      year: movie.release_date ? new Date(movie.release_date).getFullYear() : 'Unknown',
      poster: movie.poster_path ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : '/placeholder.jpg',
      rating: Math.round(movie.vote_average * 10) / 10, // Round to 1 decimal place, keep 10-point scale
      starRating: Math.round((movie.vote_average / 2) * 10) / 10 // Convert to 5-star scale for display
    }))
  } catch (error) {
    console.error('Error fetching movies:', error)
  }
}

const goToDetail = (movieId) => {
  router.push(`/movie/${movieId}`)
}

// 获取初始电影列表
const fetchInitialMovies = async () => {
  try {
    console.log('Fetching movies from backend...')
    const response = await axios.get('http://localhost:5000/api/movies/popular')
    console.log('Response received:', response.data)
    
    if (response.data && response.data.results) {
      movies.value = response.data.results.map(movie => ({
        id: movie.id,
        title: movie.title,
        year: movie.release_date ? new Date(movie.release_date).getFullYear() : 'Unknown',
        poster: movie.poster_path ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : '/placeholder.jpg',
        rating: Math.round(movie.vote_average * 10) / 10, // Round to 1 decimal place, keep 10-point scale
        starRating: Math.round((movie.vote_average / 2) * 10) / 10 // Convert to 5-star scale for display
      }))
      console.log('Movies loaded:', movies.value.length)
    } else {
      console.error('No results in response:', response.data)
    }
  } catch (error) {
    console.error('Error fetching initial movies:', error)
    console.error('Error details:', error.response ? error.response.data : error.message)
  }
}

fetchInitialMovies()
</script>

<style scoped>
.home {
  padding: 20px;
}

.search-input {
  margin-bottom: 30px;
}

.movie-grid {
  margin-top: 20px;
}

.movie-card {
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.movie-card:hover {
  transform: translateY(-5px);
}

.movie-poster {
  width: 100%;
  height: 300px;
  object-fit: cover;
}

.movie-info {
  padding: 14px;
}

.movie-info h3 {
  margin: 0;
  font-size: 16px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.movie-info p {
  color: #666;
  margin: 5px 0;
}

.rating-section {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0;
}

.rating-text {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.detail-button {
  width: 100%;
  margin-top: 10px;
}
</style>