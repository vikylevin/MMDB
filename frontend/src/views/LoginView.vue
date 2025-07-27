<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <el-radio-group v-model="mode" size="large">
          <el-radio-button label="login">Login</el-radio-button>
          <el-radio-button label="register">Register</el-radio-button>
        </el-radio-group>
      </template>

      <el-form v-if="mode === 'login'" :model="loginForm" @submit.prevent="handleLogin">
        <el-form-item label="Username">
          <el-input v-model="loginForm.username" placeholder="Please enter username" />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="loginForm.password" type="password" placeholder="Please enter password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleLogin">Login</el-button>
          <el-button @click="$router.push('/')">Back to Home</el-button>
        </el-form-item>
      </el-form>

      <el-form v-else :model="registerForm" @submit.prevent="handleRegister">
        <el-form-item label="Username">
          <el-input v-model="registerForm.username" placeholder="Please enter username" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="registerForm.email" type="email" placeholder="Please enter email" />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="registerForm.password" type="password" placeholder="Please enter password" />
        </el-form-item>
        <el-form-item label="Confirm">
          <el-input v-model="confirmPassword" type="password" placeholder="Please confirm password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleRegister">Register</el-button>
          <el-button @click="$router.push('/')">Back to Home</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

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

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('Please enter username and password')
    return
  }

  loading.value = true
  try {
    const response = await fetch('http://localhost:5000/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(loginForm.value)
    })

    if (response.ok) {
      const data = await response.json()
      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))
      ElMessage.success('Login successful')
      router.push('/')
    } else {
      throw new Error('Login failed')
    }
  } catch (error) {
    console.error('Login error:', error)
    ElMessage.error('Login failed. Please check your credentials')
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
  background-color: #f5f7fa;
}

.login-card {
  width: 100%;
  max-width: 400px;
}

.el-card__header {
  text-align: center;
  padding: 15px;
}

.el-form-item:last-child {
  margin-bottom: 0;
  text-align: center;
}

.el-button {
  margin: 0 10px;
}
</style>