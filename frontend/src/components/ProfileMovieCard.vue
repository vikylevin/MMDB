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
  // Handle TMDB poster_path
  if (props.movie.poster_path && typeof props.movie.poster_path === 'string') {
    if (props.movie.poster_path.startsWith('http')) {
      return props.movie.poster_path;
    }
    return `https://image.tmdb.org/t/p/w342${props.movie.poster_path}`;
  }
  // Handle poster (full URL)
  if (props.movie.poster && typeof props.movie.poster === 'string') {
    if (props.movie.poster.startsWith('http')) {
      return props.movie.poster;
    }
    return `https://image.tmdb.org/t/p/w342${props.movie.poster}`;
  }
  return '';
});

const title = computed(() => props.movie.title);

const navigateToDetail = () => {
  router.push(`/movie/${props.movie.id}`);
};
</script>

<template>
  <el-card :body-style="{ padding: '0px' }" class="profile-movie-card" @click="navigateToDetail">
    <div class="poster-container">
      <template v-if="posterUrl">
        <img :src="posterUrl" :alt="movie.title" class="movie-poster" />
      </template>
      <template v-else>
        <div class="poster-placeholder">
          <span class="movie-title-placeholder">{{ title }}</span>
        </div>
      </template>
    </div>
    <div class="movie-info">
      <h3 class="movie-title" :title="title">{{ title }}</h3>
    </div>
  </el-card>
</template>

<style scoped>
.profile-movie-card {
  transition: transform 0.3s ease;
  height: 320px;
  width: 165px;
  margin: 0 auto;
  cursor: pointer;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.profile-movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.poster-container {
  position: relative;
  width: 100%;
  height: 250px;
  overflow: hidden;
  background: var(--background-color);
  display: flex;
  align-items: center;
  justify-content: center;
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center;
  background: var(--background-color);
}

.poster-placeholder {
  width: 100%;
  height: 100%;
  background: var(--background-color);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  text-align: center;
  border: 1px solid var(--border-color);
}

.movie-title-placeholder {
  color: var(--text-color);
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.movie-info {
  padding: 12px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.movie-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-color);
  text-align: center;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Responsive design */
@media (max-width: 768px) {
  .profile-movie-card {
    width: 180px;
    height: 320px;
  }
  
  .poster-container {
    height: 240px;
  }
  
  .movie-info {
    height: 80px;
    padding: 8px;
  }
  
  .movie-title {
    font-size: 0.85rem;
  }
}
</style>
