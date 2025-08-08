<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick, inject } from 'vue';
import { useRouter } from 'vue-router';
import { StarFilled, Clock, View, Check } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { isAuthenticated, toggleWatchLater, toggleLike, toggleWatched, getLikes, getWatchLater, getWatched, rateMovie, getMovieRating } from '../services/api';
import { isMovieLiked, isMovieInWatchLater, isMovieWatched, updateMovieStatus, isInitialized } from '../stores/movieStatus';
import { getMovieRating as getCachedRating, updateMovieRating, isRatingsLoaded } from '../stores/movieRatings';
import { isUserAuthenticated } from '../stores/auth';

// Inject theme configuration
const theme = inject('theme');

const router = useRouter();
const props = defineProps({
  movie: {
    type: Object,
    required: true
  }
});

const userRating = ref(0);
const showRatingTooltip = ref(false);

// Get rating from cache first, then fallback to API if needed
const loadUserRating = async () => {
  if (!isAuthenticated()) {
    userRating.value = 0;
    return;
  }
  
  const movieId = Number(props.movie.tmdb_id || props.movie.id);
  if (!movieId || isNaN(movieId)) return;
  
  // Try to get from cache first
  if (isRatingsLoaded()) {
    userRating.value = getCachedRating(movieId);
    return;
  }
  
  // Fallback to API call if cache not available
  try {
    const response = await getMovieRating(movieId);
    const rating = response.rating || 0;
    userRating.value = rating;
    // Update cache
    updateMovieRating(movieId, rating);
  } catch (error) {
    console.error('Error loading user rating:', error);
    userRating.value = 0;
  }
};

// Computed properties for rating styles - back to basics
const ratingProps = computed(() => ({
  size: 'small',
  disabled: !isUserAuthenticated.value,
  allowHalf: false,
  voidColor: '#e0e0e0',
  colors: ['#ffd700', '#ffd700', '#ffd700'],
  showText: false,
  textColor: '#ffd700'
}));

// Reactive rating state
const isRated = computed(() => userRating.value > 0);
const ratingMessage = computed(() => {
  if (!isRated.value) return 'Click to rate this movie';
  return `You rated this movie ${userRating.value} star${userRating.value > 1 ? 's' : ''}`;
});

// Use computed properties based on the global status store
const addedToWatchLater = computed(() => {
  const movieId = Number(props.movie.tmdb_id || props.movie.id);
  return isMovieInWatchLater(movieId);
});

// Backward compatibility alias
const addedToWatchlist = addedToWatchLater;

const addedToLikes = computed(() => {
  const movieId = Number(props.movie.tmdb_id || props.movie.id);
  return isMovieLiked(movieId);
});

const isWatched = computed(() => {
  const movieId = Number(props.movie.tmdb_id || props.movie.id);
  return isMovieWatched(movieId);
});

const handleToggleWatched = async () => {
  if (!isAuthenticated()) {
    ElMessage.warning('Please login to mark movies as watched');
    return;
  }
  try {
    const movieId = Number(props.movie.tmdb_id || props.movie.id);
    const response = await toggleWatched(movieId);
    updateMovieStatus(movieId, 'watched', response.watched);
    if (response.watched) {
      ElMessage.success('Marked as watched');
    } else {
      ElMessage.success('Unmarked as watched');
    }
  } catch (error) {
    console.error('Error updating watched status:', error);
    ElMessage.error('Failed to update watched status');
  }
}
// Handle toggle like button
const handleToggleLike = async () => {
  if (!isAuthenticated()) {
    ElMessage.warning('Please login to like movies');
    return;
  }
  try {
    const movieId = Number(props.movie.tmdb_id || props.movie.id);
    // Toggle like
    const response = await toggleLike(movieId);
    updateMovieStatus(movieId, 'likes', response.added);
    
    if (response.added) {
      ElMessage.success('Movie liked');
      // Auto add to watched if not already
      if (!isMovieWatched(movieId)) {
        try {
          const watchedResp = await toggleWatched(movieId);
          updateMovieStatus(movieId, 'watched', watchedResp.watched);
        } catch (err) {
          // Do not affect like main flow
          console.error('Error auto-marking as watched:', err);
        }
      }
    } else {
      ElMessage.success('Movie unliked');
    }
  } catch (error) {
    console.error('Error updating like status:', error);
    ElMessage.error('Failed to update like status');
  }
};

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

// Watch authentication state changes
watch(isUserAuthenticated, (newAuthState) => {
  if (newAuthState) {
    // User logged in, load rating immediately
    loadUserRating();
  } else {
    // User logged out, clear rating
    userRating.value = 0;
  }
});

// Watch for ratings cache initialization
watch(isRatingsLoaded, (loaded) => {
  if (loaded && isAuthenticated()) {
    loadUserRating();
  }
});

// Watch for movie status initialization
watch(isInitialized, (initialized) => {
  if (initialized && isAuthenticated()) {
    loadUserRating();
  }
});

// Watch userRating changes - let CSS handle colors
watch(userRating, (newRating, oldRating) => {
  // Rating changed, let Element Plus and CSS handle the visual updates naturally
  if (newRating !== oldRating) {
    // Visual updates handled by CSS
  }
});

onMounted(() => {
  checkTextOverflow();
  // Listen for window resize events
  window.addEventListener('resize', checkTextOverflow);
  // Load user rating immediately if cache is available, otherwise wait for cache initialization
  if (isAuthenticated()) {
    loadUserRating();
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', checkTextOverflow);
});

const posterUrl = computed(() => {
  if (props.movie.poster_path) {
    // Use higher quality image for better display
    return `https://image.tmdb.org/t/p/w500${props.movie.poster_path}`;
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
    const movieId = Number(props.movie.tmdb_id || props.movie.id);
    if (!movieId || isNaN(movieId)) {
      throw new Error('Invalid movie ID');
    }
    
    await rateMovie(movieId, value);
    userRating.value = value;
    
    // Update cache
    updateMovieRating(movieId, value);
    
    // Auto-mark as watched when rating a movie (rating > 0)
    if (value > 0) {
      // Since backend automatically adds to watched when rating, 
      // we need to update the frontend state to reflect this
      updateMovieStatus(movieId, 'watched', true);
    }
    
    ElMessage({
      message: 'Rating saved successfully',
      type: 'success',
      duration: 2000
    });
    
    // Let CSS handle star colors naturally
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

const handleToggleWatchLater = async () => {
  if (!isAuthenticated()) {
    ElMessage.warning('Please login to add movies to your watch later list');
    return;
  }
  try {
    const movieId = Number(props.movie.tmdb_id || props.movie.id);
    if (!movieId || isNaN(movieId)) {
      ElMessage.error('Invalid movie id');
      return;
    }
    const response = await toggleWatchLater(movieId);
    updateMovieStatus(movieId, 'watchLater', response.added);
    if (response.added) {
      ElMessage.success('Added to watch later');
    } else {
      ElMessage.success('Removed from watch later');
    }
  } catch (error) {
    console.error('Error updating watch later:', error);
    ElMessage.error('Failed to update watch later');
  }
}

// Backward compatibility alias
const handleToggleWatchlist = handleToggleWatchLater;
</script>

<template>
  <el-card 
    :body-style="{ padding: '0px' }" 
    class="movie-card"
    :data-movie-id="movie.tmdb_id || movie.id"
  >
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
        <el-icon><StarFilled /></el-icon>
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

      <!-- User rating - simplified without background -->
      <div class="user-rating">
        <el-tooltip :content="ratingMessage" placement="top" :disabled="!isUserAuthenticated">
          <el-rate
            v-model="userRating"
            :size="ratingProps.size"
            :disabled="ratingProps.disabled"
            :allow-half="ratingProps.allowHalf"
            :void-color="ratingProps.voidColor"
            :colors="ratingProps.colors"
            :show-text="ratingProps.showText"
            :text-color="ratingProps.textColor"
            @change="handleRating"
            class="movie-rating-stars"
          />
        </el-tooltip>
      </div>

      <!-- Watch Later & Like buttons side by side, now below the rating -->
      <div class="user-actions">
        <el-tooltip content="Watch Later" placement="top">
          <el-button
            :type="addedToWatchLater ? 'success' : 'default'"
            size="small"
            @click="handleToggleWatchLater"
            class="watch-later-btn"
          >
            <el-icon>
              <Check v-if="addedToWatchLater" />
              <Clock v-else />
            </el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="Watched" placement="top">
          <el-button
            :type="isWatched ? 'primary' : 'default'"
            size="small"
            @click="handleToggleWatched"
            class="watched-btn"
          >
            <el-icon><View /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="Like" placement="top">
          <el-button
            :type="addedToLikes ? 'danger' : 'default'"
            size="small"
            @click="handleToggleLike"
            class="like-btn"
          >
            <el-icon><StarFilled /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.movie-card {
  transition: transform 0.3s ease;
  height: 520px; /* Increased from 500px to provide more space for action buttons */
  width: 220px; /* Fixed width instead of 100% to ensure consistency */
  margin-left: auto;
  margin-right: auto; /* Center the card in its container */
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

/* Status indicators */
.status-indicators {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-badge {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.status-badge .el-icon {
  font-size: 14px;
}

.status-badge .el-icon svg {
  width: 14px;
  height: 14px;
}

.like-badge {
  background-color: var(--error-color);
}

/* Backward compatibility alias */
.like-badge {
  background-color: var(--error-color);
}

.watched-badge {
  background-color: var(--text-color);
}

.watch-later-badge {
  background-color: var(--success-color);
}

/* Backward compatibility alias */
.watchlist-badge {
  background-color: var(--success-color);
}

.movie-card:hover {
  transform: translateY(-5px);
  background: var(--hover-color);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.poster-container {
  position: relative;
  width: 100%; /* Use full width of card */
  height: 300px; /* Adjusted to 2:3 aspect ratio for TMDB posters */
  overflow: hidden;
  cursor: pointer;
  margin: 0 auto; /* Center the poster in the card */
  flex: 0 0 auto; /* Prevent poster from being compressed */
  background: var(--background-color);
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover; /* Back to cover for consistent display */
  object-position: center; /* Center the poster for best overall composition */
  display: block;
  transition: transform 0.3s ease; /* Add smooth transition */
}

/* Slight zoom effect on hover for better poster appreciation */
.movie-card:hover .movie-poster {
  transform: scale(1.05);
}

.poster-placeholder {
  width: 100%;
  height: 100%;
  background: var(--background-color);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  text-align: center;
  color: var(--light-text);
  border: 1px solid var(--border-color);
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
  color: var(--text-color);
}

.poster-placeholder .release-date {
  margin: 0.5rem 0 0 0;
  font-size: 0.9em;
  opacity: 0.8;
  color: var(--light-text);
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
  padding: 8px 12px; /* Further reduced top/bottom padding */
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start; /* Changed from space-between to flex-start */
  min-height: 100px; /* Increased from 80px to provide more space for buttons */
  gap: 0; /* Remove gap completely to eliminate any spacing */
}

.movie-title {
  margin: 0 0 4px 0; /* Reduced bottom margin */
  font-size: 1.05em;
  width: 100%;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  color: var(--text-color);
  line-height: 1.3;
}

/* Title scroll animation container - for long titles */
.movie-card:hover .movie-title[data-overflow="true"] {
  position: relative;
  overflow: hidden;
  text-overflow: clip;
  white-space: nowrap;
  background: var(--card-bg);
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
  color: var(--light-text);
  margin: 0 0 4px 0; /* Reduced bottom margin */
  font-size: 0.85em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-actions {
  margin-top: auto; /* Push to bottom */
  display: flex;
  flex-direction: row;
  gap: 16px; /* Further increased gap between buttons from 12px to 16px */
  justify-content: center;
  padding-top: 0; /* Remove padding completely */
  box-sizing: border-box;
}

.user-rating {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 0; /* Remove all padding */
  margin-bottom: 8px; /* Add spacing between rating and buttons */
  box-sizing: border-box;
}

.login-hint {
  font-size: 12px;
  color: var(--light-text);
}

.watch-later-btn,
.like-btn,
.watched-btn {
  width: 36px;
  min-width: 36px;
  max-width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 0;
  margin: 0 !important; /* Force remove any default margin */
  transition: all 0.3s ease;
  border-radius: 8px;
}

/* Increase icon size in action buttons */
.watch-later-btn .el-icon,
.like-btn .el-icon,
.watched-btn .el-icon {
  font-size: 16px;
}

.watch-later-btn .el-icon svg,
.like-btn .el-icon svg,
.watched-btn .el-icon svg {
  width: 16px;
  height: 16px;
}

/* Active state styles for marked buttons */
.watch-later-btn.el-button--success {
  background-color: var(--success-color);
  border-color: var(--success-color);
  color: white;
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
}

.watched-btn.el-button--primary {
  background-color: var(--text-color);
  border-color: var(--text-color);
  color: white;
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(51, 51, 51, 0.3);
}

.like-btn.el-button--danger {
  background-color: var(--error-color);
  border-color: var(--error-color);
  color: white;
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
}

.watch-later-btn.el-button--success:hover,
.watched-btn.el-button--primary:hover,
.like-btn.el-button--danger:hover {
  transform: scale(1.15);
}

/* Simple rating styles - no background, no fancy effects */
.movie-rating-stars {
  display: inline-flex;
  justify-content: center;
  margin: 8px 0;
  
  /* Element Plus CSS variables override */
  --el-rate-void-color: #e0e0e0;
  --el-rate-fill-color: #ffd700;
  --el-rate-text-color: #ffd700;
}

/* Ensure rating and actions spacing */
.movie-card .user-rating {
  margin-bottom: 8px;
}

.movie-card .user-actions {
  padding-top: 0 !important; /* Remove all padding */
  margin-top: auto !important;
}

/* Allow some spacing between rating and actions */
.movie-card .user-rating + .user-actions {
  margin-top: 0 !important;
  padding-top: 0 !important;
}

/* Override any Element Plus default spacing */
.movie-card :deep(.el-rate) {
  margin: 8px 0;
  padding: 0;
}

.movie-card :deep(.el-button) {
  margin: 0;
}

/* Element Plus rate component - clean CSS-only approach */
:deep(.movie-rating-stars) {
  /* Use Element Plus CSS variables - this is the correct way */
  --el-rate-void-color: #e0e0e0;
  --el-rate-fill-color: #ffd700;
  --el-rate-disabled-void-color: #e0e0e0;
}

/* Ensure active stars show yellow color */
:deep(.movie-rating-stars .el-rate__icon.is-active svg),
:deep(.movie-rating-stars .el-rate__icon.is-active svg path) {
  color: #ffd700;
  fill: #ffd700;
}

/* Ensure inactive stars show gray color */
:deep(.movie-rating-stars .el-rate__icon:not(.is-active) svg),
:deep(.movie-rating-stars .el-rate__icon:not(.is-active) svg path) {
  color: #e0e0e0;
  fill: #e0e0e0;
}

/* Ensure button icons are visible with high specificity */
.user-actions .el-button .el-icon,
.user-actions .el-button .el-icon svg {
  font-size: 14px !important;
  display: inline-flex !important;
}

/* Success button (watch later added) - green background, white icon */
.user-actions .el-button--success,
.user-actions .watch-later-btn.el-button--success {
  background-color: #67c23a !important;
  border-color: #67c23a !important;
  color: white !important;
}

.user-actions .el-button--success .el-icon,
.user-actions .el-button--success .el-icon svg,
.user-actions .watch-later-btn.el-button--success .el-icon,
.user-actions .watch-later-btn.el-button--success .el-icon svg {
  color: white !important;
  fill: white !important;
}

/* Primary button (watched) - blue background, white icon */
.user-actions .el-button--primary,
.user-actions .watched-btn.el-button--primary {
  background-color: #409eff !important;
  border-color: #409eff !important;
  color: white !important;
}

.user-actions .el-button--primary .el-icon,
.user-actions .el-button--primary .el-icon svg,
.user-actions .watched-btn.el-button--primary .el-icon,
.user-actions .watched-btn.el-button--primary .el-icon svg {
  color: white !important;
  fill: white !important;
}

/* Danger button (like) - red background, white icon */
.user-actions .el-button--danger,
.user-actions .like-btn.el-button--danger {
  background-color: #f56c6c !important;
  border-color: #f56c6c !important;
  color: white !important;
}

.user-actions .el-button--danger .el-icon,
.user-actions .el-button--danger .el-icon svg,
.user-actions .like-btn.el-button--danger .el-icon,
.user-actions .like-btn.el-button--danger .el-icon svg {
  color: white !important;
  fill: white !important;
}

/* Default button - light background, black icon */
.user-actions .el-button--default .el-icon,
.user-actions .el-button--default .el-icon svg {
  color: #000000 !important;
  fill: #000000 !important;
}

/* Hover states for default buttons */
.user-actions .el-button--default:hover .el-icon,
.user-actions .el-button--default:hover .el-icon svg {
  color: white !important;
  fill: white !important;
}
</style>
