<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Star, StarFilled, Clock, Calendar, MessageBox, Edit, Delete, ChatDotRound, Check } from '@element-plus/icons-vue';
import { isAuthenticated, getCurrentUser, rateMovie, getMovieRating, toggleWatchLater, toggleWatched, toggleLike,
         submitReview, getMovieReviews, toggleReviewLike, addReviewComment, getReviewComments, updateReview, deleteReview } from '../services/api';
import { isMovieInWatchLater, updateMovieStatus, isMovieWatched, isMovieLiked } from '../stores/movieStatus';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'https://mmdb-f1b3.onrender.com/api';
console.log('MovieDetailView API URL being used:', API_URL);

const route = useRoute();
const router = useRouter();
const movieId = computed(() => route.params.id);

const movie = ref(null);
const reviews = ref([]);
const loading = ref(true);
const error = ref(null);
const userReview = ref({
  rating: 0,
  comment: ''
});
const reviewSubmitting = ref(false);
const showReviewForm = ref(false);
const userRating = ref(0);
const currentUser = ref(null);

// Review editing state
const editingReviewId = ref(null);
const editReviewData = ref({
  rating: 0,
  comment: ''
});

// Review interaction state
const reviewComments = ref({});
const showCommentForms = ref({});
const commentTexts = ref({});

// Use global state for watch later status
const isInWatchLater = computed(() => {
  return isMovieInWatchLater(Number(movieId.value));
});

// Backward compatibility alias
const isInWatchlist = isInWatchLater;

// Use global state for like status
const isLiked = computed(() => {
  return isMovieLiked(Number(movieId.value));
});

const imageBaseUrl = 'https://image.tmdb.org/t/p/original';
const posterBaseUrl = 'https://image.tmdb.org/t/p/w500';

// Check if user is authenticated
const checkAuthentication = () => {
  if (isAuthenticated()) {
    currentUser.value = getCurrentUser();
  }
};

// Load user's rating for this movie
const loadUserRating = async () => {
  if (!isAuthenticated()) return;
  
  try {
    const response = await getMovieRating(movieId.value);
    userRating.value = response.rating || 0;
  } catch (error) {
    console.error('Error loading user rating:', error);
  }
};

// Handle rating change
const handleRating = async (rating) => {
  if (!isAuthenticated()) {
    ElMessage.warning('Please log in to rate movies');
    router.push('/login');
    return;
  }

  try {
    console.log('Submitting rating:', rating, 'for movie:', movieId.value);
    await rateMovie(movieId.value, rating);
    userRating.value = rating;
    
    // Auto-mark as watched when rating a movie (rating > 0)
    if (rating > 0) {
      // Since backend automatically adds to watched when rating, 
      // we need to update the frontend state to reflect this
      const movieIdNum = Number(movieId.value);
      updateMovieStatus(movieIdNum, 'watched', true);
    }
    
    ElMessage.success('Rating saved successfully');
  } catch (error) {
    console.error('Error saving rating:', error);
    let errorMessage = 'Failed to save rating';
    
    if (error.response) {
      if (error.response.status === 401) {
        errorMessage = 'Please log in again to rate movies';
        // Clear invalid token
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        router.push('/login');
      } else if (error.response.data?.error) {
        errorMessage = `Failed to save rating: ${error.response.data.error}`;
      }
    } else if (error.request) {
      errorMessage = 'Network error - please check your connection';
    }
    
    ElMessage.error(errorMessage);
    // Reset rating to previous value
    await loadUserRating();
  }
};

const checkWatchlistStatus = async () => {
  // No longer needed as we use global state
};

const toggleWatchLaterHandler = async () => {
  if (!isAuthenticated()) {
    ElMessage.warning('Please log in to add movies to your watch later list');
    return;
  }

  try {
    const response = await toggleWatchLater(movieId.value);
    // Update global state
    updateMovieStatus(Number(movieId.value), 'watchLater', response.added);
    ElMessage.success(`Movie ${response.added ? 'added to' : 'removed from'} watch later`);
  } catch (err) {
    console.error('Error updating watch later:', err);
    ElMessage.error('Failed to update watch later. Please try again later.');
  }
};

// Backward compatibility alias
const toggleWatchlistHandler = toggleWatchLaterHandler;

const toggleLikeHandler = async () => {
  if (!isAuthenticated()) {
    ElMessage.warning('Please log in to like movies');
    router.push('/login');
    return;
  }

  try {
    console.log('Toggling like for movie:', movieId.value);
    const response = await toggleLike(movieId.value);
    // Update global state
    updateMovieStatus(Number(movieId.value), 'likes', response.added);
    ElMessage.success(`Movie ${response.added ? 'liked' : 'unliked'}`);
  } catch (err) {
    console.error('Error updating like status:', err);
    let errorMessage = 'Failed to update like status. Please try again later.';
    
    if (err.response) {
      if (err.response.status === 401) {
        errorMessage = 'Please log in again to like movies';
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        router.push('/login');
      } else if (err.response.data?.error) {
        errorMessage = `Failed to update like status: ${err.response.data.error}`;
      }
    } else if (err.request) {
      errorMessage = 'Network error - please check your connection';
    }
    
    ElMessage.error(errorMessage);
  }
};

const fetchMovieDetails = async () => {
  try {
    loading.value = true;
    error.value = null;

    const [movieRes, reviewsData] = await Promise.all([
      axios.get(`${API_URL}/movie/${movieId.value}`),
      getMovieReviews(movieId.value)
    ]);

    movie.value = movieRes.data;
    reviews.value = reviewsData || [];
    // No longer need to check watchlist status as we use global state
  } catch (err) {
    console.error('Error fetching movie details:', err);
    error.value = 'Failed to load movie details. Please try again later.';
  } finally {
    loading.value = false;
  }
};

// Utility functions
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const formatRuntime = (minutes) => {
  if (!minutes) return 'N/A';
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
};

const formatReleaseDate = (dateString) => {
  if (!dateString) return 'N/A';
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

const submitUserReview = async () => {
  if (!isAuthenticated()) {
    ElMessage.warning('Please log in to write a review');
    router.push('/login');
    return;
  }

  if (userReview.value.rating === 0) {
    ElMessage.warning('Please select a rating');
    return;
  }

  reviewSubmitting.value = true;
  try {
    console.log('Submitting review for movie:', movieId.value, userReview.value);
    await submitReview(movieId.value, {
      rating: userReview.value.rating,
      comment: userReview.value.comment.trim()
    });
    
    userRating.value = userReview.value.rating;
    
    const movieIdNum = Number(movieId.value);
    updateMovieStatus(movieIdNum, 'watched', true);
    
    ElMessage.success('Review submitted successfully');
    showReviewForm.value = false;
    userReview.value = { rating: 0, comment: '' };
    await fetchMovieDetails();
  } catch (err) {
    console.error('Error submitting review:', err);
    let errorMessage = 'Failed to submit review';
    
    if (err.response) {
      if (err.response.status === 401) {
        errorMessage = 'Please log in again to submit reviews';
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        router.push('/login');
      } else if (err.response.data?.error) {
        errorMessage = `Failed to submit review: ${err.response.data.error}`;
      }
    } else if (err.request) {
      errorMessage = 'Network error - please check your connection';
    }
    
    ElMessage.error(errorMessage);
  } finally {
    reviewSubmitting.value = false;
  }
};

const showReviewFormHandler = () => {
  if (!isAuthenticated()) {
    ElMessage.warning('Please log in to write a review');
    router.push('/login');
    return;
  }
  showReviewForm.value = true;
};

// Review interaction functions
const toggleReviewLikeHandler = async (reviewId) => {
  if (!isAuthenticated()) {
    ElMessage.warning('Please log in to like reviews');
    return;
  }
  
  try {
    const result = await toggleReviewLike(reviewId);
    const reviewIndex = reviews.value.findIndex(r => r.id === reviewId);
    if (reviewIndex !== -1) {
      reviews.value[reviewIndex].user_has_liked = result.liked;
      reviews.value[reviewIndex].like_count = result.like_count;
    }
    ElMessage.success(result.liked ? 'Review liked' : 'Review unliked');
  } catch (error) {
    console.error('Error toggling review like:', error);
    ElMessage.error('Failed to update like status');
  }
};

const toggleCommentForm = async (reviewId) => {
  if (!isAuthenticated()) {
    ElMessage.warning('Please log in to comment');
    return;
  }
  
  showCommentForms.value[reviewId] = !showCommentForms.value[reviewId];
  
  // Load comments when expanding
  if (showCommentForms.value[reviewId] && !reviewComments.value[reviewId]) {
    try {
      const comments = await getReviewComments(reviewId);
      reviewComments.value[reviewId] = comments;
    } catch (error) {
      console.error('Error loading comments:', error);
      reviewComments.value[reviewId] = [];
    }
  }
};

const submitComment = async (reviewId) => {
  const commentText = commentTexts.value[reviewId];
  if (!commentText || !commentText.trim()) {
    ElMessage.warning('Please enter a comment');
    return;
  }

  try {
    const newComment = await addReviewComment(reviewId, commentText.trim());

    if (!reviewComments.value[reviewId]) {
      reviewComments.value[reviewId] = [];
    }
    reviewComments.value[reviewId].push(newComment);

    const reviewIndex = reviews.value.findIndex(r => r.id === reviewId);
    if (reviewIndex !== -1) {
      reviews.value[reviewIndex].comment_count = (reviews.value[reviewIndex].comment_count || 0) + 1;
    }

    commentTexts.value[reviewId] = '';
    ElMessage.success('Comment added successfully');
  } catch (error) {
    console.error('Error submitting comment:', error);
    ElMessage.error('Failed to submit comment');
  }
};

// Review management functions
const editReview = (review) => {
  editingReviewId.value = review.id;
  editReviewData.value = {
    rating: review.rating,
    comment: review.comment || ''
  };
};

const saveEditReview = async (reviewId) => {
  if (editReviewData.value.rating === 0) {
    ElMessage.warning('Please select a rating');
    return;
  }

  try {
    const updatedReview = await updateReview(reviewId, {
      rating: editReviewData.value.rating,
      comment: editReviewData.value.comment.trim()
    });

    const reviewIndex = reviews.value.findIndex(r => r.id === reviewId);
    if (reviewIndex !== -1) {
      reviews.value[reviewIndex] = { ...reviews.value[reviewIndex], ...updatedReview };
    }

    editingReviewId.value = null;
    editReviewData.value = { rating: 0, comment: '' };
    
    ElMessage.success('Review updated successfully');
  } catch (error) {
    console.error('Error updating review:', error);
    ElMessage.error('Failed to update review');
  }
};

const cancelEditReview = () => {
  editingReviewId.value = null;
  editReviewData.value = { rating: 0, comment: '' };
};

const confirmDeleteReview = async (reviewId) => {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to delete this review? This action cannot be undone.',
      'Delete Review',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    );
    
    await deleteReview(reviewId);
    
    reviews.value = reviews.value.filter(r => r.id !== reviewId);
    
    ElMessage.success('Review deleted successfully');
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Error deleting review:', error);
      ElMessage.error('Failed to delete review');
    }
  }
};

// Check if user came from profile page to edit a review
const checkEditReviewIntent = async () => {
  const editIntent = sessionStorage.getItem('editReviewIntent');
  if (editIntent === 'true' && isAuthenticated()) {
    // Clear the intent flag
    sessionStorage.removeItem('editReviewIntent');
    
    // Wait a bit for reviews to load
    setTimeout(() => {
      const currentUserName = getCurrentUser()?.username;
      if (currentUserName && reviews.value.length > 0) {
        // Find user's review
        const userReviewObj = reviews.value.find(review => review.author === currentUserName);
        if (userReviewObj) {
          // Automatically start editing the user's review
          editReview(userReviewObj);
          
          // Scroll to reviews section
          const reviewsSection = document.querySelector('.reviews-section');
          if (reviewsSection) {
            reviewsSection.scrollIntoView({ behavior: 'smooth' });
          }
          
          ElMessage.info('Edit mode activated for your review');
        }
      }
    }, 1000); // Wait 1 second for data to load
  }
};

onMounted(() => {
  checkAuthentication();
  fetchMovieDetails();
  loadUserRating();
  checkEditReviewIntent();
});
</script>

<template>
  <div class="movie-detail-view">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <el-skeleton style="width: 100%" animated>
        <template #template>
          <div style="display: flex; gap: 20px;">
            <el-skeleton-item variant="image" style="width: 300px; height: 450px" />
            <div style="flex: 1;">
              <el-skeleton-item variant="h1" style="width: 50%" />
              <el-skeleton-item variant="text" style="margin-top: 16px; width: 80%" />
              <el-skeleton-item variant="text" style="width: 60%" />
            </div>
          </div>
        </template>
      </el-skeleton>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      <el-alert :title="error" type="error" show-icon />
    </div>

    <!-- Movie Details -->
    <div v-if="!loading && !error && movie" class="movie-content">
      <!-- Backdrop -->
      <div class="movie-backdrop" :style="{
        backgroundImage: movie.backdrop_path ? 
          `linear-gradient(to bottom, rgba(0,0,0,0.7), rgba(0,0,0,0.9)), url(${imageBaseUrl}${movie.backdrop_path})` : 
          'none'
      }">
        <div class="movie-detail-container">
          <!-- Poster and Basic Info -->
          <div class="movie-detail-header">
            <div class="movie-poster">
              <img 
                :src="movie.poster_path ? `${posterBaseUrl}${movie.poster_path}` : '/placeholder-poster.jpg'" 
                :alt="movie.title" 
              />
            </div>

            <div class="movie-info">
              <h1>{{ movie.title }} <span v-if="movie.release_date">({{ new Date(movie.release_date).getFullYear() }})</span></h1>

              <div class="movie-meta">
                <div class="rating">
                  <el-icon><StarFilled /></el-icon>
                  <span>{{ (Math.round(movie.vote_average * 10) / 10).toFixed(1) }}</span>
                  <span class="vote-count">({{ movie.vote_count }} votes)</span>
                </div>

                <div class="meta-item" v-if="movie.runtime">
                  <el-icon><Clock /></el-icon>
                  <span>{{ formatRuntime(movie.runtime) }}</span>
                </div>

                <div class="meta-item" v-if="movie.release_date">
                  <el-icon><Calendar /></el-icon>
                  <span>{{ formatReleaseDate(movie.release_date) }}</span>
                </div>
              </div>

              <div class="genres" v-if="movie.genres && movie.genres.length">
                <span v-for="genre in movie.genres" :key="genre.id" class="genre-tag">
                  {{ genre.name }}
                </span>
              </div>

              <div class="tagline" v-if="movie.tagline">
                <em>{{ movie.tagline }}</em>
              </div>

              <div class="overview">
                <h3>Overview</h3>
                <p>{{ movie.overview }}</p>
              </div>

              <div class="actions">
                <!-- User Rating Section -->
                <div class="user-rating-section">
                  <h4>Rate this movie:</h4>
                  <el-rate 
                    v-model="userRating" 
                    :max="5" 
                    @change="handleRating"
                    text-color="var(--rating-color)"
                    void-color="var(--border-color)"
                    :disabled="!isAuthenticated()"
                  />
                  <span v-if="!isAuthenticated()" class="login-hint">
                    <router-link to="/login">Login to rate</router-link>
                  </span>
                </div>

                <div class="action-buttons-container">
                  <div class="action-buttons">
                    <el-tooltip content="Write a Review" placement="top">
                      <el-button @click="showReviewFormHandler" class="review-btn highlighted-btn icon-only-btn">
                        <el-icon><ChatDotRound /></el-icon>
                      </el-button>
                    </el-tooltip>
                    <el-tooltip :content="isLiked ? 'Remove from Likes' : 'Add to Likes'" placement="top">
                      <el-button @click="toggleLikeHandler" class="like-btn highlighted-btn icon-only-btn" :class="{ 'liked': isLiked }">
                        <el-icon>
                          <StarFilled v-if="isLiked" />
                          <Star v-else />
                        </el-icon>
                      </el-button>
                    </el-tooltip>
                    <el-tooltip :content="isInWatchLater ? 'Remove from Watch Later' : 'Add to Watch Later'" placement="top">
                      <el-button @click="toggleWatchLaterHandler" class="watch-later-btn highlighted-btn icon-only-btn" :class="{ 'added': isInWatchLater }">
                        <el-icon>
                          <Check v-if="isInWatchLater" />
                          <Clock v-else />
                        </el-icon>
                      </el-button>
                    </el-tooltip>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Details -->
      <div class="movie-detail-container">
        <!-- Cast & Crew Section would go here -->

        <!-- Reviews Section -->
        <section class="reviews-section">
          <div class="section-header">
            <h2>Reviews</h2>
            <span v-if="reviews.length" class="review-count">{{ reviews.length }} reviews</span>
          </div>

          <!-- Review Form -->
          <div v-if="showReviewForm" class="review-form">
            <h3>Write a Review</h3>
            <el-form>
              <el-form-item label="Rating">
                <el-rate 
                  v-model="userReview.rating" 
                  :max="5" 
                  text-color="var(--rating-color)"
                  void-color="var(--border-color)"
                  :size="24"
                />
              </el-form-item>

              <el-form-item label="Your Review (Optional)">
                <el-input 
                  v-model="userReview.comment" 
                  type="textarea" 
                  :rows="4" 
                  placeholder="Share your thoughts about the movie (optional)"
                />
              </el-form-item>

              <el-form-item>
                <div class="review-form-actions">
                  <el-button @click="submitUserReview" :loading="reviewSubmitting" type="primary" class="submit-btn">
                    Submit Review
                  </el-button>
                  <el-button @click="showReviewForm = false" class="cancel-btn">Cancel</el-button>
                </div>
              </el-form-item>
            </el-form>
          </div>

          <!-- Reviews List -->
          <div v-if="reviews.length" class="reviews-list">
            <div v-for="(review, index) in reviews" :key="review.id || index" class="review-card">
              <div class="review-header">
                <div class="review-author-section">
                  <h4>{{ review.author }}</h4>
                  <div class="review-rating" v-if="review.rating">
                    <el-rate 
                      :model-value="review.rating" 
                      :max="5" 
                      disabled 
                      text-color="#ffce54"
                      void-color="#e0e0e0"
                      :size="18"
                    />
                  </div>
                </div>
                
                <!-- Edit/Delete buttons for own reviews -->
                <div v-if="currentUser && currentUser.username === review.author" class="review-management">
                  <el-button size="small" @click="editReview(review)" type="primary" link>
                    <el-icon><Edit /></el-icon>
                    Edit
                  </el-button>
                  <el-button size="small" @click="confirmDeleteReview(review.id)" type="danger" link>
                    <el-icon><Delete /></el-icon>
                    Delete
                  </el-button>
                </div>
              </div>

              <div class="review-date" v-if="review.created_at">
                {{ new Date(review.created_at).toLocaleDateString() }}
                <span v-if="review.updated_at && review.updated_at !== review.created_at" class="updated-tag">
                  (Updated: {{ new Date(review.updated_at).toLocaleDateString() }})
                </span>
              </div>

              <!-- Regular review content -->
              <div v-if="editingReviewId !== review.id" class="review-content">
                <p v-if="review.comment">{{ review.comment }}</p>
                <p v-else-if="review.content">{{ review.content }}</p>
              </div>

              <!-- Edit review form -->
              <div v-else class="edit-review-form">
                <el-form>
                  <el-form-item label="Rating">
                    <el-rate 
                      v-model="editReviewData.rating" 
                      :max="5" 
                      text-color="var(--rating-color)"
                      void-color="var(--border-color)"
                      :size="20"
                    />
                  </el-form-item>

                  <el-form-item label="Review">
                    <el-input 
                      v-model="editReviewData.comment" 
                      type="textarea" 
                      :rows="3" 
                      placeholder="Update your review..."
                    />
                  </el-form-item>

                  <el-form-item>
                    <div class="edit-review-actions">
                      <el-button @click="saveEditReview(review.id)" type="primary" size="small" class="save-btn">
                        Save Changes
                      </el-button>
                      <el-button @click="cancelEditReview" size="small" class="cancel-btn">
                        Cancel
                      </el-button>
                    </div>
                  </el-form-item>
                </el-form>
              </div>

              <!-- Review Actions -->
              <div v-if="editingReviewId !== review.id" class="review-actions">
                <el-button 
                  :type="review.user_has_liked ? 'primary' : 'default'"
                  size="small"
                  @click="toggleReviewLikeHandler(review.id)"
                  class="review-action-btn like-btn"
                >
                  <span class="heart-icon">♥</span>
                  <span>{{ review.like_count || 0 }}</span>
                </el-button>

                <el-button 
                  size="small"
                  @click="toggleCommentForm(review.id)"
                  class="review-action-btn comment-btn"
                >
                  <el-icon><ChatDotRound /></el-icon>
                  <span>{{ review.comment_count || 0 }}</span>
                </el-button>
              </div>

              <!-- Comments Section -->
              <div v-if="showCommentForms[review.id]" class="comments-section">
                <!-- Existing Comments -->
                <div v-if="reviewComments[review.id] && reviewComments[review.id].length > 0" class="existing-comments">
                  <div v-for="comment in reviewComments[review.id]" :key="comment.id" class="comment-item">
                    <div class="comment-header">
                      <span class="comment-author">{{ comment.username }}</span>
                      <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                    </div>
                    <div class="comment-content">{{ comment.comment }}</div>
                  </div>
                </div>

                <!-- Add Comment Form -->
                <div class="add-comment-form">
                  <el-input
                    v-model="commentTexts[review.id]"
                    type="textarea"
                    :rows="2"
                    placeholder="Write a comment..."
                    class="comment-input"
                  />
                  <div class="comment-actions">
                    <el-button size="small" @click="submitComment(review.id)" type="primary">
                      Post Comment
                    </el-button>
                    <el-button size="small" @click="showCommentForms[review.id] = false">
                      Cancel
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="no-reviews">
            <p>No reviews yet. Be the first to review this movie!</p>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.movie-detail-view {
  color: var(--text-color);
}

.loading-state, .error-message {
  padding: 2rem;
}

.movie-backdrop {
  background-size: cover;
  background-position: center top;
  padding: 3rem 0;
  color: white;
}

.movie-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.movie-detail-header {
  display: flex;
  gap: 2rem;
}

.movie-poster {
  flex-shrink: 0;
  width: 300px;
}

.movie-poster img {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
}

.movie-info {
  flex: 1;
  position: relative;
}

.movie-info h1 {
  margin: 0 0 1rem;
  font-size: 2.5rem;
  font-weight: 700;
}

.movie-meta {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.rating, .meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rating .el-icon {
  color: #ffce54;
}

.vote-count {
  opacity: 0.8;
  font-size: 0.9rem;
}

.genres {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.genre-tag {
  background-color: rgba(255, 255, 255, 0.1);
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

.tagline {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  opacity: 0.8;
}

.overview h3 {
  margin: 0 0 0.5rem;
}

.overview p {
  line-height: 1.6;
  font-size: 1.1rem;
}

.actions {
  margin-top: 2rem;
}

.user-rating-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.user-rating-section h4 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-size: 1rem;
}

.login-hint {
  margin-left: 1rem;
  font-size: 0.9rem;
  color: var(--light-text);
}

.login-hint a {
  color: var(--rating-color);
  text-decoration: none;
}

.login-hint a:hover {
  text-decoration: underline;
}

.action-buttons-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.review-btn, .watch-later-btn {
  background: var(--card-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
  opacity: 0.8;
}

.review-btn:hover, .watch-later-btn:hover {
  background: var(--hover-color);
  border-color: var(--text-color);
  opacity: 1;
}

/* Highlighted buttons for movie info section */
.highlighted-btn {
  background: #2c3e50 !important;
  color: white !important;
  border: 2px solid #34495e !important;
  font-weight: 600 !important;
  padding: 12px 24px !important;
  border-radius: 8px !important;
  opacity: 1 !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.highlighted-btn:hover {
  background: #34495e !important;
  border-color: #2c3e50 !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* Icon-only button styling */
.icon-only-btn {
  width: 48px !important;
  height: 48px !important;
  padding: 0 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  border-radius: 50% !important;
}

.icon-only-btn .el-icon {
  font-size: 24px !important;
}

/* Specific button colors */
.review-btn.icon-only-btn {
  background: white !important;
  border-color: #e9ecef !important;
  color: #333333 !important;
}

.review-btn.icon-only-btn:hover {
  background: #f8f9fa !important;
  border-color: #333333 !important;
  color: #333333 !important;
}

.like-btn.icon-only-btn {
  background: white !important;
  border-color: #e9ecef !important;
  color: #333333 !important;
}

.like-btn.icon-only-btn:hover {
  background: #f8f9fa !important;
  border-color: #333333 !important;
  color: #333333 !important;
}

.like-btn.icon-only-btn.liked {
  background: #f39c12 !important;
  border-color: #e67e22 !important;
  color: white !important;
}

.like-btn.icon-only-btn.liked:hover {
  background: #e67e22 !important;
  border-color: #d35400 !important;
  color: white !important;
}

/* Backward compatibility */
.like-btn.icon-only-btn {
  background: white !important;
  border-color: #e9ecef !important;
  color: #333333 !important;
}

.like-btn.icon-only-btn:hover {
  background: #f8f9fa !important;
  border-color: #333333 !important;
  color: #333333 !important;
}

.like-btn.icon-only-btn.liked {
  background: #f39c12 !important;
  border-color: #e67e22 !important;
  color: white !important;
}

.like-btn.icon-only-btn.liked:hover {
  background: #e67e22 !important;
  border-color: #d35400 !important;
  color: white !important;
}

.watch-later-btn.icon-only-btn {
  background: #27ae60 !important;
  border-color: #229954 !important;
  color: white !important;
}

.watch-later-btn.icon-only-btn:hover {
  background: #229954 !important;
  border-color: #1e8449 !important;
  color: white !important;
}

.watch-later-btn.icon-only-btn.added {
  background: #28a745 !important;
  border-color: #1e7e34 !important;
  color: white !important;
}

.watch-later-btn.icon-only-btn.added:hover {
  background: #1e7e34 !important;
  border-color: #155724 !important;
  color: white !important;
}

/* Backward compatibility */
.watchlist-btn.icon-only-btn {
  background: #27ae60 !important;
  border-color: #229954 !important;
}

.watchlist-btn.icon-only-btn:hover {
  background: #229954 !important;
  border-color: #1e8449 !important;
}

/* Featured button for reviews section */
.featured-btn {
  background: #2c3e50 !important;
  color: white !important;
  border: 2px solid #34495e !important;
  font-weight: 600 !important;
  padding: 14px 28px !important;
  border-radius: 10px !important;
  font-size: 1.1rem !important;
  margin-top: 1rem !important;
  box-shadow: 0 4px 12px rgba(44, 62, 80, 0.3);
}

.featured-btn:hover {
  background: #34495e !important;
  border-color: #2c3e50 !important;
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(44, 62, 80, 0.4);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 3rem 0 1.5rem;
}

.review-count {
  opacity: 0.7;
}

.reviews-list {
  display: grid;
  gap: 1.5rem;
}

.review-card {
  background-color: var(--card-bg);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.review-header h4 {
  margin: 0;
  font-size: 1.1rem;
}

.review-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #ffce54;
}

.review-date {
  font-size: 0.9rem;
  opacity: 0.7;
  margin-bottom: 1rem;
}

.review-content p {
  margin: 0;
  line-height: 1.6;
}

/* Review management styles */
.review-author-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.review-management {
  display: flex;
  gap: 0.5rem;
}

.review-management .el-button {
  font-size: 0.8rem;
  padding: 0.25rem 0.5rem;
}

.updated-tag {
  font-size: 0.8rem;
  opacity: 0.6;
  font-style: italic;
}

.edit-review-form {
  margin: 1rem 0;
  padding: 1rem;
  background-color: var(--hover-color);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.edit-review-form .el-form-item {
  margin-bottom: 1rem;
}

.edit-review-form .el-rate {
  font-size: 20px;
}

.edit-review-form .el-button {
  margin-right: 0.5rem;
}

.action-buttons-container {
  margin-top: 2rem;
  display: flex;
  justify-content: flex-end;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.review-btn, .watch-later-btn, .like-btn {
  background: rgba(255, 255, 255, 0.95) !important;
  color: #333333 !important;
  border: 2px solid #e9ecef !important;
  font-weight: 600 !important;
  padding: 10px 20px !important;
  border-radius: 8px !important;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease !important;
  display: flex !important;
  align-items: center !important;
  gap: 0.5rem !important;
}

.review-btn:hover, .watch-later-btn:hover, .like-btn:hover {
  background: white !important;
  border-color: #333333 !important;
  color: #333333 !important;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.watch-later-btn.highlighted-btn {
  background: rgba(255, 255, 255, 0.95) !important;
  color: #333333 !important;
  border-color: #e9ecef !important;
}

.watch-later-btn.highlighted-btn:hover {
  background: white !important;
  border-color: #333333 !important;
  color: #333333 !important;
}

/* Backward compatibility */
.watchlist-btn.highlighted-btn {
  background: rgba(255, 255, 255, 0.95) !important;
  color: #333333 !important;
  border-color: #e9ecef !important;
}

.watchlist-btn.highlighted-btn:hover {
  background: white !important;
  border-color: #333333 !important;
  color: #333333 !important;
}

.like-btn.liked {
  background: rgba(255, 69, 90, 0.95) !important;
  color: white !important;
  border-color: #ff455a !important;
}

.like-btn.liked:hover {
  background: #ff455a !important;
  border-color: #ff455a !important;
  color: white !important;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 69, 90, 0.3);
}

/* Review interaction styles */
.review-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

/* Unified Review Action Button Styling */
.review-action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8f9fa !important;
  border: 1px solid #e9ecef !important;
  color: #6c757d !important;
  transition: all 0.3s ease !important;
  border-radius: 6px !important;
  font-weight: 500 !important;
  padding: 8px 12px !important;
}

.review-action-btn:hover {
  background: #e9ecef !important;
  border-color: #adb5bd !important;
  color: #495057 !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.review-action-btn.el-button--primary {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important;
  border-color: #e74c3c !important;
  color: white !important;
}

.review-action-btn.el-button--primary:hover {
  background: linear-gradient(135deg, #c0392b 0%, #a93226 100%) !important;
  border-color: #c0392b !important;
  transform: translateY(-1px) scale(1.05);
  box-shadow: 0 4px 8px rgba(231, 76, 60, 0.3);
}

.review-action-btn .heart-icon {
  transition: all 0.3s ease;
  font-size: 16px;
}

.review-action-btn.el-button--primary .heart-icon {
  animation: heartbeat 0.6s ease-in-out;
}

.review-action-btn .el-icon {
  font-size: 16px;
}

@keyframes heartbeat {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
}

.action-btn .el-icon {
  font-size: 16px;
}

.comments-section {
  margin-top: 1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 50%, #f8f9fa 100%);
  border: 1px solid #dee2e6;
  border-radius: 12px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.existing-comments {
  margin-bottom: 1rem;
}

.comment-item {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.comment-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.comment-item:last-child {
  margin-bottom: 0;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #f1f3f4;
}

.comment-author {
  font-weight: 600;
  color: #333333;
  font-size: 0.9rem;
}

.comment-date {
  font-size: 0.8rem;
  color: #6c757d;
}

.comment-content {
  color: #495057;
  line-height: 1.5;
  font-size: 0.9rem;
}

.add-comment-form {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
}

.comment-input {
  margin-bottom: 0.75rem;
}

.comment-actions {
  display: flex;
  gap: 0.75rem;
}

/* Edit Review Actions Styling */
.edit-review-actions {
  display: flex;
  gap: 0.75rem;
}

/* Review Form Actions Styling */
.review-form-actions {
  display: flex;
  gap: 0.75rem;
}

/* Unified button theme for comment, edit, and form actions */
.comment-actions .el-button--primary,
.edit-review-actions .save-btn,
.review-form-actions .submit-btn {
  background: #2c3e50 !important;
  border-color: #2c3e50 !important;
  color: white !important;
  font-weight: 600 !important;
  border-radius: 6px !important;
  padding: 8px 16px !important;
  transition: all 0.3s ease !important;
}

.comment-actions .el-button--primary:hover,
.edit-review-actions .save-btn:hover,
.review-form-actions .submit-btn:hover {
  background: #34495e !important;
  border-color: #34495e !important;
  color: white !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(44, 62, 80, 0.3);
}

.comment-actions .el-button:not(.el-button--primary),
.edit-review-actions .cancel-btn,
.review-form-actions .cancel-btn {
  background: #f8f9fa !important;
  border-color: #dee2e6 !important;
  color: #6c757d !important;
  font-weight: 500 !important;
  border-radius: 6px !important;
  padding: 8px 16px !important;
  transition: all 0.3s ease !important;
}

.comment-actions .el-button:not(.el-button--primary):hover,
.edit-review-actions .cancel-btn:hover,
.review-form-actions .cancel-btn:hover {
  background: #e9ecef !important;
  border-color: #adb5bd !important;
  color: #495057 !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.no-reviews {
  text-align: center;
  padding: 3rem 2rem;
  background-color: var(--card-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.no-reviews p {
  font-size: 1.1rem;
  color: var(--text-color);
  margin-bottom: 1.5rem;
  opacity: 0.8;
}

.review-form {
  background-color: var(--card-bg);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Larger stars in review form */
.review-form .el-rate {
  font-size: 28px;
}

.review-form .el-rate .el-icon {
  margin-right: 8px;
}

</style>
