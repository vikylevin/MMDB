<template>
  <div class="debug-container">
    <h2>Debug Information</h2>
    <div class="debug-section">
      <h3>Environment Variables</h3>
      <p><strong>MODE:</strong> {{ mode }}</p>
      <p><strong>VITE_API_BASE_URL:</strong> {{ apiBaseUrl }}</p>
      <p><strong>API URL being used:</strong> {{ actualApiUrl }}</p>
    </div>
    
    <div class="debug-section">
      <h3>Authentication</h3>
      <p><strong>Is Authenticated:</strong> {{ isAuth }}</p>
      <p><strong>Token exists:</strong> {{ hasToken }}</p>
      <p><strong>Token preview:</strong> {{ tokenPreview }}</p>
      <p><strong>User:</strong> {{ currentUser }}</p>
    </div>
    
    <div class="debug-section">
      <h3>API Test</h3>
      <el-button @click="testHealth" type="primary">Test Health Endpoint</el-button>
      <el-button @click="testAuth" type="success" :disabled="!isAuth">Test Auth Endpoint</el-button>
      <div v-if="testResult" class="test-result">
        <h4>Test Result:</h4>
        <pre>{{ testResult }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { isAuthenticated, getCurrentUser } from '../services/api'
import axios from 'axios'

const mode = ref(import.meta.env.MODE)
const apiBaseUrl = ref(import.meta.env.VITE_API_BASE_URL)
const actualApiUrl = ref('')
const isAuth = ref(false)
const hasToken = ref(false)
const tokenPreview = ref('')
const currentUser = ref(null)
const testResult = ref('')

// Get actual API URL from the axios instance
onMounted(() => {
  // Get the API URL that's actually being used
  const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'
  actualApiUrl.value = API_URL
  
  // Check authentication
  isAuth.value = isAuthenticated()
  const token = localStorage.getItem('access_token')
  hasToken.value = !!token
  if (token) {
    tokenPreview.value = token.substring(0, 20) + '...'
  }
  currentUser.value = getCurrentUser()
})

const testHealth = async () => {
  try {
    const response = await axios.get(`${actualApiUrl.value}/movie/health`)
    testResult.value = JSON.stringify(response.data, null, 2)
  } catch (error) {
    testResult.value = `Error: ${error.message}\n${JSON.stringify(error.response?.data, null, 2)}`
  }
}

const testAuth = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(`${actualApiUrl.value}/user/likes`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    testResult.value = JSON.stringify(response.data, null, 2)
  } catch (error) {
    testResult.value = `Error: ${error.message}\n${JSON.stringify(error.response?.data, null, 2)}`
  }
}
</script>

<style scoped>
.debug-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.debug-section {
  margin-bottom: 30px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.test-result {
  margin-top: 15px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 3px;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
