<script setup>
import { ref } from 'vue';
import { Search, UserFilled } from '@element-plus/icons-vue';
import AuthDialog from './AuthDialog.vue';

defineProps({
  darkMode: Boolean
});

const emit = defineEmits(['toggle-dark-mode']);
const searchQuery = ref('');
const isMenuOpen = ref(false);
const showAuthDialog = ref(false);
const currentUser = ref(null);

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    // Navigate to search results page with query
    window.location.href = `/search?query=${encodeURIComponent(searchQuery.value)}`;
  }
};

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value;
};

const handleAuthSuccess = (user) => {
  currentUser.value = user;
  showAuthDialog.value = false;
};

const handleLogout = async () => {
  try {
    await axios.post('http://localhost:5000/api/auth/logout');
    currentUser.value = null;
    ElMessage.success('Logged out successfully');
  } catch (error) {
    console.error('Logout error:', error);
    ElMessage.error('Failed to logout');
  }
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
          <!-- 用户认证按钮 -->
          <template v-if="!currentUser">
            <el-button type="primary" @click="showAuthDialog = true">
              <el-icon><user-filled /></el-icon>
              Login
            </el-button>
          </template>
          <template v-else>
            <el-dropdown trigger="click">
              <el-button>
                {{ currentUser.username }}
                <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>My Ratings</el-dropdown-item>
                  <el-dropdown-item>Watch Later</el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">
                    Logout
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>

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

    <!-- 认证对话框 -->
    <auth-dialog
      v-model="showAuthDialog"
      @auth-success="handleAuthSuccess"
    />
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
}

.header-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.logo-container {
  display: flex;
  align-items: center;
  min-width: 100px; /* Ensuring minimum width for the logo container */
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
  margin-left: 2rem; /* Adding left margin to create more space */
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

  .controls {
    flex-direction: column;
    width: 100%;
    gap: 0.5rem;
  }

  .controls .el-button {
    width: 100%;
  }
}
</style>
