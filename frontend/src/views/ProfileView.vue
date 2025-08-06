<template>
  <div class="profile-container">
    <!-- 个人信息模块 -->
    <el-card class="profile-info-card">
      <template #header>
        <div class="card-header">
          <el-icon><User /></el-icon>
          <span>Personal Information</span>
        </div>
      </template>
      
      <div v-if="user" class="user-info">
        <div class="info-section basic-info">
          <h4>Basic Information</h4>
          <div class="info-grid">
            <div class="info-item">
              <label>Username:</label>
              <span>{{ user.username }}</span>
            </div>
            <div class="info-item">
              <label>Email:</label>
              <span>{{ user.email || 'Not set' }}</span>
            </div>
            <div class="info-item">
              <label>Member since:</label>
              <span>{{ formatDate(user.created_at) }}</span>
            </div>
            <div class="info-item">
              <label>Full Name:</label>
              <el-input 
                v-if="isEditing" 
                v-model="userProfile.fullName" 
                placeholder="Enter your full name"
              />
              <span v-else>{{ userProfile.fullName || 'Not set' }}</span>
            </div>
          </div>
        </div>

        <div class="info-section personal-info">
          <h4>Personal Details</h4>
          <div class="info-grid">
            <div class="info-item">
              <label>Bio:</label>
              <el-input 
                v-if="isEditing" 
                v-model="userProfile.bio" 
                type="textarea" 
                :rows="3"
                placeholder="Tell us about yourself"
              />
              <span v-else class="bio-text">{{ userProfile.bio || 'No bio added yet' }}</span>
            </div>
            <div class="info-item">
              <label>Location:</label>
              <el-input 
                v-if="isEditing" 
                v-model="userProfile.location" 
                placeholder="Your location"
              />
              <span v-else>{{ userProfile.location || 'Not specified' }}</span>
            </div>
            <div class="info-item">
              <label>Birthday:</label>
              <el-date-picker
                v-if="isEditing"
                v-model="userProfile.birthday"
                type="date"
                placeholder="Select your birthday"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
              <span v-else>{{ formatDate(userProfile.birthday) || 'Not set' }}</span>
            </div>
            <div class="info-item">
              <label>Website:</label>
              <el-input 
                v-if="isEditing" 
                v-model="userProfile.website" 
                placeholder="Your website URL"
              />
              <a v-else-if="userProfile.website" :href="userProfile.website" target="_blank">{{ userProfile.website }}</a>
              <span v-else>Not set</span>
            </div>
          </div>
        </div>

        <div class="info-section movie-preferences">
          <h4>Movie Preferences</h4>
          <div class="info-grid">
            <div class="info-item">
              <label>Favorite Genres:</label>
              <el-select
                v-if="isEditing"
                v-model="userProfile.favoriteGenres"
                multiple
                placeholder="Select your favorite genres"
                style="width: 100%"
              >
                <el-option
                  v-for="genre in availableGenres"
                  :key="genre.id"
                  :label="genre.name"
                  :value="genre.name"
                />
              </el-select>
              <div v-else class="genre-tags">
                <el-tag 
                  v-for="genre in userProfile.favoriteGenres" 
                  :key="genre" 
                  size="small"
                  class="genre-tag"
                >
                  {{ genre }}
                </el-tag>
                <span v-if="!userProfile.favoriteGenres?.length">Not specified</span>
              </div>
            </div>
            <div class="info-item">
              <label>Favorite Director:</label>
              <el-input 
                v-if="isEditing" 
                v-model="userProfile.favoriteDirector" 
                placeholder="Your favorite director"
              />
              <span v-else>{{ userProfile.favoriteDirector || 'Not specified' }}</span>
            </div>
            <div class="info-item">
              <label>Favorite Actor:</label>
              <el-input 
                v-if="isEditing" 
                v-model="userProfile.favoriteActor" 
                placeholder="Your favorite actor"
              />
              <span v-else>{{ userProfile.favoriteActor || 'Not specified' }}</span>
            </div>
          </div>
        </div>

        <div class="profile-actions">
          <el-button 
            v-if="!isEditing" 
            type="primary" 
            @click="startEditing"
            :icon="Edit"
          >
            Edit Profile
          </el-button>
          <div v-else class="edit-actions">
            <el-button 
              type="primary" 
              @click="saveProfile"
              :loading="isSaving"
              :icon="Check"
            >
              Save Changes
            </el-button>
            <el-button 
              @click="cancelEditing"
              :icon="Close"
            >
              Cancel
            </el-button>
          </div>
        </div>
      </div>
      <div v-else class="login-prompt">
        <p>Please log in to view your profile</p>
        <el-button type="primary" @click="$router.push('/login')">Login</el-button>
      </div>
    </el-card>

    <!-- 汇总统计模块 -->
    <el-card class="stats-card">
      <template #header>
        <div class="card-header">
          <el-icon><DataAnalysis /></el-icon>
          <span>Movie Statistics</span>
        </div>
      </template>
      
      <div class="stats-grid">
        <div class="stat-item likes">
          <div class="stat-icon">
            <el-icon><Star /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ favorites.length }}</div>
            <div class="stat-label">Liked Movies</div>
          </div>
          <el-button text @click="activeTab = 'favorites'">View All</el-button>
        </div>
        
        <div class="stat-item watchlist">
          <div class="stat-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ watchlist.length }}</div>
            <div class="stat-label">Watch Later</div>
          </div>
          <el-button text @click="activeTab = 'watchlist'">View All</el-button>
        </div>
        
        <div class="stat-item watched">
          <div class="stat-icon">
            <el-icon><Check /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ watched.length }}</div>
            <div class="stat-label">Watched</div>
          </div>
          <el-button text @click="activeTab = 'watched'">View All</el-button>
        </div>

        <div class="stat-item reviews">
          <div class="stat-icon">
            <el-icon><Star /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ userReviews.length }}</div>
            <div class="stat-label">My Reviews</div>
          </div>
          <el-button text @click="activeTab = 'reviews'">View All</el-button>
        </div>
      </div>
    </el-card>

    <!-- 观影分析模块 -->
    <el-card class="analysis-card">
      <template #header>
        <div class="card-header">
          <el-icon><PieChart /></el-icon>
          <span>Viewing Analysis</span>
        </div>
      </template>
      
      <div class="analysis-content">
        <div class="genre-analysis">
          <h4>Favorite Genres</h4>
          <div class="genre-stats" v-if="genreStats.length">
            <div v-for="genre in genreStats.slice(0, 8)" :key="genre.name" class="genre-item">
              <span class="genre-name">{{ genre.name }}</span>
              <div class="genre-bar">
                <div class="genre-fill" :style="{ width: (genre.count / genreStats[0].count * 100) + '%' }"></div>
              </div>
              <span class="genre-count">{{ genre.count }}</span>
            </div>
          </div>
          <p v-else class="no-data">Watch more movies to see your favorite genres</p>
        </div>
      </div>
    </el-card>

    <!-- 电影列表标签页 -->
    <el-card class="movies-card">
      <template #header>
        <el-tabs v-model="activeTab" class="profile-tabs" @tab-change="handleTabChange">
          <el-tab-pane label="Liked Movies" name="favorites">
            <template #label>
              <span class="tab-label">
                <el-icon><Star /></el-icon>
                Liked ({{ favorites.length }})
              </span>
            </template>
          </el-tab-pane>
          <el-tab-pane label="Watch Later" name="watchlist">
            <template #label>
              <span class="tab-label">
                <el-icon><Clock /></el-icon>
                Watch Later ({{ watchlist.length }})
              </span>
            </template>
          </el-tab-pane>
          <el-tab-pane label="Watched" name="watched">
            <template #label>
              <span class="tab-label">
                <el-icon><Check /></el-icon>
                Watched ({{ watched.length }})
              </span>
            </template>
          </el-tab-pane>
          <el-tab-pane label="My Reviews" name="reviews">
            <template #label>
              <span class="tab-label">
                <el-icon><Star /></el-icon>
                My Reviews ({{ userReviews.length }})
              </span>
            </template>
          </el-tab-pane>
        </el-tabs>
      </template>
      
      <div class="movies-content">
        <!-- Favorites Tab -->
        <div v-if="activeTab === 'favorites'">
          <div v-if="favorites.length" class="movies-grid">
            <ProfileMovieCard v-for="movie in favorites" :key="movie.id" :movie="movie" />
          </div>
          <div v-else class="no-movies">
            <el-icon><Star /></el-icon>
            <p>No liked movies yet</p>
            <el-button @click="$router.push('/movies/popular')">Discover Movies</el-button>
          </div>
        </div>
        
        <!-- Watchlist Tab -->
        <div v-if="activeTab === 'watchlist'">
          <div v-if="watchlist.length" class="movies-grid">
            <ProfileMovieCard v-for="movie in watchlist" :key="movie.id" :movie="movie" />
          </div>
          <div v-else class="no-movies">
            <el-icon><Clock /></el-icon>
            <p>No movies in watch later list</p>
            <el-button @click="$router.push('/movies/popular')">Add Movies</el-button>
          </div>
        </div>
        
        <!-- Watched Tab -->
        <div v-if="activeTab === 'watched'">
          <div v-if="watched.length" class="movies-grid">
            <ProfileMovieCard v-for="movie in watched" :key="movie.id" :movie="movie" />
          </div>
          <div v-else class="no-movies">
            <el-icon><Check /></el-icon>
            <p>No watched movies yet</p>
            <el-button @click="$router.push('/movies/popular')">Start Watching</el-button>
          </div>
        </div>

        <!-- My Reviews Tab -->
        <div v-if="activeTab === 'reviews'">
          <div v-if="userReviews.length" class="reviews-grid">
            <div v-for="review in userReviews" :key="review.id || review.movie_id" class="review-card">
              <div class="review-movie-poster">
                <img 
                  :src="review.movie_poster ? `https://image.tmdb.org/t/p/w200${review.movie_poster}` : '/placeholder-poster.jpg'" 
                  :alt="review.movie_title" 
                />
              </div>
              <div class="review-content">
                <h4 class="movie-title">{{ review.movie_title }}</h4>
                <div class="review-rating">
                  <el-rate 
                    :model-value="review.rating" 
                    disabled 
                    text-color="var(--rating-color)"
                    void-color="var(--border-color)"
                  />
                  <span class="rating-text">{{ review.rating }}/5</span>
                </div>
                <div v-if="review.comment" class="review-text">
                  <p>{{ review.comment }}</p>
                </div>
                <div v-else class="review-text no-comment">
                  <p><em>No written review - rating only</em></p>
                </div>
                <div v-if="review.created_at" class="review-date">
                  {{ formatDate(review.created_at) }}
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-movies">
            <el-icon><Star /></el-icon>
            <p>No reviews yet</p>
            <el-button @click="$router.push('/movies/popular')">Rate Some Movies</el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { User, Star, Clock, Check, DataAnalysis, PieChart, Edit, Close } from '@element-plus/icons-vue';
import { getFavorites, getWatchlist, getWatched, getUserReviews } from '../services/api';
import ProfileMovieCard from '../components/ProfileMovieCard.vue';
import { ElMessage } from 'element-plus';
import { initializeMovieStatus } from '../stores/movieStatus';

// Data
const user = ref(null);
const favorites = ref([]);
const watchlist = ref([]);
const watched = ref([]);
const userReviews = ref([]);
const activeTab = ref('favorites');
const isEditing = ref(false);
const isSaving = ref(false);

// User profile data for editing
const userProfile = ref({
  fullName: '',
  bio: '',
  location: '',
  birthday: '',
  website: '',
  favoriteGenres: [],
  favoriteDirector: '',
  favoriteActor: ''
});

// Available genres for selection
const availableGenres = ref([
  { id: 28, name: 'Action' },
  { id: 12, name: 'Adventure' },
  { id: 16, name: 'Animation' },
  { id: 35, name: 'Comedy' },
  { id: 80, name: 'Crime' },
  { id: 99, name: 'Documentary' },
  { id: 18, name: 'Drama' },
  { id: 10751, name: 'Family' },
  { id: 14, name: 'Fantasy' },
  { id: 36, name: 'History' },
  { id: 27, name: 'Horror' },
  { id: 10402, name: 'Music' },
  { id: 9648, name: 'Mystery' },
  { id: 10749, name: 'Romance' },
  { id: 878, name: 'Science Fiction' },
  { id: 10770, name: 'TV Movie' },
  { id: 53, name: 'Thriller' },
  { id: 10752, name: 'War' },
  { id: 37, name: 'Western' }
]);

// Computed properties for analysis
const genreStats = computed(() => {
  const genreMap = new Map();
  
  // Count genres from watched movies only
  watched.value.forEach(movie => {
    if (movie.genres) {
      movie.genres.forEach(genre => {
        genreMap.set(genre.name, (genreMap.get(genre.name) || 0) + 1);
      });
    }
    // Handle genre_ids if available (from TMDB API)
    else if (movie.genre_ids && Array.isArray(movie.genre_ids)) {
      movie.genre_ids.forEach(genreId => {
        const genreObj = availableGenres.value.find(g => g.id === genreId);
        if (genreObj) {
          genreMap.set(genreObj.name, (genreMap.get(genreObj.name) || 0) + 1);
        }
      });
    }
  });
  
  return Array.from(genreMap.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);
});

// Methods
const formatDate = (dateString) => {
  if (!dateString) return 'Unknown';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

const loadUserData = () => {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    user.value = JSON.parse(userStr);
    // Load user profile data from localStorage or API
    loadUserProfile();
  }
};

const loadUserProfile = () => {
  const profileStr = localStorage.getItem('userProfile');
  if (profileStr) {
    userProfile.value = JSON.parse(profileStr);
  }
};

const startEditing = () => {
  isEditing.value = true;
};

const cancelEditing = () => {
  isEditing.value = false;
  // Reset profile data
  loadUserProfile();
};

const saveProfile = async () => {
  isSaving.value = true;
  try {
    // Save profile data to localStorage (in real app, this would be an API call)
    localStorage.setItem('userProfile', JSON.stringify(userProfile.value));
    ElMessage.success('Profile updated successfully');
    isEditing.value = false;
  } catch (error) {
    console.error('Error saving profile:', error);
    ElMessage.error('Failed to save profile');
  } finally {
    isSaving.value = false;
  }
};

const loadFavorites = async () => {
  try {
    const response = await getFavorites();
    // Backend returns array directly, not wrapped in {data: ...}
    favorites.value = Array.isArray(response) ? response : response.data || [];
  } catch (error) {
    console.error('Error loading favorites:', error);
    ElMessage.error('Failed to load favorite movies');
  }
};

const loadWatchlist = async () => {
  try {
    const response = await getWatchlist();
    // Backend returns array directly, not wrapped in {data: ...}
    watchlist.value = Array.isArray(response) ? response : response.data || [];
  } catch (error) {
    console.error('Error loading watchlist:', error);
    ElMessage.error('Failed to load watchlist');
  }
};

const loadWatched = async () => {
  try {
    const response = await getWatched();
    // Backend returns array directly, not wrapped in {data: ...}
    watched.value = Array.isArray(response) ? response : response.data || [];
  } catch (error) {
    console.error('Error loading watched movies:', error);
    ElMessage.error('Failed to load watched movies');
  }
};

const loadUserReviews = async () => {
  try {
    const response = await getUserReviews();
    userReviews.value = Array.isArray(response) ? response : response.data || [];
  } catch (error) {
    console.error('Error loading user reviews:', error);
    ElMessage.error('Failed to load user reviews');
  }
};

// Add periodic refresh for reviews when user is on reviews tab
let reviewsRefreshInterval = null;

const startReviewsRefresh = () => {
  // Clear any existing interval
  if (reviewsRefreshInterval) {
    clearInterval(reviewsRefreshInterval);
  }
  
  // Refresh reviews every 10 seconds when on reviews tab
  reviewsRefreshInterval = setInterval(() => {
    if (activeTab.value === 'reviews' && user.value) {
      loadUserReviews();
    }
  }, 10000); // 10 seconds
};

const stopReviewsRefresh = () => {
  if (reviewsRefreshInterval) {
    clearInterval(reviewsRefreshInterval);
    reviewsRefreshInterval = null;
  }
};

// Watch activeTab changes to manage refresh
const handleTabChange = (tabName) => {
  if (tabName === 'reviews') {
    startReviewsRefresh();
    // Also refresh immediately when switching to reviews tab
    loadUserReviews();
  } else {
    stopReviewsRefresh();
  }
};

const loadAllData = async () => {
  await Promise.all([
    loadFavorites(),
    loadWatchlist(),
    loadWatched(),
    loadUserReviews()
  ]);
  
  // Initialize global movie status
  initializeMovieStatus(favorites.value, watchlist.value, watched.value);
};

onMounted(() => {
  loadUserData();
  if (user.value) {
    loadAllData();
  }
  
  // Start refresh if already on reviews tab
  if (activeTab.value === 'reviews') {
    startReviewsRefresh();
  }
  
  // Add window focus listener to refresh reviews when user returns to this page
  // This ensures reviews are updated if user rated movies in other tabs/pages
  const handleWindowFocus = () => {
    if (user.value && activeTab.value === 'reviews') {
      loadUserReviews();
    }
  };
  
  window.addEventListener('focus', handleWindowFocus);
  
  // Cleanup listener on component unmount
  onUnmounted(() => {
    window.removeEventListener('focus', handleWindowFocus);
    stopReviewsRefresh(); // Clean up the interval timer
  });
});
</script>

<style scoped>
.profile-container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Personal information card */
.profile-info-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.info-section {
  padding: 1rem 0;
}

.info-section h4 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-weight: 600;
  font-size: 1.1rem;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 0.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.9rem;
}

.info-item span {
  color: var(--secondary-color);
  min-height: 1.5rem;
}

.info-item a {
  color: var(--rating-color);
  text-decoration: none;
}

.info-item a:hover {
  text-decoration: underline;
}

.bio-text {
  line-height: 1.5;
  padding: 0.5rem 0;
}

.genre-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.genre-tag {
  background: var(--hover-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.profile-actions {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: center;
}

.edit-actions {
  display: flex;
  gap: 1rem;
}

.login-prompt {
  text-align: center;
  padding: 2rem;
  color: var(--light-text);
}

/* 统计卡片 */
.stats-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: var(--hover-color);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-item.likes .stat-icon {
  background: rgba(255, 215, 0, 0.1);
  color: var(--rating-color);
}

.stat-item.watchlist .stat-icon {
  background: rgba(102, 102, 102, 0.1);
  color: var(--secondary-color);
}

.stat-item.watched .stat-icon {
  background: rgba(51, 51, 51, 0.1);
  color: var(--text-color);
}

.stat-item.reviews .stat-icon {
  background: rgba(255, 215, 0, 0.1);
  color: var(--rating-color);
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1;
}

.stat-label {
  color: var(--light-text);
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

/* 分析卡片 */
.analysis-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
}

.analysis-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.analysis-content h4 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-weight: 600;
}

.genre-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.genre-name {
  min-width: 80px;
  font-size: 0.875rem;
  color: var(--text-color);
}

.genre-bar {
  flex: 1;
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
}

.genre-fill {
  height: 100%;
  background: var(--secondary-color);
  transition: width 0.3s ease;
}

.genre-count {
  min-width: 30px;
  text-align: right;
  font-size: 0.875rem;
  color: var(--light-text);
}

.rating-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.rating-count {
  font-size: 0.875rem;
  color: var(--light-text);
}

.no-data {
  color: var(--light-text);
  text-align: center;
  padding: 2rem;
  font-style: italic;
}

/* 电影列表卡片 */
.movies-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
}

.profile-tabs {
  margin: -1rem -1rem 0 -1rem;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-color);
}

.movies-content {
  padding-top: 1rem;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}

.no-movies {
  text-align: center;
  padding: 3rem;
  color: var(--light-text);
}

.no-movies .el-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: var(--border-color);
}

.no-movies p {
  margin: 1rem 0;
  font-size: 1.1rem;
}

/* Reviews grid styles */
.reviews-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

.review-card {
  display: flex;
  gap: 1rem;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.3s ease;
}

.review-card:hover {
  background: var(--hover-color);
  transform: translateY(-2px);
}

.review-movie-poster {
  flex-shrink: 0;
  width: 80px;
  height: 120px;
  border-radius: 4px;
  overflow: hidden;
}

.review-movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.review-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.movie-title {
  margin: 0;
  color: var(--text-color);
  font-size: 1.1rem;
  font-weight: 600;
}

.review-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rating-text {
  color: var(--light-text);
  font-size: 0.9rem;
}

.review-text {
  margin: 0.5rem 0;
}

.review-text p {
  color: var(--secondary-color);
  line-height: 1.5;
  margin: 0;
}

.review-text.no-comment p {
  color: var(--light-text);
  font-style: italic;
  font-size: 0.9rem;
}

.review-date {
  color: var(--light-text);
  font-size: 0.8rem;
  margin-top: auto;
}

/* Responsive design */
@media (max-width: 768px) {
  .profile-container {
    padding: 1rem;
    gap: 1rem;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .analysis-content {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
  
  .edit-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .edit-actions .el-button {
    width: 100%;
  }
}
</style>


