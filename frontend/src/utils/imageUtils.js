/**
 * TMDB Image URL Generator with Responsive Image Support
 * Provides optimized image URLs based on display size
 */

// Available TMDB image sizes
const TMDB_POSTER_SIZES = {
  w92: 92,
  w154: 154,
  w185: 185,
  w342: 342,
  w500: 500,
  w780: 780,
  original: 'original'
};

const TMDB_BACKDROP_SIZES = {
  w300: 300,
  w780: 780,
  w1280: 1280,
  original: 'original'
};

/**
 * Get optimal poster size based on display width
 * @param {number} displayWidth - Width at which image will be displayed
 * @returns {string} - TMDB size string
 */
export function getOptimalPosterSize(displayWidth) {
  // Account for high DPI displays (multiply by 2)
  const targetWidth = displayWidth * 2;
  
  if (targetWidth <= 92) return 'w92';
  if (targetWidth <= 154) return 'w154';
  if (targetWidth <= 185) return 'w185';
  if (targetWidth <= 342) return 'w342';
  if (targetWidth <= 500) return 'w500';
  if (targetWidth <= 780) return 'w780';
  return 'original';
}

/**
 * Get optimal backdrop size based on display width
 * @param {number} displayWidth - Width at which image will be displayed
 * @returns {string} - TMDB size string
 */
export function getOptimalBackdropSize(displayWidth) {
  const targetWidth = displayWidth * 2;
  
  if (targetWidth <= 300) return 'w300';
  if (targetWidth <= 780) return 'w780';
  if (targetWidth <= 1280) return 'w1280';
  return 'original';
}

/**
 * Generate responsive poster URL
 * @param {string} posterPath - TMDB poster path
 * @param {number} displayWidth - Width at which image will be displayed
 * @returns {string} - Complete image URL
 */
export function getResponsivePosterUrl(posterPath, displayWidth = 200) {
  if (!posterPath) return null;
  
  const size = getOptimalPosterSize(displayWidth);
  return `https://image.tmdb.org/t/p/${size}${posterPath}`;
}

/**
 * Generate responsive backdrop URL
 * @param {string} backdropPath - TMDB backdrop path
 * @param {number} displayWidth - Width at which image will be displayed
 * @returns {string} - Complete image URL
 */
export function getResponsiveBackdropUrl(backdropPath, displayWidth = 1280) {
  if (!backdropPath) return null;
  
  const size = getOptimalBackdropSize(displayWidth);
  return `https://image.tmdb.org/t/p/${size}${backdropPath}`;
}

/**
 * Generate srcSet for responsive images
 * @param {string} imagePath - TMDB image path
 * @param {Array} sizes - Array of size objects {size: 'w342', width: 342}
 * @returns {string} - srcSet string
 */
export function generatePosterSrcSet(imagePath, sizes = [
  { size: 'w185', width: 185 },
  { size: 'w342', width: 342 },
  { size: 'w500', width: 500 }
]) {
  if (!imagePath) return '';
  
  return sizes
    .map(({ size, width }) => `https://image.tmdb.org/t/p/${size}${imagePath} ${width}w`)
    .join(', ');
}

/**
 * Get placeholder image URL for failed loads
 * @param {number} width - Image width
 * @param {number} height - Image height
 * @returns {string} - Placeholder URL
 */
export function getPlaceholderUrl(width = 200, height = 300) {
  return `/placeholder-poster.svg`;
}
