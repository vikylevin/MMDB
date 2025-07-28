<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue';
import { Search, User } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';

defineProps({
  darkMode: Boolean
});

const router = useRouter();
const emit = defineEmits(['toggle-dark-mode']);
const searchQuery = ref('');
const isMenuOpen = ref(false);
const isSearchExpanded = ref(false);

const user = ref(null);

// Add click outside handler
const handleClickOutside = (event) => {
  const searchContainer = document.querySelector('.search-container');
  if (isSearchExpanded.value && searchContainer && !searchContainer.contains(event.target)) {
    isSearchExpanded.value = false;
    searchQuery.value = '';
  }
};

// Add event listeners when component is mounted
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  // Initial check
  updateUserState();
  // Check periodically
  const interval = setInterval(updateUserState, 1000);
  // Add storage change listener
  window.addEventListener('storage', updateUserState);
  
  // Clean up interval on unmount
  onUnmounted(() => {
    clearInterval(interval);
  });
});

// Remove event listeners when component is unmounted
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  window.removeEventListener('storage', () => {
    user.value = localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null;
  });
});

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    // Navigate to search results page with query
    window.location.href = `/search?query=${encodeURIComponent(searchQuery.value)}`;
    // After searching, collapse the search bar
    isSearchExpanded.value = false;
  }
};

const toggleSearch = () => {
  isSearchExpanded.value = !isSearchExpanded.value;
  if (isSearchExpanded.value) {
    // Focus the input when expanded
    nextTick(() => {
      document.querySelector('.search-input input').focus();
    });
  } else {
    // Clear the search query when collapsed
    searchQuery.value = '';
  }
};

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value;
};

const updateUserState = () => {
  const userStr = localStorage.getItem('user');
  const token = localStorage.getItem('access_token');
  if (userStr && token) {
    user.value = JSON.parse(userStr);
  } else {
    user.value = null;
  }
};

const handleLogin = () => {
  router.push('/login');
};

const handleLogout = () => {
  localStorage.removeItem('user');
  localStorage.removeItem('access_token');
  localStorage.removeItem('login_time');
  updateUserState();
  router.push('/login');
};
</script>

<template>
  <header class="app-header">
    <div class="header-container">
      <div class="left-section">
        <div class="logo-container">
          <router-link to="/" class="logo">
            <span class="logo-text">MMDb</span>
          </router-link>
        </div>

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
      </div>

      <div class="right-section">
        <div class="search-container" :class="{ 'expanded': isSearchExpanded }">
          <el-button 
            circle 
            class="search-icon" 
            :icon="Search" 
            @click.stop="toggleSearch"
            v-if="!isSearchExpanded"
          />
          <el-input
            v-show="isSearchExpanded"
            v-model="searchQuery"
            placeholder="Search movies..."
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
          <div class="user-menu">
            <template v-if="user">
              <el-dropdown trigger="click">
                <el-avatar :size="32" :src="user.avatar" class="user-avatar">
                  {{ user.username?.charAt(0).toUpperCase() }}
                </el-avatar>
                
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="router.push('/profile')">
                      Profile
                    </el-dropdown-item>
                    <el-dropdown-item @click="handleLogout">
                      Logout
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
            <template v-else>
              <el-button type="primary" @click="handleLogin" :icon="User">
                Login
              </el-button>
            </template>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background-color: var(--bg-color);
  border-bottom: 1px solid var(--border-color);
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
  height: 64px;
}

.header-container {
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-container {
  display: flex;
  align-items: center;
  min-width: 100px;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--secondary-color);
  text-decoration: none;
}

.left-section {
  display: flex;
  align-items: center;
  gap: 2rem;
  flex: 1;
  max-width: 600px;
}

.right-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: auto;
  min-width: 200px;
  justify-content: flex-end;
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
  position: relative;
  width: auto;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
}

.search-container.expanded {
  width: 300px;
}

.search-icon {
  z-index: 2;
}

.search-input {
  position: absolute;
  right: 0;
  width: 100%;
  opacity: 0;
  transform: translateX(10px);
  transition: all 0.3s ease;
  pointer-events: none;
}

.search-container.expanded .search-input {
  opacity: 1;
  transform: translateX(0);
  pointer-events: auto;
}

.controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-menu {
  display: flex;
  align-items: center;
}

.user-avatar {
  cursor: pointer;
}

:deep(.el-avatar) {
  cursor: pointer;
  transition: transform 0.2s ease;
}

:deep(.el-avatar:hover) {
  transform: scale(1.1);
}

:deep(.el-button) {
  height: 32px;
  padding: 0 16px;
}
</style>
Please login to add movies to your watchlist