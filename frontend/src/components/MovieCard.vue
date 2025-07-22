<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { StarFilled, Clock } from '@element-plus/icons-vue';

const router = useRouter();
const props = defineProps({
  movie: {
    type: Object,
    required: true
  },
  isAuthenticated: { // Added: Used to check if the user is logged in
    type: Boolean,
    default: false
  }
});

const userRating = ref(0);
const showRatingTooltip = ref(false);
const addedToWatchlist = ref(false);

const posterUrl = computed(() => {
  if (props.movie.poster_path) {
    return `https://image.tmdb.org/t/p/w500${props.movie.poster_path}`;
  }
  // Support for pre-processed poster URL
  if (props.movie.poster && props.movie.poster.startsWith('http')) {
    return props.movie.poster;
  }
  return '/placeholder-poster.jpg';
});

const title = computed(() => props.movie.title);
const year = computed(() => {
  if (props.movie.year) return props.movie.year;
  if (props.movie.release_date) {
    return new Date(props.movie.release_date).getFullYear();
  }
  return 'Unknown';
});

const rating = computed(() => {
  if (props.movie.rating) return props.movie.rating;
  return Math.round(props.movie.vote_average * 10) / 10;
});

const navigateToDetail = () => {
  router.push(`/movie/${props.movie.id}`);
}

const handleRating = async (value) => {
  if (!props.isAuthenticated) {
    ElMessage.warning('Please login to rate movies');
    return;
  }
  try {
    // TODO: Implement rating API call
    userRating.value = value;
    ElMessage.success('Rating saved successfully');
  } catch (error) {
    console.error('Error saving rating:', error);
    ElMessage.error('Failed to save rating');
  }
}

const toggleWatchlist = async () => {
  if (!props.isAuthenticated) {
    ElMessage.warning('Please login to add movies to your watchlist');
    return;
  }
  try {
    // TODO: Implement add to watchlist API call
    addedToWatchlist.value = !addedToWatchlist.value;
    ElMessage.success(addedToWatchlist.value ? 'Added to watchlist' : 'Removed from watchlist');
  } catch (error) {
    console.error('Error updating watchlist:', error);
    ElMessage.error('Failed to update watchlist');
  }
}
</script>

<template>
  <el-card :body-style="{ padding: '0px' }" class="movie-card">
    <div class="poster-container" @click="navigateToDetail">
      <img :src="posterUrl" :alt="movie.title" class="movie-poster" />
      <!-- TMDB rating in top right corner -->
      <div class="tmdb-rating">
        <el-icon><star-filled /></el-icon>
        <span>{{ rating }}</span>
      </div>
    </div>
    <div class="movie-info">
      <h3 class="movie-title" :title="movie.title">{{ movie.title }}</h3>
      <p class="year">{{ year }}</p>

      <!-- User action area -->
      <div class="user-actions">
        <!-- User rating -->
        <div class="user-rating"
             @mouseenter="showRatingTooltip = true"
             @mouseleave="showRatingTooltip = false">
          <el-rate
            v-model="userRating"
            :disabled="!isAuthenticated"
            @change="handleRating"
            text-color="#ff9900"
          />
          <span v-if="!isAuthenticated" class="login-hint">Login to rate</span>
        </div>

        <!-- Watch Later button -->
        <el-button
          :type="addedToWatchlist ? 'success' : 'default'"
          size="small"
          @click="toggleWatchlist"
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
  margin-bottom: 20px;
  transition: transform 0.3s ease;
  height: 100%;
}

.movie-card:hover {
  transform: translateY(-5px);
}

.poster-container {
  position: relative;
  width: 100%;
  aspect-ratio: 2/3;
  overflow: hidden;
  cursor: pointer;
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.tmdb-rating {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
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
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.year {
  color: #666;
  margin: 5px 0;
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
  gap: 8px;
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
}

:deep(.el-rate__icon) {
  font-size: 16px;
  margin-right: 4px;
}
</style>
