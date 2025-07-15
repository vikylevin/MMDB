<template>
  <div class="movie-detail" v-if="movie">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="8">
        <img 
          :src="getImageUrl(movie.poster_path)" 
          :alt="movie.title"
          class="movie-poster"
        >
      </el-col>
      <el-col :xs="24" :sm="16">
        <div class="movie-info">
          <h1>{{ movie.title }}</h1>
          <el-rate
            v-model="movie.vote_average"
            :max="10"
            disabled
            show-score
          />
          <p class="overview">{{ movie.overview }}</p>
          
          <div class="review-section">
            <h2>评价</h2>
            <el-form @submit.prevent="submitReview">
              <el-form-item label="评分">
                <el-rate
                  v-model="newReview.rating"
                  :max="5"
                  show-score
                />
              </el-form-item>
              <el-form-item label="评论">
                <el-input
                  v-model="newReview.comment"
                  type="textarea"
                  :rows="4"
                  placeholder="写下你的观影感受..."
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="submitReview">
                  提交评价
                </el-button>
              </el-form-item>
            </el-form>
          </div>

          <div class="reviews-list" v-if="reviews.length > 0">
            <h3>用户评价</h3>
            <el-timeline>
              <el-timeline-item
                v-for="review in reviews"
                :key="review.id"
                :timestamp="formatDate(review.created_at)"
              >
                <el-card>
                  <el-rate
                    v-model="review.rating"
                    disabled
                    show-score
                  />
                  <p>{{ review.comment }}</p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const movie = ref(null)
const reviews = ref([])
const newReview = ref({
  rating: 0,
  comment: ''
})

const getImageUrl = (path) => {
  return path ? `https://image.tmdb.org/t/p/w500${path}` : '/placeholder.jpg'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

const fetchMovie = async () => {
  try {
    const response = await axios.get(`http://localhost:5000/api/movies/${route.params.id}`)
    movie.value = response.data
  } catch (error) {
    console.error('Error fetching movie details:', error)
  }
}

const fetchReviews = async () => {
  try {
    const response = await axios.get(`http://localhost:5000/api/movies/${route.params.id}/reviews`)
    reviews.value = response.data
  } catch (error) {
    console.error('Error fetching reviews:', error)
  }
}

const submitReview = async () => {
  try {
    await axios.post(
      `http://localhost:5000/api/movies/${route.params.id}/reviews`,
      newReview.value
    )
    newReview.value = { rating: 0, comment: '' }
    await fetchReviews()
  } catch (error) {
    console.error('Error submitting review:', error)
  }
}

onMounted(() => {
  fetchMovie()
  fetchReviews()
})
</script>

<style scoped>
.movie-detail {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.movie-poster {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.movie-info {
  padding: 20px;
}

.overview {
  margin: 20px 0;
  line-height: 1.6;
  color: #606266;
}

.review-section {
  margin: 30px 0;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.reviews-list {
  margin-top: 30px;
}

h1 {
  color: #303133;
  margin-bottom: 20px;
}

h2, h3 {
  color: #606266;
  margin-bottom: 15px;
}
</style>
