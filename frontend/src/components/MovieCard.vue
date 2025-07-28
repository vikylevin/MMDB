<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { StarFilled, Clock } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { isAuthenticated, toggleWatchlist } from '../services/api';

const router = useRouter();
const props = defineProps({
  movie: {
    type: Object,
    required: true
  }
});

const userRating = ref(0);
const showRatingTooltip = ref(false);
const addedToWatchlist = ref(false);
const titleRef = ref(null);
const isTextOverflow = ref(false);

// Monitor title changes and component mounting, check for text overflow
const checkTextOverflow = () => {
  if (titleRef.value && props.movie.title) {
    // Check if text is overflowing its container
    const element = titleRef.value;
    const isOverflowing = element.scrollWidth > element.clientWidth;
    isTextOverflow.value = isOverflowing;
  }
};

onMounted(() => {
  checkTextOverflow();
  // Listen for window resize events
  window.addEventListener('resize', checkTextOverflow);
});

onUnmounted(() => {
  window.removeEventListener('resize', checkTextOverflow);
});

const posterUrl = computed(() => {
  if (props.movie.poster_path) {
    // Try smaller size for better loading performance and availability
    return `https://image.tmdb.org/t/p/w342${props.movie.poster_path}`;
  }
  // Support for pre-processed poster URL
  if (props.movie.poster && props.movie.poster.startsWith('http')) {
    return props.movie.poster;
  }
  return ''; // No need for placeholder image as we show title instead
});

const title = computed(() => props.movie.title);
const year = computed(() => {
  if (props.movie.year) return props.movie.year;
  if (props.movie.release_date) {
    const date = new Date(props.movie.release_date);
    const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`;
  }
  return 'Release date unknown';
});

const rating = computed(() => {
  if (props.movie.rating) return props.movie.rating.toFixed(1);
  return props.movie.vote_average ? Number(props.movie.vote_average).toFixed(1) : '0.0';
});

const navigateToDetail = () => {
  router.push(`/movie/${props.movie.id}`);
}

const handleRating = async (value) => {
  if (!isAuthenticated()) {
    userRating.value = 0; // Reset rating if not authenticated
    ElMessage({
      message: 'Please login to rate movies',
      type: 'warning',
      duration: 2000,
      showClose: true
    });
    return;
  }
  
  try {
    // TODO: Implement rating API call
    const response = await fetch(`/api/movies/${props.movie.id}/rate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ rating: value })
    });

    if (response.ok) {
      userRating.value = value;
      ElMessage({
        message: 'Rating saved successfully',
        type: 'success',
        duration: 2000
      });
    } else {
      throw new Error('Failed to save rating');
    }
  } catch (error) {
    console.error('Error saving rating:', error);
    userRating.value = 0; // Reset rating on error
    ElMessage({
      message: 'Failed to save rating',
      type: 'error',
      duration: 2000,
      showClose: true
    });
  }
}

const handleToggleWatchlist = async () => {
  if (!isAuthenticated()) {
    ElMessage.warning('Please login to add movies to your watchlist');
    return;
  }
  try {
    const movieId = Number(props.movie.tmdb_id || props.movie.id);
    if (!movieId || isNaN(movieId)) {
      ElMessage.error('Invalid movie id');
      return;
    }
    const response = await toggleWatchlist(movieId);
    addedToWatchlist.value = response.added;
    if (response.added) {
      ElMessage.success('Added to watchlist');
    } else {
      ElMessage.success('Removed from watchlist');
    }
  } catch (error) {
    console.error('Error updating watchlist:', error);
    ElMessage.error('Failed to update watchlist');
  }
}
</script>

<template>
  <el-card :body-style="{ padding: '0px' }" class="movie-card">
    <div class="poster-container" @click="navigateToDetail">
      <template v-if="props.movie.poster_path">
        <img :src="posterUrl" :alt="movie.title" class="movie-poster" />
      </template>
      <template v-else>
        <div class="poster-placeholder">
          <h3>{{ movie.title }}</h3>
          <p v-if="movie.release_date" class="release-date">{{ new Date(movie.release_date).getFullYear() }}</p>
        </div>
      </template>
      <!-- TMDB rating in top right corner -->
      <div class="tmdb-rating">
        <el-icon><star-filled /></el-icon>
        <span>{{ rating }}</span>
      </div>
    </div>
    <div class="movie-info">
      <h3 class="movie-title" 
          :title="movie.title"
          ref="titleRef"
          :data-overflow="isTextOverflow">
          <span :title="movie.title">{{ movie.title }}</span>
      </h3>
      <p class="year">{{ year }}</p>

      <!-- User action area -->
      <div class="user-actions">
        <!-- User rating -->
        <div class="user-rating">
          <el-rate
            v-model="userRating"
            :disabled="false"
            :allow-half="false"
            @change="handleRating"
            text-color="#ff9900"
            void-color="#C6D1DE"
          />
        </div>

        <!-- Watch Later button -->
        <el-button
          :type="addedToWatchlist ? 'success' : 'default'"
          size="small"
          @click="handleToggleWatchlist"
          class="watchlist-btn"
        >
          <el-icon><Clock /></el-icon>
          {{ addedToWatchlist ? 'Added' : 'Watch Later' }}
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.movie-card {
  transition: transform 0.3s ease;
  height: 100%;
  max-height: 520px; /* Limit the maximum height of the card */
  width: 220px;  /* Fixed width for all cards */
  margin-left: auto;
  margin-right: auto; /* Center the card in its container */
}

.movie-card:hover {
  transform: translateY(-5px);
}

.poster-container {
  position: relative;
  width: 220px; /* Fixed width matching the card */
  aspect-ratio: 2/3;
  overflow: hidden;
  cursor: pointer;
  margin: 0 auto; /* Center the poster in the card */
  flex: 0 0 auto; /* Prevent poster from being compressed */
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.poster-placeholder {
  width: 100%;
  height: 100%;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  text-align: center;
  color: var(--el-text-color-regular);
  border: 1px solid var(--el-border-color-light);
}

.poster-placeholder h3 {
  margin: 0;
  font-size: 1.2em;
  font-weight: 500;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--el-text-color-primary);
}

.poster-placeholder .release-date {
  margin: 0.5rem 0 0 0;
  font-size: 0.9em;
  opacity: 0.8;
}

.tmdb-rating {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: #ffffff;
  padding: 4px 8px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.movie-info {
  padding: 14px;
}

.movie-title {
  margin: 0;
  font-size: 1.1em;
  width: 100%;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

/* Title scroll animation container */
.movie-card:hover .movie-title[data-overflow="true"] {
  position: relative;
  overflow: hidden;
  text-overflow: clip;
  white-space: nowrap;
  background: var(--el-bg-color);
}

/* Scrolling text animation */
.movie-card:hover .movie-title[data-overflow="true"] span {
  display: inline-block;
  animation: scroll-text 10s linear infinite;
  white-space: nowrap;
  padding-right: 50px; /* Space between repeated titles */
}

.movie-card:hover .movie-title[data-overflow="true"] span::after {
  content: attr(title);
  padding-left: 50px; /* Space between repeated titles */
}

@keyframes scroll-text {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

.year {
  color: #666;
  margin: 5px 0;
  font-size: 0.9em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-actions {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.user-rating {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 5px 0;
}

.login-hint {
  font-size: 12px;
  color: #999;
}

.watchlist-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

:deep(.el-rate) {
  display: inline-flex;
  line-height: 1;
  transition: all 0.3s ease;
  justify-content: center;
}

:deep(.el-rate:hover) {
  transform: scale(1.05);
}

:deep(.el-rate__icon) {
  font-size: 22px;
  margin-right: 6px;
  transition: all 0.2s ease;
}

:deep(.el-rate__icon--on) {
  color: #ff9900;
  transform: scale(1.1);
}

:deep(.el-rate__decimal) {
  position: absolute;
  top: 0;
  left: 0;
  display: inline-block;
  overflow: hidden;
}
</style>
