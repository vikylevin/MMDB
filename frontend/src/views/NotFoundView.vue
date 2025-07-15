<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const goHome = () => {
  router.push('/');
};
</script>

<template>
  <div class="not-found-view">
    <div class="not-found-content">
      <h1>404</h1>
      <h2>Page Not Found</h2>
      <p>Oops! The page you are looking for doesn't exist or has been moved.</p>
      <el-button type="primary" @click="goHome">Back to Home</el-button>
    </div>
  </div>
</template>

<style scoped>
.not-found-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
  text-align: center;
}

.not-found-content {
  max-width: 500px;
  padding: 2rem;
}

h1 {
  font-size: 6rem;
  margin: 0;
  color: var(--secondary-color);
  line-height: 1;
}

h2 {
  font-size: 2rem;
  margin: 0 0 1.5rem;
  color: var(--text-color);
}

p {
  margin-bottom: 2rem;
  font-size: 1.1rem;
  color: var(--text-color);
  opacity: 0.8;
}
</style>
