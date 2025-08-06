<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { Star, StarFilled, Clock, Calendar, MessageBox } from '@element-plus/icons-vue';
import { isAuthenticated, getCurrentUser, rateMovie, getMovieRating, toggleWatchlist, toggleWatched } from '../services/api';
import { isMovieInWatchlist, updateMovieStatus, isMovieWatched } from '../stores/movieStatus';

const route = useRoute();
const router = useRouter();
const movieId = computed(() => route.params.id);

const movie = ref(null);
const reviews = ref([]);
const loading = ref(true);
const error = ref(null);
const userReview = ref({
  rating: 0,
  comment: ''
});
const reviewSubmitting = ref(false);
const showReviewForm = ref(false);
const userRating = ref(0);
const currentUser = ref(null);

// Use global state for watchlist status
const isInWatchlist = computed(() => {
  return isMovieInWatchlist(Number(movieId.value));
});

const imageBaseUrl = 'https://image.tmdb.org/t/p/original';
const posterBaseUrl = 'https://image.tmdb.org/t/p/w500';

// Check if user is authenticated
const checkAuthentication = () => {
  if (isAuthenticated()) {
    currentUser.value = getCurrentUser();
  }
};

// Load user's rating for this movie
const loadUserRating = async () => {
  if (!isAuthenticated()) return;
  
  try {
    const response = await getMovieRating(movieId.value);
    userRating.value = response.rating || 0;
  } catch (error) {
    console.error('Error loading user rating:', error);
  }
};

// Handle rating change
const handleRating = async (rating) => {
  if (!isAuthenticated()) {
    ElMessage.warning('Please log in to rate movies');
    return;
  }

  try {
    await rateMovie(movieId.value, rating);
    userRating.value = rating;
    
    // Auto-mark as watched when rating a movie (rating > 0)
    if (rating > 0) {
      // Since backend automatically adds to watched when rating, 
      // we need to update the frontend state to reflect this
      const movieIdNum = Number(movieId.value);
      updateMovieStatus(movieIdNum, 'watched', true);
    }
    
    ElMessage.success('Rating saved successfully');
  } catch (error) {
    console.error('Error saving rating:', error);
    ElMessage.error('Failed to save rating');
  }
};

const checkWatchlistStatus = async () => {
  // No longer needed as we use global state
};

const toggleWatchlistHandler = async () => {
  if (!isAuthenticated()) {
    ElMessage.warning('Please log in to add movies to your watchlist');
    return;
  }

  try {
    const response = await toggleWatchlist(movieId.value);
    // Update global state
    updateMovieStatus(Number(movieId.value), 'watchlist', response.added);
    ElMessage.success(`Movie ${response.added ? 'added to' : 'removed from'} watchlist`);
  } catch (err) {
    console.error('Error updating watchlist:', err);
    ElMessage.error('Failed to update watchlist. Please try again later.');
  }
};

const fetchMovieDetails = async () => {
  try {
    loading.value = true;
    error.value = null;

    const [movieRes, reviewsRes] = await Promise.all([
      axios.get(`http://127.0.0.1:5000/api/movie/${movieId.value}`),
      axios.get(`http://127.0.0.1:5000/api/movie/${movieId.value}/reviews`)
    ]);

    movie.value = movieRes.data;
    reviews.value = reviewsRes.data.results || [];
    // No longer need to check watchlist status as we use global state
  } catch (err) {
    console.error('Error fetching movie details:', err);
    error.value = 'Failed to load movie details. Please try again later.';
  } finally {
    loading.value = false;
  }
};

const formatRuntime = (minutes) => {
  if (!minutes) return 'N/A';
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
};

const formatReleaseDate = (dateString) => {
  if (!dateString) return 'N/A';
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

const submitReview = async () => {
  if (!isAuthenticated()) {
    ElMessage.warning('Please log in to write a review');
    return;
  }

  if (userReview.value.rating === 0) {
    ElMessage.warning('Please select a rating');
    return;
  }

  reviewSubmitting.value = true;
  try {
    // Submit review (this will also update the rating)
    await axios.post(`http://127.0.0.1:5000/api/movie/${movieId.value}/reviews`, {
      rating: userReview.value.rating,
      comment: userReview.value.comment.trim()
    }, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    });
    
    // Update local rating state
    userRating.value = userReview.value.rating;
    
    // Auto-mark as watched (backend handles this, but update frontend state)
    const movieIdNum = Number(movieId.value);
    updateMovieStatus(movieIdNum, 'watched', true);
    
    ElMessage.success('Review submitted successfully');
    showReviewForm.value = false;
    userReview.value = { rating: 0, comment: '' };
    await fetchMovieDetails(); // Refresh reviews
  } catch (err) {
    console.error('Error submitting review:', err);
    if (err.response?.data?.error) {
      ElMessage.error(`Failed to submit review: ${err.response.data.error}`);
    } else {
      ElMessage.error('Failed to submit review');
    }
  } finally {
    reviewSubmitting.value = false;
  }
};

const showReviewFormHandler = () => {
  if (!isAuthenticated()) {
    ElMessage.warning('Please log in to write a review');
    router.push('/login');
    return;
  }
  showReviewForm.value = true;
};

onMounted(() => {
  checkAuthentication();
  fetchMovieDetails();
  loadUserRating();
});
</script>

<template>
  <div class="movie-detail-view">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <el-skeleton style="width: 100%" animated>
        <template #template>
          <div style="display: flex; gap: 20px;">
            <el-skeleton-item variant="image" style="width: 300px; height: 450px" />
            <div style="flex: 1;">
              <el-skeleton-item variant="h1" style="width: 50%" />
              <el-skeleton-item variant="text" style="margin-top: 16px; width: 80%" />
              <el-skeleton-item variant="text" style="width: 60%" />
            </div>
          </div>
        </template>
      </el-skeleton>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      <el-alert :title="error" type="error" show-icon />
    </div>

    <!-- Movie Details -->
    <div v-if="!loading && !error && movie" class="movie-content">
      <!-- Backdrop -->
      <div class="movie-backdrop" :style="{
        backgroundImage: movie.backdrop_path ? 
          `linear-gradient(to bottom, rgba(0,0,0,0.7), rgba(0,0,0,0.9)), url(${imageBaseUrl}${movie.backdrop_path})` : 
          'none'
      }">
        <div class="movie-detail-container">
          <!-- Poster and Basic Info -->
          <div class="movie-detail-header">
            <div class="movie-poster">
              <img 
                :src="movie.poster_path ? `${posterBaseUrl}${movie.poster_path}` : '/placeholder-poster.jpg'" 
                :alt="movie.title" 
              />
            </div>

            <div class="movie-info">
              <h1>{{ movie.title }} <span v-if="movie.release_date">({{ new Date(movie.release_date).getFullYear() }})</span></h1>

              <div class="movie-meta">
                <div class="rating">
                  <el-icon><star-filled /></el-icon>
                  <span>{{ (Math.round(movie.vote_average * 10) / 10).toFixed(1) }}</span>
                  <span class="vote-count">({{ movie.vote_count }} votes)</span>
                </div>

                <div class="meta-item" v-if="movie.runtime">
                  <el-icon><clock /></el-icon>
                  <span>{{ formatRuntime(movie.runtime) }}</span>
                </div>

                <div class="meta-item" v-if="movie.release_date">
                  <el-icon><calendar /></el-icon>
                  <span>{{ formatReleaseDate(movie.release_date) }}</span>
                </div>
              </div>

              <div class="genres" v-if="movie.genres && movie.genres.length">
                <span v-for="genre in movie.genres" :key="genre.id" class="genre-tag">
                  {{ genre.name }}
                </span>
              </div>

              <div class="tagline" v-if="movie.tagline">
                <em>{{ movie.tagline }}</em>
              </div>

              <div class="overview">
                <h3>Overview</h3>
                <p>{{ movie.overview }}</p>
              </div>

              <div class="actions">
                <!-- User Rating Section -->
                <div class="user-rating-section">
                  <h4>Rate this movie:</h4>
                  <el-rate 
                    v-model="userRating" 
                    :max="5" 
                    @change="handleRating"
                    text-color="var(--rating-color)"
                    void-color="var(--border-color)"
                    :disabled="!isAuthenticated()"
                  />
                  <span v-if="!isAuthenticated()" class="login-hint">
                    <router-link to="/login">Login to rate</router-link>
                  </span>
                </div>

                <div class="action-buttons">
                  <el-button @click="showReviewFormHandler" class="review-btn">
                    <el-icon><message-box /></el-icon>
                    {{ isAuthenticated() ? 'Write a Review' : 'Login to Review' }}
                  </el-button>
                  <el-button @click="toggleWatchlistHandler" class="watchlist-btn">
                    <el-icon><star-filled /></el-icon>
                    {{ isInWatchlist ? 'Remove from Watchlist' : 'Add to Watchlist' }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Details -->
      <div class="movie-detail-container">
        <!-- Cast & Crew Section would go here -->

        <!-- Reviews Section -->
        <section class="reviews-section">
          <div class="section-header">
            <h2>Reviews</h2>
            <span v-if="reviews.length" class="review-count">{{ reviews.length }} reviews</span>
          </div>

          <!-- Review Form -->
          <div v-if="showReviewForm" class="review-form">
            <h3>Write a Review</h3>
            <el-form>
              <el-form-item label="Rating">
                <el-rate 
                  v-model="userReview.rating" 
                  :max="5" 
                  text-color="var(--rating-color)"
                  void-color="var(--border-color)"
                  :size="24"
                />
              </el-form-item>

              <el-form-item label="Your Review (Optional)">
                <el-input 
                  v-model="userReview.comment" 
                  type="textarea" 
                  :rows="4" 
                  placeholder="Share your thoughts about the movie (optional)"
                />
              </el-form-item>

              <el-form-item>
                <el-button @click="submitReview" :loading="reviewSubmitting" class="submit-btn">
                  Submit Review
                </el-button>
                <el-button @click="showReviewForm = false" class="cancel-btn">Cancel</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- Reviews List -->
          <div v-if="reviews.length" class="reviews-list">
            <div v-for="(review, index) in reviews" :key="index" class="review-card">
              <div class="review-header">
                <h4>{{ review.author }}</h4>
                <div class="review-rating" v-if="review.author_details && review.author_details.rating">
                  <el-icon><star-filled /></el-icon>
                  <span>{{ review.author_details.rating }}</span>
                </div>
              </div>

              <div class="review-date" v-if="review.created_at">
                {{ new Date(review.created_at).toLocaleDateString() }}
              </div>

              <div class="review-content">
                <p>{{ review.content }}</p>
              </div>
            </div>
          </div>

          <div v-else class="no-reviews">
            <p>No reviews yet. Be the first to review this movie!</p>
            <el-button @click="showReviewFormHandler" class="review-btn">
              {{ isAuthenticated() ? 'Write a Review' : 'Login to Review' }}
            </el-button>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.movie-detail-view {
  color: var(--text-color);
}

.loading-state, .error-message {
  padding: 2rem;
}

.movie-backdrop {
  background-size: cover;
  background-position: center top;
  padding: 3rem 0;
  color: white;
}

.movie-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.movie-detail-header {
  display: flex;
  gap: 2rem;
}

.movie-poster {
  flex-shrink: 0;
  width: 300px;
}

.movie-poster img {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
}

.movie-info {
  flex: 1;
}

.movie-info h1 {
  margin: 0 0 1rem;
  font-size: 2.5rem;
  font-weight: 700;
}

.movie-meta {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.rating, .meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rating .el-icon {
  color: #ffce54;
}

.vote-count {
  opacity: 0.8;
  font-size: 0.9rem;
}

.genres {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.genre-tag {
  background-color: rgba(255, 255, 255, 0.1);
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

.tagline {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  opacity: 0.8;
}

.overview h3 {
  margin: 0 0 0.5rem;
}

.overview p {
  line-height: 1.6;
  font-size: 1.1rem;
}

.actions {
  margin-top: 2rem;
}

.user-rating-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.user-rating-section h4 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-size: 1rem;
}

.login-hint {
  margin-left: 1rem;
  font-size: 0.9rem;
  color: var(--light-text);
}

.login-hint a {
  color: var(--rating-color);
  text-decoration: none;
}

.login-hint a:hover {
  text-decoration: underline;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.review-btn, .watchlist-btn, .submit-btn, .cancel-btn {
  background: var(--card-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.review-btn:hover, .watchlist-btn:hover, .submit-btn:hover {
  background: var(--hover-color);
  border-color: var(--secondary-color);
}

.cancel-btn:hover {
  background: var(--hover-color);
  border-color: var(--border-color);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 3rem 0 1.5rem;
}

.review-count {
  opacity: 0.7;
}

.reviews-list {
  display: grid;
  gap: 1.5rem;
}

.review-card {
  background-color: var(--card-bg);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.review-header h4 {
  margin: 0;
  font-size: 1.1rem;
}

.review-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #ffce54;
}

.review-date {
  font-size: 0.9rem;
  opacity: 0.7;
  margin-bottom: 1rem;
}

.review-content p {
  margin: 0;
  line-height: 1.6;
}

.no-reviews {
  text-align: center;
  padding: 2rem;
  background-color: var(--card-bg);
  border-radius: 8px;
}

.review-form {
  background-color: var(--card-bg);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Larger stars in review form */
.review-form .el-rate {
  font-size: 28px;
}

.review-form .el-rate .el-icon {
  margin-right: 8px;
}

</style>
