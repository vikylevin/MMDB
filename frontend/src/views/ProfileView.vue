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

        <div class="favorite-movies" v-if="favorites.length">
          <h3>Favorite Movies</h3>
          <el-row :gutter="20">
            <el-col :span="8" v-for="movie in favorites" :key="movie.id">
              <el-card :body-style="{ padding: '0px' }" class="movie-card">
                <img :src="movie.poster_path" class="movie-poster" />
                <div class="movie-info">
                  <h4>{{ movie.title }}</h4>
                  <el-button type="text" @click="viewMovie(movie.id)">View Details</el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        <div v-else class="no-favorites">
          <p>No favorite movies yet</p>
          <el-button type="primary" @click="$router.push('/')">Browse Movies</el-button>
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

const router = useRouter()
const user = ref(null)
const favorites = ref([])

onMounted(() => {
  const storedUser = localStorage.getItem('user')
  const token = localStorage.getItem('token')

  if (storedUser && token) {
    user.value = JSON.parse(storedUser)
    fetchFavorites()
  }
})

const fetchFavorites = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/user/favorites', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    if (response.ok) {
      favorites.value = await response.json()
    } else {
      throw new Error('Failed to fetch favorites')
    }
  } catch (error) {
    console.error('Error fetching favorites:', error)
    ElMessage.error('Failed to load favorite movies')
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
