<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>{{ mode === 'login' ? 'Welcome Back' : 'Create Account' }}</h2>
        <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 14px;">
          {{ mode === 'login' ? 'Sign in to your account' : 'Join our movie community' }}
        </p>
      </template>
      
      <el-radio-group v-model="mode" size="large" class="mode-switcher">
        <el-radio-button label="login">Sign In</el-radio-button>
        <el-radio-button label="register">Sign Up</el-radio-button>
      </el-radio-group>

      <el-form v-if="mode === 'login'" :model="loginForm" @submit.prevent="handleLogin" label-position="top" size="large">
        <el-form-item label="Username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="Enter your username"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item label="Password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="Enter your password"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            @click="handleLogin"
            size="large"
          >
            {{ loading ? 'Signing In...' : 'Sign In' }}
          </el-button>
          <el-button 
            @click="$router.push('/')"
            size="large"
          >
            Back to Home
          </el-button>
        </el-form-item>
      </el-form>

      <el-form v-else :model="registerForm" @submit.prevent="handleRegister" label-position="top" size="large">
        <el-form-item label="Username">
          <el-input 
            v-model="registerForm.username" 
            placeholder="Choose a username"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item label="Email">
          <el-input 
            v-model="registerForm.email" 
            type="email" 
            placeholder="Enter your email address"
            :prefix-icon="Message"
          />
        </el-form-item>
        <el-form-item label="Password">
          <el-input 
            v-model="registerForm.password" 
            type="password" 
            placeholder="Create a password"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item label="Confirm Password">
          <el-input 
            v-model="confirmPassword" 
            type="password" 
            placeholder="Confirm your password"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            @click="handleRegister"
            size="large"
          >
            {{ loading ? 'Creating Account...' : 'Create Account' }}
          </el-button>
          <el-button 
            @click="$router.push('/')"
            size="large"
          >
            Back to Home
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { login, register } from '../services/api'

const router = useRouter()
const mode = ref('login')
const loading = ref(false)

const loginForm = ref({
  username: '',
  password: ''
})

const registerForm = ref({
  username: '',
  email: '',
  password: ''
})
const confirmPassword = ref('')

// Auto-clear localStorage after 1 hour
onMounted(() => {
  const loginTime = localStorage.getItem('login_time')
  if (loginTime) {
    const now = Date.now()
    const diff = now - parseInt(loginTime, 10)
    if (diff > 3600000) { // 1 hour in ms
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('login_time')
      ElMessage.info('Session expired, please login again')
      router.push('/login')
    }
  }
})

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('Please enter username and password')
    return
  }
  loading.value = true
  try {
    await login(loginForm.value.username, loginForm.value.password)
    localStorage.setItem('login_time', Date.now().toString())
    ElMessage.success('Login successful')
    router.push('/')
  } catch (error) {
    ElMessage.error('Login failed')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.email || !registerForm.value.password) {
    ElMessage.warning('Please fill in all fields')
    return
  }

  if (registerForm.value.password !== confirmPassword.value) {
    ElMessage.error('Passwords do not match')
    return
  }

  loading.value = true
  try {
    const response = await fetch('http://localhost:5000/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(registerForm.value)
    })

    if (response.ok) {
      ElMessage.success('Registration successful')
      mode.value = 'login'
      loginForm.value.username = registerForm.value.username
      loginForm.value.password = ''
      registerForm.value = {
        username: '',
        email: '',
        password: ''
      }
      confirmPassword.value = ''
      localStorage.setItem('login_time', Date.now().toString())
    } else {
      const data = await response.json()
      throw new Error(data.message || 'Registration failed')
    }
  } catch (error) {
    console.error('Registration error:', error)
    ElMessage.error(error.message || 'Registration failed')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 100%;
  max-width: 420px;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
}

.el-card__header {
  text-align: center;
  padding: 30px 20px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin: 0;
}

.el-card__header h2 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.el-card__body {
  padding: 30px;
}

/* Mode switcher styling */
.mode-switcher {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
  gap: 10px;
}

.el-radio-button {
  border-radius: 25px !important;
}

.el-radio-button__inner {
  border-radius: 25px !important;
  padding: 10px 25px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.el-radio-button__orig-radio:checked + .el-radio-button__inner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* Form styling */
.el-form {
  margin-top: 20px;
}

.el-form-item {
  margin-bottom: 25px;
}

.el-form-item__label {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

/* Input field styling */
:deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  border: 2px solid #e4e7ed;
  background-color: #fafafa;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #c0c4cc;
  background-color: #ffffff;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
  background-color: #ffffff;
}

:deep(.el-input__inner) {
  font-size: 16px;
  color: #2c3e50;
  border: none;
  padding: 0;
  background: transparent;
}

:deep(.el-input__inner::placeholder) {
  color: #a8abb2;
  font-weight: 400;
}

/* Input prefix icon styling */
:deep(.el-input__prefix) {
  color: #909399;
  font-size: 16px;
}

:deep(.el-input__wrapper.is-focus .el-input__prefix) {
  color: #667eea;
}

/* Button styling */
.el-form-item:last-child {
  margin-bottom: 0;
  text-align: center;
  margin-top: 35px;
}

.el-button {
  margin: 0 8px;
  border-radius: 12px;
  padding: 12px 30px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
  min-width: 120px;
}

.el-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.el-button--primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.el-button--default {
  background: white;
  border: 2px solid #e4e7ed;
  color: #606266;
}

.el-button--default:hover {
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Loading state */
.el-button.is-loading {
  transform: none;
}

/* Responsive design */
@media (max-width: 480px) {
  .login-container {
    padding: 15px;
  }
  
  .login-card {
    max-width: 100%;
  }
  
  .el-card__body {
    padding: 25px 20px;
  }
  
  .el-button {
    margin: 5px;
    min-width: 100px;
  }
}

/* Animation for card entrance */
.login-card {
  animation: slideInUp 0.6s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
