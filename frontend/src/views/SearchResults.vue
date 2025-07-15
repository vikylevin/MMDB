<template>
  <div class="search-results">
    <h2>搜索结果: "{{ searchQuery }}"</h2>
    
    <el-row :gutter="20">
      <el-col 
        v-for="movie in searchResults" 
        :key="movie.id" 
        :xs="24" 
        :sm="12" 
        :md="8" 
        :lg="6"
      >
        <el-card :body-style="{ padding: '0px' }" class="movie-card">
          <img 
            :src="getImageUrl(movie.poster_path)" 
            class="movie-poster"
          >
          <div class="movie-info">
            <h3>{{ movie.title }}</h3>
            <el-rate
              v-model="movie.vote_average"
              :max="10"
              disabled
              show-score
            />
            <el-button 
              type="primary" 
              @click="goToMovie(movie.id)"
            >
              查看详情
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty
      v-if="searchResults.length === 0"
      description="没有找到相关电影"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const searchResults = ref([])
const searchQuery = ref('')

const getImageUrl = (path) => {
  return path ? `https://image.tmdb.org/t/p/w500${path}` : '/placeholder.jpg'
}

const goToMovie = (id) => {
  router.push(`/movie/${id}`)
}

const performSearch = async () => {
  if (!route.query.q) return
  
  searchQuery.value = route.query.q
  try {
    const response = await axios.get('http://localhost:5000/api/movies/search', {
      params: { query: route.query.q }
    })
    searchResults.value = response.data.results
  } catch (error) {
    console.error('Error searching movies:', error)
  }
}

watch(() => route.query.q, performSearch)

onMounted(performSearch)
</script>

<style scoped>
.search-results {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
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
  margin-bottom: 10px;
}

h2 {
  margin-bottom: 30px;
  color: #409EFF;
}
</style>
