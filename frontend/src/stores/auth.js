import { ref } from 'vue';

// Reactive authentication state
const isUserAuthenticated = ref(false);
const currentUser = ref(null);

// Initialize authentication state
export const initializeAuth = () => {
  const token = localStorage.getItem('access_token');
  const userStr = localStorage.getItem('user');
  
  isUserAuthenticated.value = !!token;
  currentUser.value = userStr ? JSON.parse(userStr) : null;
};

// Update authentication state
export const setAuthState = (authenticated, user = null) => {
  isUserAuthenticated.value = authenticated;
  currentUser.value = user;
};

// Get authentication state
export const getAuthState = () => ({
  isAuthenticated: isUserAuthenticated.value,
  user: currentUser.value
});

// Export reactive refs
export { isUserAuthenticated, currentUser };

// Initialize on module load
initializeAuth();
