import { ref, reactive } from 'vue';

// Movie status store for tracking favorites, watchlist, and watched movies
const movieStatus = reactive({
  favorites: new Set(),
  watchlist: new Set(),
  watched: new Set()
});

// Initialization state
const isInitialized = ref(false);

// Methods to update status
export const updateMovieStatus = (movieId, type, isActive) => {
  const id = Number(movieId);
  if (isActive) {
    movieStatus[type].add(id);
  } else {
    movieStatus[type].delete(id);
  }
};

// Methods to check status
export const isMovieFavorite = (movieId) => {
  return movieStatus.favorites.has(Number(movieId));
};

export const isMovieInWatchlist = (movieId) => {
  return movieStatus.watchlist.has(Number(movieId));
};

export const isMovieWatched = (movieId) => {
  return movieStatus.watched.has(Number(movieId));
};

// Check if movie status is initialized
export const isMovieStatusInitialized = () => {
  return isInitialized.value;
};

// Initialize status from API
export const initializeMovieStatus = (favorites = [], watchlist = [], watched = []) => {
  // Clear existing status
  movieStatus.favorites.clear();
  movieStatus.watchlist.clear();
  movieStatus.watched.clear();
  
  // Add movies to status sets
  favorites.forEach(movie => {
    movieStatus.favorites.add(Number(movie.tmdb_id || movie.id));
  });
  
  watchlist.forEach(movie => {
    movieStatus.watchlist.add(Number(movie.tmdb_id || movie.id));
  });
  
  watched.forEach(movie => {
    movieStatus.watched.add(Number(movie.tmdb_id || movie.id));
  });
  
  // Mark as initialized
  isInitialized.value = true;
};

// Clear initialization state (for logout)
export const clearMovieStatus = () => {
  movieStatus.favorites.clear();
  movieStatus.watchlist.clear();
  movieStatus.watched.clear();
  isInitialized.value = false;
};

export { movieStatus, isInitialized };
