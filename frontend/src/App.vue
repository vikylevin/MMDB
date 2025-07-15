<script setup>
import { ref } from 'vue';
import AppHeader from './components/AppHeader.vue';
import AppFooter from './components/AppFooter.vue';

const isDarkMode = ref(false);

const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value;
  document.body.classList.toggle('dark-mode', isDarkMode.value);
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
:root {
  --primary-color: #2c3e50;
  --secondary-color: #42b883;
  --text-color: #333;
  --bg-color: #f5f5f5;
  --card-bg: #ffffff;
  --border-color: #eaeaea;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--bg-color);
  color: var(--text-color);
}

body.dark-mode {
  --primary-color: #42b883;
  --secondary-color: #3eaf7c;
  --text-color: #f5f5f5;
  --bg-color: #121212;
  --card-bg: #1e1e1e;
  --border-color: #333;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 1rem;
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
}

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
