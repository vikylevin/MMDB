<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const props = defineProps({
  movie: {
    type: Object,
    required: true
  }
});

const posterUrl = computed(() => {
  // 1. TMDB poster_path (string, not full URL)
  if (props.movie.poster_path && typeof props.movie.poster_path === 'string') {
    if (props.movie.poster_path.startsWith('http')) {
      return props.movie.poster_path;
    }
    return `https://image.tmdb.org/t/p/w342${props.movie.poster_path}`;
  }
  // 2. poster (full URL)
  if (props.movie.poster && typeof props.movie.poster === 'string') {
    if (props.movie.poster.startsWith('http')) {
      return props.movie.poster;
    }
    // fallback: treat as TMDB path
    return `https://image.tmdb.org/t/p/w342${props.movie.poster}`;
  }
  // 3. image (full URL)
  if (props.movie.image && typeof props.movie.image === 'string') {
    if (props.movie.image.startsWith('http')) {
      return props.movie.image;
    }
    return `https://image.tmdb.org/t/p/w342${props.movie.image}`;
  }
  // 4. posterUrl (full URL)
  if (props.movie.posterUrl && typeof props.movie.posterUrl === 'string') {
    return props.movie.posterUrl;
  }
  return '';
});

const title = computed(() => props.movie.title);
const year = computed(() => {
  if (props.movie.year) return props.movie.year;
  if (props.movie.release_date) {
    const date = new Date(props.movie.release_date);
    return date.getFullYear();
  }
  return '';
});

const rating = computed(() => {
  if (props.movie.rating) return props.movie.rating.toFixed(1);
  return props.movie.vote_average ? Number(props.movie.vote_average).toFixed(1) : '0.0';
});

const navigateToDetail = () => {
  router.push(`/movie/${props.movie.id}`);
};
</script>

<template>
  <el-card :body-style="{ padding: '0px' }" class="movie-card" @click="navigateToDetail">
    <div class="poster-container">
      <template v-if="posterUrl">
        <img :src="posterUrl" :alt="movie.title" class="movie-poster" />
      </template>
      <template v-else>
        <div class="poster-placeholder">
          <h3>{{ movie.title }}</h3>
          <p v-if="movie.release_date" class="release-date">{{ new Date(movie.release_date).getFullYear() }}</p>
        </div>
      </template>
      <div class="tmdb-rating">
        <el-icon><star-filled /></el-icon>
        <span>{{ rating }}</span>
      </div>
    </div>
    <div class="movie-info">
      <h3 class="movie-title" :title="movie.title">
        <span :title="movie.title">{{ movie.title }}</span>
      </h3>
      <p class="year">{{ year }}</p>
    </div>
  </el-card>
</template>

<style scoped>
.movie-card {
  transition: transform 0.3s ease;
  height: 100%;
  max-height: 520px;
  width: 220px;
  margin-left: auto;
  margin-right: auto;
  cursor: pointer;
}
.movie-card:hover {
  transform: translateY(-5px);
}
.poster-container {
  position: relative;
  width: 220px;
  aspect-ratio: 2/3;
  overflow: hidden;
  margin: 0 auto;
  flex: 0 0 auto;
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
.year {
  color: #666;
  margin: 5px 0;
  font-size: 0.9em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
