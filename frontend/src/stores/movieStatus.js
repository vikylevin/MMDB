import { ref, reactive } from 'vue';

// Movie status store for tracking likes, watch later, and watched movies
const movieStatus = reactive({
  likes: new Set(),
  watchLater: new Set(),
  watched: new Set()
});

// Initialization state
const isInitialized = ref(false);

// Methods to update status
export const updateMovieStatus = (movieId, type, isActive) => {
  const id = Number(movieId);
  // Handle legacy watchlist type
  let statusType = type;
  if (type === 'watchlist') {
    statusType = 'watchLater';
  }
  
  if (isActive) {
    movieStatus[statusType].add(id);
  } else {
    movieStatus[statusType].delete(id);
  }
};

// Methods to check status
export const isMovieLiked = (movieId) => {
  return movieStatus.likes.has(Number(movieId));
};

export const isMovieInWatchLater = (movieId) => {
  return movieStatus.watchLater.has(Number(movieId));
};

// Backward compatibility alias
export const isMovieInWatchlist = isMovieInWatchLater;

export const isMovieWatched = (movieId) => {
  return movieStatus.watched.has(Number(movieId));
};

// Check if movie status is initialized
export const isMovieStatusInitialized = () => {
  return isInitialized.value;
};

// Initialize status from API
export const initializeMovieStatus = (likes = [], watchLater = [], watched = []) => {
  // Clear existing status
  movieStatus.likes.clear();
  movieStatus.watchLater.clear();
  movieStatus.watched.clear();
  
  // Add movies to status sets
  likes.forEach(movie => {
    movieStatus.likes.add(Number(movie.tmdb_id || movie.id));
  });
  
  watchLater.forEach(movie => {
    movieStatus.watchLater.add(Number(movie.tmdb_id || movie.id));
  });
  
  watched.forEach(movie => {
    movieStatus.watched.add(Number(movie.tmdb_id || movie.id));
  });
  
  // Mark as initialized
  isInitialized.value = true;
};

// Clear initialization state (for logout)
export const clearMovieStatus = () => {
  movieStatus.likes.clear();
  movieStatus.watchLater.clear();
  movieStatus.watched.clear();
  isInitialized.value = false;
};

export { movieStatus, isInitialized };
