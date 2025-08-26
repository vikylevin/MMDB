<script setup>
import { ref, nextTick, onMounted, onUnmounted, watch } from 'vue';
import { Search, User, Menu, ArrowDown } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';
import { currentUser, setAuthState } from '../stores/auth';
import axios from 'axios';

const router = useRouter();
const searchQuery = ref('');
const isMenuOpen = ref(false);
const isSearchExpanded = ref(false);

// Autocomplete functionality
const searchSuggestions = ref([]);
const showSuggestions = ref(false);
const selectedSuggestionIndex = ref(-1);
const searchTimeout = ref(null);

// API configuration
const API_URL = import.meta.env.VITE_API_BASE_URL || 'https://mmdb-f1b3.onrender.com/api';

// Use reactive user from auth store instead of local state
const user = currentUser;

// Add click outside handler
const handleClickOutside = (event) => {
  const searchContainer = document.querySelector('.search-container');
  if (isSearchExpanded.value && searchContainer && !searchContainer.contains(event.target)) {
    isSearchExpanded.value = false;
    searchQuery.value = '';
    clearSearchSuggestions();
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
    // After searching, collapse the search bar and clear suggestions
    isSearchExpanded.value = false;
    showSuggestions.value = false;
    clearSearchSuggestions();
  }
};

// Debounced search function for autocomplete
const fetchSearchSuggestions = async (query) => {
  console.log('fetchSearchSuggestions called with query:', query);
  
  if (!query.trim() || query.length < 2) {
    console.log('Query too short, clearing suggestions');
    searchSuggestions.value = [];
    showSuggestions.value = false;
    return;
  }

  try {
    console.log('Making API request to:', `${API_URL}/movie/search`);
    const response = await axios.get(`${API_URL}/movie/search`, {
      params: {
        query: query.trim(),
        page: 1
      }
    });

    console.log('API response received:', response.data);

    // Get first 5 results for suggestions
    searchSuggestions.value = response.data.results.slice(0, 5).map(movie => ({
      id: movie.id,
      title: movie.title,
      year: movie.release_date ? new Date(movie.release_date).getFullYear() : '',
      poster_path: movie.poster_path
    }));
    
    console.log('Processed suggestions:', searchSuggestions.value);
    
    showSuggestions.value = searchSuggestions.value.length > 0;
    selectedSuggestionIndex.value = -1;
    
    console.log('showSuggestions set to:', showSuggestions.value);
  } catch (error) {
    console.error('Error fetching search suggestions:', error);
    searchSuggestions.value = [];
    showSuggestions.value = false;
  }
};

// Clear search suggestions
const clearSearchSuggestions = () => {
  searchSuggestions.value = [];
  showSuggestions.value = false;
  selectedSuggestionIndex.value = -1;
};

// Handle suggestion selection
const selectSuggestion = (suggestion) => {
  router.push(`/movie/${suggestion.id}`);
  isSearchExpanded.value = false;
  clearSearchSuggestions();
  searchQuery.value = '';
};

// Handle keyboard navigation
const handleKeyDown = (event) => {
  if (!showSuggestions.value || searchSuggestions.value.length === 0) return;

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault();
      selectedSuggestionIndex.value = Math.min(
        selectedSuggestionIndex.value + 1,
        searchSuggestions.value.length - 1
      );
      break;
    case 'ArrowUp':
      event.preventDefault();
      selectedSuggestionIndex.value = Math.max(selectedSuggestionIndex.value - 1, -1);
      break;
    case 'Enter':
      event.preventDefault();
      if (selectedSuggestionIndex.value >= 0) {
        selectSuggestion(searchSuggestions.value[selectedSuggestionIndex.value]);
      } else {
        handleSearch();
      }
      break;
    case 'Escape':
      clearSearchSuggestions();
      break;
  }
};

// Watch search query for autocomplete
watch(searchQuery, (newQuery) => {
  // Clear existing timeout
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value);
  }

  // Set new timeout for debounced search
  searchTimeout.value = setTimeout(() => {
    fetchSearchSuggestions(newQuery);
  }, 300); // 300ms debounce
});

const toggleSearch = () => {
  isSearchExpanded.value = !isSearchExpanded.value;
  if (isSearchExpanded.value) {
    // Focus the input when expanded
    nextTick(() => {
      document.querySelector('.search-input input').focus();
    });
  } else {
    // Clear the search query and suggestions when collapsed
    searchQuery.value = '';
    clearSearchSuggestions();
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
          <div class="search-input-wrapper" v-show="isSearchExpanded">
            <el-input
              v-model="searchQuery"
              placeholder="Search movies..."
              @keydown="handleKeyDown"
              @blur="() => setTimeout(() => clearSearchSuggestions(), 200)"
              class="search-input"
            >
              <template #append>
                <el-button :icon="Search" @click="handleSearch"/>
              </template>
            </el-input>
            
            <!-- Search Suggestions Dropdown -->
            <div 
              v-if="showSuggestions && searchSuggestions.length > 0" 
              class="search-suggestions"
            >
              <div 
                v-for="(suggestion, index) in searchSuggestions" 
                :key="suggestion.id"
                :class="[
                  'suggestion-item', 
                  { 'selected': index === selectedSuggestionIndex }
                ]"
                @click="selectSuggestion(suggestion)"
                @mouseenter="selectedSuggestionIndex = index"
              >
                <div class="suggestion-content">
                  <div class="suggestion-title">{{ suggestion.title }}</div>
                  <div class="suggestion-year" v-if="suggestion.year">({{ suggestion.year }})</div>
                </div>
              </div>
            </div>
          </div>
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
  justify-content: flex-end;
}

.search-container.expanded {
  width: 300px;
}

.search-icon {
  z-index: 2;
}

.search-input {
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

/* Search Suggestions Styles */
.search-input-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
}

.search-suggestions {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: #ffffff;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1001;
  max-height: 300px;
  overflow-y: auto;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid #f0f2f4;
  transition: all 0.2s ease;
  background: #ffffff;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover,
.suggestion-item.selected {
  background: #f8f9fa;
}

.suggestion-content {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.suggestion-title {
  font-weight: 500;
  color: #2c3e50;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
}

.suggestion-year {
  color: #6c757d;
  font-size: 12px;
  white-space: nowrap;
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