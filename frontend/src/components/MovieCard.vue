<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
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
const titleRef = ref(null);
const isTextOverflow = ref(false);

// 监听标题变化和组件挂载，检查文本是否溢出
const checkTextOverflow = () => {
  if (titleRef.value && props.movie.title) {
    // 检查标题长度是否超过17个字符
    const isTitleLong = props.movie.title.length > 17;
    // 检查实际显示是否溢出
    const element = titleRef.value;
    const isOverflowing = element.scrollWidth > element.clientWidth;
    // 只有当标题长度超过17个字符且实际显示溢出时才设置为true
    isTextOverflow.value = isTitleLong && isOverflowing;
  }
};

onMounted(() => {
  checkTextOverflow();
  // 监听窗口大小变化
  window.addEventListener('resize', checkTextOverflow);
});

onUnmounted(() => {
  window.removeEventListener('resize', checkTextOverflow);
});

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
      <h3 class="movie-title" 
          :title="movie.title"
          ref="titleRef"
          :data-overflow="isTextOverflow">
          <span>{{ movie.title }}</span>
      </h3>
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

/* 创建滚动容器 */
.movie-card:hover .movie-title[data-overflow="true"] {
  position: relative;
  overflow: hidden;
  text-overflow: clip;
  white-space: nowrap;
  background: var(--el-bg-color);
}

/* 创建滚动文本 */
.movie-card:hover .movie-title[data-overflow="true"] span {
  display: inline-block;
  padding-left: 100%;
  animation: scroll-text 15s linear infinite;
  white-space: nowrap;
}

@keyframes scroll-text {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-200%);
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
