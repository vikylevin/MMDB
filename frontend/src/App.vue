<script setup>
import { onMounted, watch } from 'vue';
import AppHeader from './components/AppHeader.vue';
import AppFooter from './components/AppFooter.vue';
import ElementThemeProvider from './components/ElementThemeProvider.vue';
import { initializeMovieStatus, clearMovieStatus } from './stores/movieStatus';
import { getWatchLater, getWatched, getLikes } from './services/api';
import { isUserAuthenticated, initializeAuth } from './stores/auth';

// Function to initialize movie status
const initializeUserMovieStatus = async () => {
  if (isUserAuthenticated.value) {
    try {
      // Load all movie statuses from backend
      const [likesResponse, watchLaterResponse, watchedResponse] = await Promise.all([
        getLikes().catch(() => []),
        getWatchLater().catch(() => []),
        getWatched().catch(() => [])
      ]);
      
      // Initialize the global status store
      // Backend returns arrays directly, not wrapped in {data: ...}
      initializeMovieStatus(
        likesResponse || [],
        watchLaterResponse || [],
        watchedResponse || []
      );
    } catch (error) {
      console.error('Error initializing movie status:', error);
    }
  } else {
    // Clear movie status when not authenticated
    clearMovieStatus();
  }
};

// Watch for authentication state changes (e.g., login/logout)
watch(isUserAuthenticated, (newAuthState) => {
  initializeUserMovieStatus();
}, { immediate: false });

// Initialize global movie status when app loads
onMounted(() => {
  initializeAuth(); // Make sure auth state is up to date
  initializeUserMovieStatus();
});
</script>

<template>
  <div class="app-container">
    <ElementThemeProvider>
      <AppHeader />
      <main class="main-content">
        <router-view />
      </main>
      <AppFooter />
    </ElementThemeProvider>
  </div>
</template>

<style>
/* Minimal CSS - theme handled by Vue */
* {
  box-sizing: border-box;
}

html {
  overflow-y: scroll;
}

html, body {
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
  margin: 0;
  padding: 0;
  font-family: var(--font-family, 'Inter', 'Avenir', Helvetica, Arial, sans-serif);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  min-width: 320px;
  min-height: 100vh;
  background-color: var(--background-color);
  color: var(--text-color);
}

img {
  max-width: 100%;
}

/* Global transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Layout Container Styles */
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  width: 100%;
}

.app-container {
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

/* Router View Container */
.router-view-container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
}

/* Basic elements - theme applied via Vue */
a {
  color: var(--text-color);
  text-decoration: none;
}

a:hover {
  color: var(--secondary-color);
}
</style>
