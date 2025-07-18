<template>
  <el-dialog
    :title="isLogin ? 'Login' : 'Register'"
    v-model="dialogVisible"
    width="400px"
    :close-on-click-modal="false"
  >
    <el-form
      :model="form"
      :rules="rules"
      ref="formRef"
      label-position="top"
    >
      <el-form-item
        label="Username"
        prop="username"
      >
        <el-input v-model="form.username" />
      </el-form-item>

      <el-form-item
        v-if="!isLogin"
        label="Email"
        prop="email"
      >
        <el-input v-model="form.email" type="email" />
      </el-form-item>

      <el-form-item
        label="Password"
        prop="password"
      >
        <el-input v-model="form.password" type="password" show-password />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="toggleMode">
          {{ isLogin ? 'Need an account? Register' : 'Already have an account? Login' }}
        </el-button>
        <el-button type="primary" @click="handleSubmit">
          {{ isLogin ? 'Login' : 'Register' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'auth-success'])
const dialogVisible = ref(false)
const isLogin = ref(true)
const formRef = ref(null)

const form = ref({
  username: '',
  email: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: 'Please input username', trigger: 'blur' },
    { min: 3, message: 'Length should be at least 3 characters', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Please input email', trigger: 'blur' },
    { type: 'email', message: 'Please input valid email', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please input password', trigger: 'blur' },
    { min: 6, message: 'Length should be at least 6 characters', trigger: 'blur' }
  ]
}

const toggleMode = () => {
  isLogin.value = !isLogin.value
  form.value = {
    username: '',
    email: '',
    password: ''
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    const endpoint = isLogin.value ? '/api/auth/login' : '/api/auth/register'

    if (!isLogin.value) {
      // Register first
      await axios.post('http://localhost:5000/api/auth/register', form.value)
    }

    // Login
    const response = await axios.post('http://localhost:5000/api/auth/login', {
      username: form.value.username,
      password: form.value.password
    })

    emit('auth-success', response.data.user)
    dialogVisible.value = false
    ElMessage.success(isLogin.value ? 'Login successful' : 'Registration successful')
  } catch (error) {
    console.error('Auth error:', error)
    ElMessage.error(error.response?.data?.error || 'Authentication failed')
  }
}

watch(
  () => props.modelValue,
  (newVal) => {
    dialogVisible.value = newVal
  }
)

watch(
  () => dialogVisible.value,
  (newVal) => {
    emit('update:modelValue', newVal)
  }
)
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.el-dialog__body) {
  padding-top: 10px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>
