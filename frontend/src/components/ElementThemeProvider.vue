<script setup>
// Simplified theme provider for Element Plus components
</script>

<template>
  <div class="element-theme-provider">
    <slot />
  </div>
</template>

<style>
/* Essential Element Plus component styling */
.element-theme-provider :deep(.el-button--primary) {
  background-color: #333333;
  border-color: #333333;
  color: white;
}

.element-theme-provider :deep(.el-button--primary:hover),
.element-theme-provider :deep(.el-button--primary:focus) {
  background-color: #666666;
  border-color: #666666;
}

.element-theme-provider :deep(.el-pagination .btn-next),
.element-theme-provider :deep(.el-pagination .btn-prev) {
  background-color: #333333;
  color: white;
  border: 1px solid #333333;
}

.element-theme-provider :deep(.el-pagination .btn-next:hover),
.element-theme-provider :deep(.el-pagination .btn-prev:hover) {
  background-color: #666666;
  border-color: #666666;
}

.element-theme-provider :deep(.el-pagination .is-active) {
  background-color: #333333;
  border-color: #333333;
  color: white;
}

.element-theme-provider :deep(.el-card) {
  background-color: #fafafa;
  border-color: #e0e0e0;
  color: #333333;
  transition: all 0.3s ease;
}

.element-theme-provider :deep(.el-card:hover) {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
</style>