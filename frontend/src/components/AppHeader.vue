<script setup>
import {ref} from 'vue';
import {Search} from '@element-plus/icons-vue';

defineProps({
  darkMode: Boolean
});

const emit = defineEmits(['toggle-dark-mode']);
const searchQuery = ref('');
const isMenuOpen = ref(false);

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    // Navigate to search results page with query
    window.location.href = `/search?query=${encodeURIComponent(searchQuery.value)}`;
  }
};

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value;
};
</script>

<template>
  <header class="app-header">
    <div class="header-container">
      <div class="logo-container">
        <router-link to="/" class="logo">
          <span class="logo-text">MMDb</span>
        </router-link>
      </div>

      <div class="nav-container" :class="{ 'menu-open': isMenuOpen }">
        <nav class="main-nav">
          <ul>
            <li>
              <router-link to="/">Home</router-link>
            </li>
            <li>
              <router-link to="/movies/popular">Popular</router-link>
            </li>
            <li>
              <router-link to="/movies/top-rated">Top Rated</router-link>
            </li>
            <li>
              <router-link to="/movies/upcoming">Upcoming</router-link>
            </li>
          </ul>
        </nav>

        <div class="search-container">
          <el-input
              v-model="searchQuery"
              placeholder="Search for movies..."
              @keyup.enter="handleSearch"
              class="search-input"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch"/>
            </template>
          </el-input>
        </div>

        <div class="controls">
          <el-button
              circle
              @click="emit('toggle-dark-mode')"
              :icon="darkMode ? 'Sunny' : 'Moon'"
          />
        </div>
      </div>

      <div class="menu-toggle" @click="toggleMenu">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background-color: var(--card-bg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  max-width: 1280px;
  margin: 0 auto;
}

.logo-container {
  display: flex;
  align-items: center;
  min-width: 100px;  /* Ensuring minimum width for the logo container */
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--secondary-color);
  text-decoration: none;
}

.nav-container {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-left: 2rem;  /* Adding left margin to create more space */
}

.main-nav ul {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 1.5rem;
}

.main-nav a {
  color: var(--text-color);
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
}

.main-nav a:hover,
.main-nav a.router-link-active {
  color: var(--secondary-color);
}

.search-container {
  width: 300px;
}

.search-input {
  transition: width 0.3s;
}

.controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.menu-toggle {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  width: 30px;
  height: 21px;
  cursor: pointer;
}

.menu-toggle span {
  display: block;
  height: 3px;
  width: 100%;
  background-color: var(--text-color);
  border-radius: 3px;
  transition: all 0.3s;
}

@media (max-width: 768px) {
  .menu-toggle {
    display: flex;
  }

  .nav-container {
    position: absolute;
    top: 70px;
    left: 0;
    right: 0;
    background-color: var(--card-bg);
    flex-direction: column;
    padding: 1rem;
    gap: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transform: translateY(-150%);
    opacity: 0;
    transition: all 0.3s;
    visibility: hidden;
  }

  .nav-container.menu-open {
    transform: translateY(0);
    opacity: 1;
    visibility: visible;
  }

  .main-nav ul {
    flex-direction: column;
    align-items: center;
  }

  .search-container {
    width: 100%;
  }
}
</style>
