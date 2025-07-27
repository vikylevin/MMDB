import { ref } from 'vue';
import { defineStore } from 'pinia';
import * as api from '../services/api';
import { ElMessage } from 'element-plus';

export const useUserStore = defineStore('user', () => {
  const user = ref(api.getCurrentUser());
  const isAuthenticated = ref(api.isAuthenticated());

  async function login(username, password) {
    try {
      const userData = await api.login(username, password);
      user.value = userData;
      isAuthenticated.value = true;
      ElMessage.success('Successfully logged in');
      return true;
    } catch (error) {
      console.error('Login error:', error);
      ElMessage.error(error.response?.data?.error || 'Failed to login');
      return false;
    }
  }

  async function register(username, email, password) {
    try {
      const userData = await api.register(username, email, password);
      user.value = userData;
      isAuthenticated.value = true;
      ElMessage.success('Successfully registered');
      return true;
    } catch (error) {
      console.error('Registration error:', error);
      ElMessage.error(error.response?.data?.error || 'Failed to register');
      return false;
    }
  }

  function logout() {
    api.logout();
    user.value = null;
    isAuthenticated.value = false;
    ElMessage.success('Successfully logged out');
  }

  async function toggleWatchlist(movieId) {
    try {
      const response = await api.toggleWatchlist(movieId);
      ElMessage.success(response.message);
      return response.added;
    } catch (error) {
      console.error('Toggle watchlist error:', error);
      ElMessage.error('Failed to update watchlist');
      return false;
    }
  }

  async function rateMovie(movieId, rating) {
    try {
      const response = await api.rateMovie(movieId, rating);
      ElMessage.success('Rating saved successfully');
      return true;
    } catch (error) {
      console.error('Rate movie error:', error);
      ElMessage.error('Failed to save rating');
      return false;
    }
  }

  async function getWatchlist() {
    try {
      return await api.getWatchlist();
    } catch (error) {
      console.error('Get watchlist error:', error);
      ElMessage.error('Failed to load watchlist');
      return [];
    }
  }

  async function getProfile() {
    try {
      return await api.getProfile();
    } catch (error) {
      console.error('Get profile error:', error);
      ElMessage.error('Failed to load profile');
      return null;
    }
  }

  return {
    user,
    isAuthenticated,
    login,
    register,
    logout,
    toggleWatchlist,
    rateMovie,
    getWatchlist,
    getProfile
  };
});
