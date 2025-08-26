<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue';
import { Search, User, Menu, ArrowDown } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';
import { currentUser, setAuthState } from '../stores/auth';

const router = useRouter();
const searchQuery = ref('');
const isMenuOpen = ref(false);
const isSearchExpanded = ref(false);

// Use reactive user from auth store instead of local state
const user = currentUser;

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
});

// Remove event listeners when component is unmounted
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    // Navigate to search results page with query using Vue Router
    router.push({
      path: '/search',
      query: { query: searchQuery.value.trim() }
    });
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

const handleLogin = () => {
  router.push('/login');
};

const handleLogout = () => {
  localStorage.removeItem('user');
  localStorage.removeItem('access_token');
  localStorage.removeItem('login_time');
  // Update the auth state immediately
  setAuthState(false, null);
  router.push('/login');
};
</script>

<template>
  <div class="header-wrapper">
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
              <li class="nav-item">
                <router-link to="/" class="nav-link">Home</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/movies/popular" class="nav-link">Popular</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/movies/top-rated" class="nav-link">Top Rated</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/movies/upcoming" class="nav-link">Upcoming</router-link>
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
  
  <!-- Add divider line below header -->
  <div class="header-divider-container">
    <el-divider class="header-divider" />
  </div>
  </div>
</template>

<style scoped>
.header-wrapper {
  position: sticky;
  top: 0;
  z-index: 1000;
  background-color: var(--bg-color);
}

.app-header {
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
  color: #333;
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

.nav-item {
  position: relative;
}

.nav-link {
  color: #666;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
  padding: 0.5rem 0;
}

.nav-link:hover {
  color: #333;
}

.nav-link.router-link-active {
  color: #333;
  font-weight: 700;
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

/* Login button styling for black/white/gray theme */
:deep(.el-button--primary) {
  background-color: #2c3e50 !important;
  border-color: #34495e !important;
  color: white !important;
}

:deep(.el-button--primary:hover) {
  background-color: #34495e !important;
  border-color: #2c3e50 !important;
}

:deep(.el-button--primary:focus) {
  background-color: #2c3e50 !important;
  border-color: #34495e !important;
}

/* Header divider styling */
.header-divider-container {
  background-color: var(--bg-color);
}

.header-divider {
  margin: 0;
  border-color: var(--border-color, #e5e7eb);
}

:deep(.header-divider .el-divider__text) {
  display: none;
}
</style>
Please login to add movies to your watchlist