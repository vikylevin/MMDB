<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <h2>Profile</h2>
      </template>

      <div v-if="user" class="profile-content">
        <div class="user-info">
          <h3>User Information</h3>
          <p><strong>Username:</strong> {{ user.username }}</p>
          <p><strong>Email:</strong> {{ user.email || 'Not set' }}</p>
          <p><strong>Member since:</strong> {{ formatDate(user.created_at) }}</p>
        </div>

        <div class="profile-modules">
          <!-- Watch Later List -->
          <div class="watchlist-section" v-if="watchlist.length">
            <h3>Watch Later</h3>
            <el-row :gutter="20">
              <el-col :span="8" v-for="movie in watchlist" :key="movie.id">
                <ProfileMovieCard :movie="movie" />
              </el-col>
            </el-row>
          </div>
          <div v-else class="no-favorites">
            <p>No movies in Watch Later</p>
          </div>

          <!-- Favorites List -->
          <div class="favorite-section" v-if="favorites.length">
            <h3>Like</h3>
            <el-row :gutter="20">
              <el-col :span="8" v-for="movie in favorites" :key="movie.id">
                <ProfileMovieCard :movie="movie" />
              </el-col>
            </el-row>
          </div>
          <div v-else class="no-favorites">
            <p>No liked movies yet</p>
          </div>

          <!-- Watched List -->
          <div class="watched-section" v-if="watched.length">
            <h3>Watched</h3>
            <el-row :gutter="20">
              <el-col :span="8" v-for="movie in watched" :key="movie.id">
                <ProfileMovieCard :movie="movie" />
              </el-col>
            </el-row>
          </div>
          <div v-else class="no-favorites">
            <p>No watched movies yet</p>
          </div>
        </div>
      </div>

      <div v-else class="login-prompt">
        <p>Please log in to view your profile</p>
        <el-button type="primary" @click="$router.push('/login')">Login</el-button>
      </div>
    </el-card>
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as api from '@/services/api'
import ProfileMovieCard from '@/components/ProfileMovieCard.vue'

const router = useRouter()
const user = ref(null)
const favorites = ref([])
const watchlist = ref([])
const watched = ref([])

onMounted(() => {
  const storedUser = localStorage.getItem('user')
  const token = localStorage.getItem('access_token')

  if (storedUser && token) {
    user.value = JSON.parse(storedUser)
    fetchFavorites()
    fetchWatchlist()
    fetchWatched()
  }
})

const fetchFavorites = async () => {
  try {
    favorites.value = await api.getFavorites();
  } catch (error) {
    console.error('Error fetching favorites:', error);
    ElMessage.error('Failed to load liked movies. ' + (error.response?.data?.message || ''));
  }
}

const fetchWatchlist = async () => {
  try {
    watchlist.value = await api.getWatchlist();
  } catch (error) {
    console.error('Error fetching watchlist:', error);
    ElMessage.error('Failed to load watch later movies. ' + (error.response?.data?.message || ''));
  }
}

const fetchWatched = async () => {
  try {
    watched.value = await api.getWatched();
  } catch (error) {
    console.error('Error fetching watched:', error);
    ElMessage.error('Failed to load watched movies. ' + (error.response?.data?.message || ''));
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

const viewMovie = (movieId) => {
  router.push(`/movie/${movieId}`)
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.profile-card {
  margin-bottom: 20px;
}

.profile-content {
  padding: 20px 0;
}

.user-info {
  margin-bottom: 30px;
}

.user-info h3 {
  margin-bottom: 15px;
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

.movie-info h4 {
  margin: 0 0 10px;
  font-size: 16px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.no-favorites {
  text-align: center;
  padding: 30px;
}

.login-prompt {
  text-align: center;
  padding: 30px;
}
</style>
