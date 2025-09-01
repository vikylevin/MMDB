<template>
  <div class="responsive-image-container" :style="containerStyle">
    <img
      v-if="!hasError && imageUrl"
      :src="imageUrl"
      :srcset="srcSet"
      :sizes="sizes"
      :alt="alt"
      :loading="loading"
      :class="imageClass"
      @load="handleLoad"
      @error="handleError"
    />
    <div v-else-if="hasError" class="image-error-placeholder" :style="containerStyle">
      <div class="error-content">
        <i class="error-icon">📷</i>
        <span class="error-text">Image unavailable</span>
      </div>
    </div>
    <div v-if="!isLoaded && !hasError" class="image-loading-skeleton" :style="containerStyle"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { 
  getResponsivePosterUrl, 
  generatePosterSrcSet, 
  getPlaceholderUrl 
} from '../utils/imageUtils.js';

const props = defineProps({
  // Image source path (TMDB path without base URL)
  src: {
    type: String,
    required: true
  },
  // Alt text for accessibility
  alt: {
    type: String,
    default: 'Movie poster'
  },
  // Display width for optimization
  displayWidth: {
    type: Number,
    default: 200
  },
  // Display height for aspect ratio
  displayHeight: {
    type: Number,
    default: 300
  },
  // Image loading strategy
  loading: {
    type: String,
    default: 'lazy',
    validator: (value) => ['lazy', 'eager'].includes(value)
  },
  // CSS class for the image
  imageClass: {
    type: String,
    default: ''
  },
  // Responsive sizes attribute
  responsiveSizes: {
    type: String,
    default: '(max-width: 480px) 150px, (max-width: 768px) 200px, 250px'
  }
});

const isLoaded = ref(false);
const hasError = ref(false);

// Compute optimized image URL based on display width
const imageUrl = computed(() => {
  if (!props.src) return getPlaceholderUrl(props.displayWidth, props.displayHeight);
  return getResponsivePosterUrl(props.src, props.displayWidth);
});

// Generate srcSet for different screen densities
const srcSet = computed(() => {
  if (!props.src) return '';
  
  const sizes = [
    { size: 'w185', width: 185 },
    { size: 'w342', width: 342 },
    { size: 'w500', width: 500 }
  ].filter(({ width }) => width >= props.displayWidth);
  
  return generatePosterSrcSet(props.src, sizes);
});

// Responsive sizes attribute
const sizes = computed(() => props.responsiveSizes);

// Container style for consistent aspect ratio
const containerStyle = computed(() => ({
  width: '100%',
  aspectRatio: `${props.displayWidth} / ${props.displayHeight}`,
  position: 'relative',
  overflow: 'hidden',
  backgroundColor: '#f5f5f5'
}));

const handleLoad = () => {
  isLoaded.value = true;
  hasError.value = false;
};

const handleError = () => {
  hasError.value = true;
  isLoaded.value = false;
};

onMounted(() => {
  // Reset state if src changes
  isLoaded.value = false;
  hasError.value = false;
});
</script>

<style scoped>
.responsive-image-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.responsive-image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.3s ease;
}

.image-loading-skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 2s infinite;
}

.image-error-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
}

.error-content {
  text-align: center;
  color: #6c757d;
  font-size: 12px;
}

.error-icon {
  display: block;
  font-size: 24px;
  margin-bottom: 4px;
}

.error-text {
  display: block;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Ensure images are responsive */
@media (max-width: 480px) {
  .responsive-image-container {
    max-width: 150px;
  }
}

@media (max-width: 768px) {
  .responsive-image-container {
    max-width: 200px;
  }
}
</style>
