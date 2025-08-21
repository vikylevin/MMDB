<template>
  <div class="profile-container">
    <!-- Loading overlay -->
    <div v-if="isInitialLoading" v-loading="true" 
         element-loading-text="Loading profile..."
         element-loading-background="rgba(0, 0, 0, 0.3)"
         class="loading-container">
      <div style="height: 400px;"></div>
    </div>
    
    <!-- Profile content -->
    <div v-else>
      <!-- personal information module -->
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
              <div style="display: flex; align-items: center; justify-content: space-between;">
                <span>{{ user.email || 'Not set' }}</span>
                <el-button 
                  size="small" 
                  @click="showChangeEmailDialog = true"
                  class="change-email-btn-inline"
                >
                  Change Email
                </el-button>
              </div>
            </div>
            <div class="info-item">
              <label>Password:</label>
              <div style="display: flex; align-items: center; justify-content: space-between;">
                <span>••••••••</span>
                <el-button 
                  size="small" 
                  @click="showChangePasswordDialog = true"
                  class="change-password-btn-inline"
                >
                  Change Password
                </el-button>
              </div>
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
              <label>Preferred Genres:</label>
              <el-select
                v-if="isEditing"
                v-model="userProfile.likedGenres"
                multiple
                placeholder="Select your preferred genres"
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
                  v-for="genre in userProfile.likedGenres" 
                  :key="genre" 
                  size="small"
                  class="genre-tag"
                >
                  {{ genre }}
                </el-tag>
                <span v-if="!userProfile.likedGenres?.length">Not specified</span>
              </div>
            </div>
            <div class="info-item">
              <label>Preferred Director:</label>
              <el-input 
                v-if="isEditing" 
                v-model="userProfile.likedDirector" 
                placeholder="Your preferred director"
              />
              <span v-else>{{ userProfile.likedDirector || 'Not specified' }}</span>
            </div>
            <div class="info-item">
              <label>Preferred Actor:</label>
              <el-input 
                v-if="isEditing" 
                v-model="userProfile.likedActor" 
                placeholder="Your preferred actor"
              />
              <span v-else>{{ userProfile.likedActor || 'Not specified' }}</span>
            </div>
          </div>
        </div>

        <div class="profile-actions">
          <el-button 
            v-if="!isEditing" 
            @click="startEditing"
            :icon="Edit"
            class="edit-profile-btn"
          >
            Edit Profile
          </el-button>
          <div v-else class="edit-actions">
            <el-button 
              @click="saveProfile"
              :loading="isSaving"
              :icon="Check"
              class="save-changes-btn"
            >
              Save Changes
            </el-button>
            <el-button 
              @click="cancelEditing"
              :icon="Close"
              class="cancel-edit-btn"
            >
              Cancel
            </el-button>
          </div>
        </div>
      </div>
      <div v-else class="login-prompt">
        <p>Please log in to view your profile</p>
        <el-button @click="$router.push('/login')" class="login-btn">Login</el-button>
      </div>
    </el-card>

    <!-- Change Password Dialog -->
    <el-dialog
      v-model="showChangePasswordDialog"
      title="Change Password"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="140px"
        @submit.prevent="changePassword"
      >
        <el-form-item label="Current Password" prop="currentPassword">
          <el-input
            v-model="passwordForm.currentPassword"
            type="password"
            show-password
            placeholder="Enter current password"
          />
        </el-form-item>
        <el-form-item label="New Password" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            show-password
            placeholder="Enter new password (min 8 characters)"
          />
        </el-form-item>
        <el-form-item label="Confirm Password" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            show-password
            placeholder="Confirm new password"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showChangePasswordDialog = false">Cancel</el-button>
          <el-button 
            type="primary" 
            @click="changePassword"
            :loading="passwordChanging"
          >
            Change Password
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Change Email Dialog -->
    <el-dialog
      v-model="showChangeEmailDialog"
      title="Change Email"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="emailFormRef"
        :model="emailForm"
        :rules="emailRules"
        label-width="140px"
        @submit.prevent="changeEmail"
      >
        <el-form-item label="Current Password" prop="currentPassword">
          <el-input
            v-model="emailForm.currentPassword"
            type="password"
            show-password
            placeholder="Enter current password for verification"
          />
        </el-form-item>
        <el-form-item label="New Email" prop="newEmail">
          <el-input
            v-model="emailForm.newEmail"
            type="email"
            placeholder="Enter new email address"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showChangeEmailDialog = false">Cancel</el-button>
          <el-button 
            type="primary" 
            @click="changeEmail"
            :loading="emailChanging"
          >
            Change Email
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- summary statistics module -->
    <el-card class="stats-card" id="statistics">
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
            <div class="stat-number">{{ likes.length }}</div>
            <div class="stat-label">Liked Movies</div>
          </div>
          <el-button text @click="activeTab = 'likes'">View All</el-button>
        </div>
        
        <div class="stat-item watch-later">
          <div class="stat-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ watchLater.length }}</div>
            <div class="stat-label">Watch Later</div>
          </div>
          <el-button text @click="activeTab = 'watch-later'">View All</el-button>
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
      
      <!-- Viewing Analysis moved here under stats -->
      <div class="analysis-section">
        <h4 class="analysis-title">
          <el-icon><PieChart /></el-icon>
          Viewing Analysis
        </h4>
        <div class="genre-analysis">
          <h5>Liked Movies by Genre</h5>
          <div class="genre-stats" v-if="genreStats.length">
            <div v-for="genre in genreStats.slice(0, 10)" :key="genre.name" class="genre-item">
              <span class="genre-name">{{ genre.name }}</span>
              <div class="genre-bar">
                <div class="genre-fill" :style="{ 
                  width: (genre.count / genreStats[0].count * 100) + '%',
                  height: '20px',
                  background: `linear-gradient(135deg, #FFD700 0%, #FFA500 100%)`
                }"></div>
              </div>
              <span class="genre-count">{{ genre.count }}</span>
            </div>
          </div>
          <p v-else class="no-data">Like more movies to see your preferred genres</p>
        </div>
      </div>
    </el-card>

    <!-- movie list tabs -->
    <el-card class="movies-card" id="movie-lists">
      <template #header>
        <el-tabs v-model="activeTab" class="profile-tabs" @tab-change="handleTabChange">
          <el-tab-pane label="Liked Movies" name="likes" id="watched">
            <template #label>
              <span class="tab-label">
                <el-icon><Star /></el-icon>
                Liked ({{ likes.length }})
              </span>
            </template>
          </el-tab-pane>
          <el-tab-pane label="Watch Later" name="watch-later" id="watch-later">
            <template #label>
              <span class="tab-label">
                <el-icon><Clock /></el-icon>
                Watch Later ({{ watchLater.length }})
              </span>
            </template>
          </el-tab-pane>
          <el-tab-pane label="Watched" name="watched" id="watched-movies">
            <template #label>
              <span class="tab-label">
                <el-icon><Check /></el-icon>
                Watched ({{ watched.length }})
              </span>
            </template>
          </el-tab-pane>
          <el-tab-pane label="My Reviews" name="reviews" id="reviews">
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
        <!-- Liked Movies Tab -->
        <div v-if="activeTab === 'likes'">
          <div v-if="likes.length" class="movies-grid">
            <ProfileMovieCard v-for="movie in likes" :key="movie.id" :movie="movie" />
          </div>
          <div v-else class="no-movies">
            <el-icon><Star /></el-icon>
            <p>No liked movies yet</p>
            <el-button @click="$router.push('/movies/popular')" class="discover-movies-btn">Discover Movies</el-button>
          </div>
        </div>
        
        <!-- Watch Later Tab -->
        <div v-if="activeTab === 'watch-later'">
          <div v-if="watchLater.length" class="movies-grid">
            <ProfileMovieCard v-for="movie in watchLater" :key="movie.id" :movie="movie" />
          </div>
          <div v-else class="no-movies">
            <el-icon><Clock /></el-icon>
            <p>No movies in watch later list</p>
            <el-button @click="$router.push('/movies/popular')" class="add-movies-btn">Add Movies</el-button>
          </div>
        </div>

        <!-- Backward compatibility - Watchlist Tab (alias) -->
        <div v-if="activeTab === 'watchlist'">
          <div v-if="watchLater.length" class="movies-grid">
            <ProfileMovieCard v-for="movie in watchLater" :key="movie.id" :movie="movie" />
          </div>
          <div v-else class="no-movies">
            <el-icon><Clock /></el-icon>
            <p>No movies in watch later list</p>
            <el-button @click="$router.push('/movies/popular')" class="add-movies-btn">Add Movies</el-button>
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
            <el-button @click="$router.push('/movies/popular')" class="start-watching-btn">Start Watching</el-button>
          </div>
        </div>

        <!-- My Reviews Tab -->
        <div v-if="activeTab === 'reviews'">
          <div v-if="userReviews.length" class="reviews-grid">
            <div v-for="review in userReviews" :key="review.id || review.movie_id" class="review-card">
              <div class="review-movie-poster" @click="goToMovieDetail(review.movie_id)">
                <img 
                  :src="review.movie_poster ? `https://image.tmdb.org/t/p/w200${review.movie_poster}` : '/placeholder-poster.jpg'" 
                  :alt="review.movie_title" 
                />
                <div class="poster-overlay">
                  <el-icon><MoreFilled /></el-icon>
                  <span>View Movie</span>
                </div>
              </div>
              <div class="review-content">
                <h4 class="movie-title" @click="goToMovieDetail(review.movie_id)">{{ review.movie_title }}</h4>
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
                <div class="review-actions">
                  <el-button 
                    size="small" 
                    @click="goToMovieDetailAndEdit(review.movie_id)"
                    :icon="Edit"
                    class="edit-review-btn"
                  >
                    Edit Review
                  </el-button>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-movies">
            <el-icon><Star /></el-icon>
            <p>No reviews yet</p>
            <el-button @click="$router.push('/movies/popular')" class="rate-movies-btn">Rate Some Movies</el-button>
          </div>
        </div>
      </div>
    </el-card>
    </div> <!-- End of v-else -->
  </div> <!-- End of profile-container -->
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { User, Star, Clock, Check, DataAnalysis, PieChart, Edit, Close, MoreFilled, Lock } from '@element-plus/icons-vue';
import { getLikes, getWatchLater, getWatched, getUserReviews } from '../services/api';
import ProfileMovieCard from '../components/ProfileMovieCard.vue';
import { ElMessage } from 'element-plus';
import { initializeMovieStatus } from '../stores/movieStatus';
import { initializeMovieRatings } from '../stores/movieRatings';
import axios from 'axios';

const router = useRouter();

// Data
const user = ref(null);
const likes = ref([]);
const watchLater = ref([]);

// Backward compatibility alias
const watchlist = watchLater;
const watched = ref([]);
const userReviews = ref([]);
const activeTab = ref('likes');
const isEditing = ref(false);
const isSaving = ref(false);
const isInitialLoading = ref(true);

// User profile data for editing
const userProfile = ref({
  fullName: '',
  bio: '',
  location: '',
  birthday: '',
  website: '',
  likedGenres: [],
  likedDirector: '',
  likedActor: ''
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

// Account Security Data
const showChangePasswordDialog = ref(false);
const showChangeEmailDialog = ref(false);
const passwordChanging = ref(false);
const emailChanging = ref(false);
const passwordFormRef = ref();
const emailFormRef = ref();

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const emailForm = ref({
  currentPassword: '',
  newEmail: ''
});

// Form validation rules
const passwordRules = {
  currentPassword: [
    { required: true, message: 'Please enter your current password', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: 'Please enter a new password', trigger: 'blur' },
    { min: 8, message: 'Password must be at least 8 characters long', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: 'Please confirm your new password', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.value.newPassword) {
          callback(new Error('Passwords do not match'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ]
};

const emailRules = {
  currentPassword: [
    { required: true, message: 'Please enter your current password', trigger: 'blur' }
  ],
  newEmail: [
    { required: true, message: 'Please enter a new email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
  ]
};

const API_URL = import.meta.env.VITE_API_BASE_URL || 'https://mmdb-f1b3.onrender.com/api';

// Computed properties for analysis
const genreStats = computed(() => {
  const genreMap = new Map();
  
  // Count genres from liked movies only
  likes.value.forEach(movie => {
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

const loadLikes = async () => {
  try {

    const response = await getLikes();
    // Backend returns array directly, not wrapped in {data: ...}
    likes.value = Array.isArray(response) ? response : response.data || [];

  } catch (error) {
    console.error('Error loading likes:', error);
    let errorMessage = 'Failed to load liked movies';
    
    if (error.response) {
      if (error.response.status === 401) {
        errorMessage = 'Please log in again to view your liked movies';
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        router.push('/login');
      } else if (error.response.data?.error) {
        errorMessage = `Failed to load liked movies: ${error.response.data.error}`;
      }
    } else if (error.request) {
      errorMessage = 'Network error - please check your connection';
    }
    
    ElMessage.error(errorMessage);
    likes.value = [];
  }
};

const loadWatchLater = async () => {
  try {

    const response = await getWatchLater();
    // Backend returns array directly, not wrapped in {data: ...}
    watchLater.value = Array.isArray(response) ? response : response.data || [];

  } catch (error) {
    console.error('Error loading watch later:', error);
    let errorMessage = 'Failed to load watch later';
    
    if (error.response) {
      if (error.response.status === 401) {
        errorMessage = 'Please log in again to view your watch later list';
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        router.push('/login');
      } else if (error.response.data?.error) {
        errorMessage = `Failed to load watch later: ${error.response.data.error}`;
      }
    } else if (error.request) {
      errorMessage = 'Network error - please check your connection';
    }
    
    ElMessage.error(errorMessage);
    watchLater.value = [];
  }
};

// Backward compatibility alias
const loadWatchlist = loadWatchLater;

const loadWatched = async () => {
  try {

    const response = await getWatched();
    // Backend returns array directly, not wrapped in {data: ...}
    watched.value = Array.isArray(response) ? response : response.data || [];

  } catch (error) {
    console.error('Error loading watched movies:', error);
    let errorMessage = 'Failed to load watched movies';
    
    if (error.response) {
      if (error.response.status === 401) {
        errorMessage = 'Please log in again to view your watched movies';
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        router.push('/login');
      } else if (error.response.data?.error) {
        errorMessage = `Failed to load watched movies: ${error.response.data.error}`;
      }
    } else if (error.request) {
      errorMessage = 'Network error - please check your connection';
    }
    
    ElMessage.error(errorMessage);
    watched.value = [];
  }
};

const loadUserReviews = async () => {
  try {

    const response = await getUserReviews();
    userReviews.value = Array.isArray(response) ? response : response.data || [];

  } catch (error) {
    console.error('Error loading user reviews:', error);
    let errorMessage = 'Failed to load user reviews';
    
    if (error.response) {
      if (error.response.status === 401) {
        errorMessage = 'Please log in again to view your reviews';
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        router.push('/login');
      } else if (error.response.data?.error) {
        errorMessage = `Failed to load reviews: ${error.response.data.error}`;
      }
    } else if (error.request) {
      errorMessage = 'Network error - please check your connection';
    }
    
    ElMessage.error(errorMessage);
    userReviews.value = [];
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

// Navigation functions for movie reviews
const goToMovieDetail = (movieId) => {
  if (movieId) {
    router.push(`/movie/${movieId}`);
  }
};

const goToMovieDetailAndEdit = (movieId) => {
  if (movieId) {
    // Navigate to movie detail page and store intent to edit review
    sessionStorage.setItem('editReviewIntent', 'true');
    router.push(`/movie/${movieId}`);
  }
};

const loadAllData = async () => {
  try {
    await Promise.all([
      loadLikes(),
      loadWatchLater(),
      loadWatched(),
      loadUserReviews()
    ]);
    
    // Initialize global movie status
    initializeMovieStatus(likes.value, watchLater.value, watched.value);
    
    // Initialize movie ratings cache
    initializeMovieRatings(userReviews.value);
  } catch (error) {
    console.error('Error loading profile data:', error);
    ElMessage.error('Failed to load profile data');
  } finally {
    isInitialLoading.value = false;
  }
};

// Account Security Methods
const changePassword = async () => {
  if (!passwordFormRef.value) return;
  
  try {
    await passwordFormRef.value.validate();
    passwordChanging.value = true;
    
    const token = localStorage.getItem('access_token');
    if (!token) {
      ElMessage.error('Please log in again');
      router.push('/login');
      return;
    }
    
    const response = await axios.put(
      `${API_URL}/user/change-password`,
      {
        current_password: passwordForm.value.currentPassword,
        new_password: passwordForm.value.newPassword
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    ElMessage.success('Password changed successfully');
    showChangePasswordDialog.value = false;
    
    // Clear form
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    };
    passwordFormRef.value.resetFields();
    
  } catch (error) {
    console.error('Error changing password:', error);
    let errorMessage = 'Failed to change password';
    
    if (error.response?.data?.error) {
      errorMessage = error.response.data.error;
    } else if (error.response?.status === 401) {
      errorMessage = 'Current password is incorrect';
    }
    
    ElMessage.error(errorMessage);
  } finally {
    passwordChanging.value = false;
  }
};

const changeEmail = async () => {
  if (!emailFormRef.value) return;
  
  try {
    await emailFormRef.value.validate();
    emailChanging.value = true;
    
    const token = localStorage.getItem('access_token');
    if (!token) {
      ElMessage.error('Please log in again');
      router.push('/login');
      return;
    }
    
    const response = await axios.put(
      `${API_URL}/user/change-email`,
      {
        current_password: emailForm.value.currentPassword,
        new_email: emailForm.value.newEmail
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    ElMessage.success('Email changed successfully');
    
    // Update user data in localStorage
    if (response.data.user) {
      const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
      currentUser.email = response.data.user.email;
      localStorage.setItem('user', JSON.stringify(currentUser));
      user.value = currentUser;
    }
    
    showChangeEmailDialog.value = false;
    
    // Clear form
    emailForm.value = {
      currentPassword: '',
      newEmail: ''
    };
    emailFormRef.value.resetFields();
    
  } catch (error) {
    console.error('Error changing email:', error);
    let errorMessage = 'Failed to change email';
    
    if (error.response?.data?.error) {
      errorMessage = error.response.data.error;
    } else if (error.response?.status === 401) {
      errorMessage = 'Current password is incorrect';
    }
    
    ElMessage.error(errorMessage);
  } finally {
    emailChanging.value = false;
  }
};

onMounted(async () => {
  loadUserData();
  if (user.value) {
    await loadAllData();
  } else {
    // If no user, still stop loading
    isInitialLoading.value = false;
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
  
  // Listen for footer navigation events
  const handleProfileTabChange = (event) => {
    if (event.detail) {
      activeTab.value = event.detail;
      // Scroll to the movies card section
      setTimeout(() => {
        const moviesCard = document.getElementById('movie-lists');
        if (moviesCard) {
          moviesCard.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    }
  };
  
  window.addEventListener('focus', handleWindowFocus);
  window.addEventListener('profileTabChange', handleProfileTabChange);
  
  // Cleanup listener on component unmount
  onUnmounted(() => {
    window.removeEventListener('focus', handleWindowFocus);
    window.removeEventListener('profileTabChange', handleProfileTabChange);
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

/* Loading container */
.loading-container {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
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

.info-item {
  position: relative;
}

.change-password-btn-inline,
.change-email-btn-inline {
  margin-left: 10px !important;
  padding: 8px 16px !important;
  font-size: 14px !important;
  height: auto !important;
  background: #ff6b35 !important;
  border-color: #ff6b35 !important;
  color: white !important;
  border-radius: 6px !important;
  transition: all 0.3s ease !important;
  display: inline-block !important;
  visibility: visible !important;
  opacity: 1 !important;
  font-weight: 600 !important;
  box-shadow: 0 2px 4px rgba(255, 107, 53, 0.3) !important;
}

.change-password-btn-inline:hover,
.change-email-btn-inline:hover {
  background: #e55a2b !important;
  border-color: #e55a2b !important;
  color: white !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 8px rgba(255, 107, 53, 0.4) !important;
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

/* stats card */
.stats-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
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

.stat-item.watch-later .stat-icon {
  background: rgba(102, 102, 102, 0.1);
  color: var(--secondary-color);
}

/* Backward compatibility */
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

/* Analysis section within stats card */
.analysis-section {
  border-top: 2px solid var(--border-color);
  padding-top: 2rem;
}

.analysis-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1.5rem 0;
  color: var(--text-color);
  font-weight: 600;
  font-size: 1.2rem;
}

.genre-analysis {
  width: 100%;
}

.genre-analysis h5 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-weight: 600;
  font-size: 1rem;
}

.genre-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.genre-item:hover {
  background: var(--hover-color);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.genre-name {
  min-width: 120px;
  font-size: 0.9rem;
  color: var(--text-color);
  font-weight: 600;
}

.genre-bar {
  flex: 1;
  height: 20px;
  background: var(--border-color);
  border-radius: 10px;
  overflow: hidden;
  position: relative;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.genre-fill {
  height: 100%;
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  transition: all 0.4s ease;
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}

.genre-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, 
    rgba(255, 255, 255, 0.3) 0%, 
    rgba(255, 255, 255, 0.1) 50%, 
    rgba(255, 255, 255, 0.3) 100%);
  border-radius: 10px;
}

.genre-count {
  min-width: 40px;
  text-align: right;
  font-size: 0.9rem;
  color: var(--text-color);
  font-weight: 600;
  background: var(--card-bg);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  border: 1px solid var(--border-color);
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

/* movie list card */
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
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1rem;
  justify-items: center;
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
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
}

.review-movie-poster:hover {
  transform: scale(1.05);
}

.review-movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.3s ease;
}

.review-movie-poster:hover img {
  filter: brightness(0.7);
}

.poster-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.8rem;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.review-movie-poster:hover .poster-overlay {
  opacity: 1;
}

.poster-overlay .el-icon {
  font-size: 20px;
  margin-bottom: 4px;
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
  cursor: pointer;
  transition: color 0.3s ease;
}

.movie-title:hover {
  color: var(--rating-color);
  text-decoration: underline;
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

.review-actions {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-color);
}

.review-actions .el-button {
  font-size: 0.85rem;
}

/* Unified edit review button styling to match movie detail page theme */
.review-actions .edit-review-btn {
  background: #2c3e50 !important;
  border-color: #2c3e50 !important;
  color: white !important;
  font-weight: 600 !important;
  border-radius: 6px !important;
  padding: 8px 16px !important;
  transition: all 0.3s ease !important;
}

.review-actions .edit-review-btn:hover {
  background: #34495e !important;
  border-color: #34495e !important;
  color: white !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(44, 62, 80, 0.3);
}

/* Unified styling for the rate movies button */
.no-movies .rate-movies-btn {
  background: #2c3e50 !important;
  border-color: #2c3e50 !important;
  color: white !important;
  font-weight: 600 !important;
  border-radius: 6px !important;
  padding: 8px 16px !important;
  transition: all 0.3s ease !important;
}

.no-movies .rate-movies-btn:hover {
  background: #34495e !important;
  border-color: #34495e !important;
  color: white !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(44, 62, 80, 0.3);
}

/* Unified styling for Personal Information module buttons */
.profile-actions .edit-profile-btn,
.edit-actions .save-changes-btn,
.login-prompt .login-btn {
  background: #2c3e50 !important;
  border-color: #2c3e50 !important;
  color: white !important;
  font-weight: 600 !important;
  border-radius: 6px !important;
  padding: 8px 16px !important;
  transition: all 0.3s ease !important;
}

.profile-actions .edit-profile-btn:hover,
.edit-actions .save-changes-btn:hover,
.login-prompt .login-btn:hover {
  background: #34495e !important;
  border-color: #34495e !important;
  color: white !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(44, 62, 80, 0.3);
}

.edit-actions .cancel-edit-btn {
  background: #f8f9fa !important;
  border-color: #dee2e6 !important;
  color: #6c757d !important;
  font-weight: 500 !important;
  border-radius: 6px !important;
  padding: 8px 16px !important;
  transition: all 0.3s ease !important;
}

.edit-actions .cancel-edit-btn:hover {
  background: #e9ecef !important;
  border-color: #adb5bd !important;
  color: #495057 !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Unified styling for all other action buttons in profile */
.no-movies .discover-movies-btn,
.no-movies .add-movies-btn,
.no-movies .start-watching-btn {
  background: #2c3e50 !important;
  border-color: #2c3e50 !important;
  color: white !important;
  font-weight: 600 !important;
  border-radius: 6px !important;
  padding: 8px 16px !important;
  transition: all 0.3s ease !important;
}

.no-movies .discover-movies-btn:hover,
.no-movies .add-movies-btn:hover,
.no-movies .start-watching-btn:hover {
  background: #34495e !important;
  border-color: #34495e !important;
  color: white !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(44, 62, 80, 0.3);
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
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 0.8rem;
  }
  
  .edit-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .edit-actions .el-button {
    width: 100%;
  }
}

/* Account Security Card Styles */
.security-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
}

.security-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--bg-color);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.security-info h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
  font-size: 1.1rem;
  font-weight: 600;
}

.security-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.change-password-btn,
.change-email-btn {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.change-password-btn:hover,
.change-email-btn:hover {
  background: var(--primary-color-hover);
  border-color: var(--primary-color-hover);
  transform: translateY(-1px);
}

/* Dialog Form Styles */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

/* Responsive design for security section */
@media (max-width: 768px) {
  .security-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .change-password-btn,
  .change-email-btn {
    width: 100%;
    justify-content: center;
  }
}

/* Override any conflicting button styles for password/email change buttons */
.element-theme-provider .info-item .change-password-btn-inline,
.element-theme-provider .info-item .change-email-btn-inline,
.element-theme-provider .profile-info-card .change-password-btn-inline,
.element-theme-provider .profile-info-card .change-email-btn-inline,
.change-password-btn-inline,
.change-email-btn-inline {
  background-color: #ff6b35 !important;
  border-color: #ff6b35 !important;
  color: white !important;
  font-weight: 600 !important;
  border-radius: 6px !important;
  padding: 8px 16px !important;
  font-size: 14px !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 2px 4px rgba(255, 107, 53, 0.3) !important;
  margin-left: 10px !important;
  display: inline-block !important;
  visibility: visible !important;
  opacity: 1 !important;
}

.element-theme-provider .info-item .change-password-btn-inline:hover,
.element-theme-provider .info-item .change-email-btn-inline:hover,
.element-theme-provider .profile-info-card .change-password-btn-inline:hover,
.element-theme-provider .profile-info-card .change-email-btn-inline:hover,
.change-password-btn-inline:hover,
.change-email-btn-inline:hover {
  background-color: #e55a2b !important;
  border-color: #e55a2b !important;
  color: white !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 8px rgba(255, 107, 53, 0.4) !important;
}
</style>


