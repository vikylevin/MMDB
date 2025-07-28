<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import AppHeader from './components/AppHeader.vue';
import AppFooter from './components/AppFooter.vue';

// Get theme preference from localStorage
const isDarkMode = ref(localStorage.getItem('theme') === 'dark');

onMounted(() => {
  // Initialize theme
  document.body.classList.toggle('dark-mode', isDarkMode.value);
});

const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value;
  document.body.classList.toggle('dark-mode', isDarkMode.value);
  // Save user's theme preference
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light');
};
</script>

<template>
  <div class="app-container" :class="{ 'dark-mode': isDarkMode }">
    <AppHeader @toggle-dark-mode="toggleDarkMode" :dark-mode="isDarkMode" />
    <main class="main-content">
      <router-view />
    </main>
    <AppFooter />
  </div>
</template>

<style>
/* Global CSS Variables */
:root {
  --primary-color: #2c3e50;
  --secondary-color: #42b883;
  --text-color: #333;
  --bg-color: #f5f5f5;
  --card-bg: #ffffff;
  --border-color: #eaeaea;
  --container-width: 1440px;
  --content-width: 1400px;
}

/* Dark mode variables */
.dark-mode {
  --primary-color: #34495e;
  --secondary-color: #42b883;
  --text-color: #ffffff;
  --bg-color: #1a1a1a;
  --card-bg: #2c2c2c;
  --border-color: #3a3a3a;
}

/* Base Styles */
html {
  overflow-y: scroll;
}

html, body {
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
  margin: 0;
  padding: 0;
}

body {
  min-height: 100vh;
  font-family: 'Inter', 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--bg-color);
  color: var(--text-color);
}

/* Dark Mode */
body.dark-mode {
  --primary-color: #42b883;
  --secondary-color: #3eaf7c;
  --text-color: #f5f5f5;
  --bg-color: #121212;
  --card-bg: #1e1e1e;
  --border-color: #333;
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
  max-width: var(--container-width);
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: var(--content-width);
  margin: 0 auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

/* Router View Container */
.router-view-container {
  width: 100%;
  max-width: var(--content-width);
  margin: 0 auto;
}

/* Common Elements */
a {
  color: var(--secondary-color);
  text-decoration: none;
}

.el-card {
  background-color: var(--card-bg);
  border-color: var(--border-color);
  color: var(--text-color);
  transition: all 0.3s;
}

.el-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
</style>
