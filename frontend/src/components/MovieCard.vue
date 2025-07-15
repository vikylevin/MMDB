<script setup>
import { ref, computed } from 'vue';
import { Star, StarFilled } from '@element-plus/icons-vue';

const props = defineProps({
  movie: {
    type: Object,
    required: true
  }
});

const imageBaseUrl = 'https://image.tmdb.org/t/p/w500';

const posterUrl = computed(() => {
  if (props.movie.poster_path) {
    return `${imageBaseUrl}${props.movie.poster_path}`;
  }
  return '/placeholder-poster.jpg';
});

const truncatedTitle = computed(() => {
  if (props.movie.title.length > 25) {
    return props.movie.title.substring(0, 25) + '...';
  }
  return props.movie.title;
});

const truncatedOverview = computed(() => {
  if (props.movie.overview.length > 100) {
    return props.movie.overview.substring(0, 100) + '...';
  }
  return props.movie.overview;
});

const releaseYear = computed(() => {
  if (props.movie.release_date) {
    return new Date(props.movie.release_date).getFullYear();
  }
  return 'N/A';
});

const roundedRating = computed(() => {
  return (Math.round(props.movie.vote_average * 10) / 10).toFixed(1);
});
</script>

<template>
  <div class="movie-card">
    <router-link :to="`/movie/${movie.id}`" class="card-link">
      <div class="poster-container">
        <img :src="posterUrl" :alt="movie.title" class="movie-poster" />
        <div class="rating">
          <el-icon><star-filled /></el-icon>
          <span>{{ roundedRating }}</span>
        </div>
      </div>
      <div class="movie-info">
        <h3 class="movie-title" :title="movie.title">{{ truncatedTitle }}</h3>
        <p class="release-year">{{ releaseYear }}</p>
        <p class="movie-overview">{{ truncatedOverview }}</p>
      </div>
    </router-link>
  </div>
</template>

<style scoped>
.movie-card {
  height: 100%;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  background-color: var(--card-bg);
  transition: transform 0.3s, box-shadow 0.3s;
}

.movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

.card-link {
  display: block;
  height: 100%;
  color: var(--text-color);
  text-decoration: none;
}

.poster-container {
  position: relative;
  aspect-ratio: 2/3;
  overflow: hidden;
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.movie-card:hover .movie-poster {
  transform: scale(1.05);
}

.rating {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.7);
  color: #ffce54;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 4px;
}

.rating .el-icon {
  color: #ffce54;
}

.movie-info {
  padding: 1rem;
}

.movie-title {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.release-year {
  color: var(--secondary-color);
  font-weight: 500;
  margin: 0 0 0.5rem;
}

.movie-overview {
  font-size: 0.9rem;
  margin: 0;
  color: var(--text-color);
  opacity: 0.8;
  line-height: 1.4;
}
</style>
