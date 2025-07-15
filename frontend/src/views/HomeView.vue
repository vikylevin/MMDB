<template>
  <div class="home">
    <el-container>
      <el-main>
        <el-row :gutter="20" justify="center">
          <el-col :span="16">
            <el-input
              v-model="searchQuery"
              placeholder="搜索电影..."
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
                <el-rate
                  v-model="movie.rating"
                  disabled
                  show-score
                  text-color="#ff9900"
                />
                <el-button
                  type="primary"
                  @click="goToDetail(movie.id)"
                  class="detail-button"
                >
                  查看详情
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
      rating: movie.vote_average / 2 // Convert 10-point scale to 5-point scale
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
    const response = await axios.get('http://localhost:5000/api/movies/popular')
    movies.value = response.data.results.map(movie => ({
      id: movie.id,
      title: movie.title,
      year: new Date(movie.release_date).getFullYear(),
      poster: `https://image.tmdb.org/t/p/w500${movie.poster_path}`,
      rating: movie.vote_average / 2 // Convert 10-point scale to 5-point scale
    }))
  } catch (error) {
    console.error('Error fetching initial movies:', error)
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
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import MovieCard from '../components/MovieCard.vue';
import { ElSkeleton, ElSkeletonItem, ElCarousel, ElCarouselItem } from 'element-plus';

const popularMovies = ref([]);
const topRatedMovies = ref([]);
const upcomingMovies = ref([]);
const trendingMovies = ref([]);
const loading = ref(true);
const error = ref(null);

const fetchMovies = async () => {
  try {
    loading.value = true;
    error.value = null;

    const [popularRes, topRatedRes, upcomingRes, trendingRes] = await Promise.all([
      axios.get('http://localhost:5000/api/movies/popular'),
      axios.get('http://localhost:5000/api/movies/top-rated'),
      axios.get('http://localhost:5000/api/movies/upcoming'),
      axios.get('http://localhost:5000/api/movies/trending')
    ]);

    popularMovies.value = popularRes.data.results.slice(0, 8);
    topRatedMovies.value = topRatedRes.data.results.slice(0, 8);
    upcomingMovies.value = upcomingRes.data.results.slice(0, 8);
    trendingMovies.value = trendingRes.data.results.slice(0, 5);
  } catch (err) {
    console.error('Error fetching movies:', err);
    error.value = 'Failed to load movies. Please try again later.';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchMovies();
});

const imageBaseUrl = 'https://image.tmdb.org/t/p/original';
</script>

<template>
  <div class="home-view">
    <!-- Hero Section with Carousel -->
    <section class="hero-section" v-if="!loading && !error">
      <el-carousel :interval="5000" height="500px" indicator-position="outside" arrow="always">
        <el-carousel-item v-for="movie in trendingMovies" :key="movie.id">
          <div class="carousel-item" :style="{
            backgroundImage: `linear-gradient(to bottom, rgba(0,0,0,0.2), rgba(0,0,0,0.8)), url(${imageBaseUrl}${movie.backdrop_path})`
          }">
            <div class="carousel-content">
              <h2>{{ movie.title }}</h2>
              <p>{{ movie.overview }}</p>
              <router-link :to="`/movie/${movie.id}`" class="hero-btn">
                View Details
              </router-link>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </section>

    <!-- Loading Skeleton -->
    <div v-if="loading" class="loading-skeleton">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      <el-alert :title="error" type="error" show-icon />
    </div>

    <!-- Movie Sections -->
    <template v-if="!loading && !error">
      <!-- Popular Movies Section -->
      <section class="movie-section">
        <div class="section-header">
          <h2>Popular Movies</h2>
          <router-link to="/movies/popular" class="view-all">View All</router-link>
        </div>
        <div class="movie-grid">
          <div v-for="movie in popularMovies" :key="movie.id" class="movie-item">
            <MovieCard :movie="movie" />
          </div>
        </div>
      </section>

      <!-- Top Rated Movies Section -->
      <section class="movie-section">
        <div class="section-header">
          <h2>Top Rated</h2>
          <router-link to="/movies/top-rated" class="view-all">View All</router-link>
        </div>
        <div class="movie-grid">
          <div v-for="movie in topRatedMovies" :key="movie.id" class="movie-item">
            <MovieCard :movie="movie" />
          </div>
        </div>
      </section>

      <!-- Upcoming Movies Section -->
      <section class="movie-section">
        <div class="section-header">
          <h2>Coming Soon</h2>
          <router-link to="/movies/upcoming" class="view-all">View All</router-link>
        </div>
        <div class="movie-grid">
          <div v-for="movie in upcomingMovies" :key="movie.id" class="movie-item">
            <MovieCard :movie="movie" />
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.home-view {
  padding-bottom: 2rem;
}

.hero-section {
  margin-bottom: 2rem;
}

.carousel-item {
  height: 100%;
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: flex-end;
}

.carousel-content {
  color: white;
  padding: 2rem;
  max-width: 600px;
}

.carousel-content h2 {
  font-size: 2.5rem;
  margin: 0 0 1rem;
}

.carousel-content p {
  font-size: 1.1rem;
  margin: 0 0 1.5rem;
  line-height: 1.5;
}

.hero-btn {
  background-color: var(--secondary-color);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: background-color 0.3s;
  display: inline-block;
}

.hero-btn:hover {
  background-color: #3ba676;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-color);
}

.view-all {
  font-weight: 500;
  transition: color 0.2s;
}

.movie-section {
  margin-bottom: 3rem;
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}

.loading-skeleton {
  padding: 2rem;
  background-color: var(--card-bg);
  border-radius: 8px;
  margin-bottom: 2rem;
}

.error-message {
  margin: 2rem 0;
}

@media (max-width: 768px) {
  .carousel-content h2 {
    font-size: 1.8rem;
  }

  .carousel-content p {
    font-size: 1rem;
  }

  .movie-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }
}
</style>
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

.detail-button {
  width: 100%;
  margin-top: 10px;
}
</style>