import { ref, reactive } from 'vue';

// Movie ratings store for caching user ratings
const movieRatings = reactive(new Map());

// Initialization state
const isRatingsInitialized = ref(false);

// Methods to update ratings
export const updateMovieRating = (movieId, rating) => {
  const id = Number(movieId);
  if (rating > 0) {
    movieRatings.set(id, rating);
  } else {
    movieRatings.delete(id);
  }
};

// Method to get rating
export const getMovieRating = (movieId) => {
  return movieRatings.get(Number(movieId)) || 0;
};

// Check if ratings are initialized
export const isRatingsLoaded = () => {
  return isRatingsInitialized.value;
};

// Initialize ratings from API data
export const initializeMovieRatings = (ratingsData = []) => {
  // Clear existing ratings
  movieRatings.clear();
  
  // Add ratings to cache
  ratingsData.forEach(item => {
    if (item.movie_id && item.rating > 0) {
      movieRatings.set(Number(item.movie_id), item.rating);
    }
  });
  
  // Mark as initialized
  isRatingsInitialized.value = true;
};

// Clear ratings cache (for logout)
export const clearMovieRatings = () => {
  movieRatings.clear();
  isRatingsInitialized.value = false;
};

export { movieRatings, isRatingsInitialized };
