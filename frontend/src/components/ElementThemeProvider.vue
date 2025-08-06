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

/* Ensure icons are visible in buttons with higher specificity */
.element-theme-provider :deep(.el-button .el-icon),
.element-theme-provider :deep(.el-button .el-icon svg) {
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

/* Active button states - white icons on colored backgrounds */
.element-theme-provider :deep(.el-button--success),
.element-theme-provider :deep(.el-button--success:hover),
.element-theme-provider :deep(.el-button--success:focus) {
  background-color: #67c23a !important;
  border-color: #67c23a !important;
  color: white !important;
}

.element-theme-provider :deep(.el-button--success .el-icon),
.element-theme-provider :deep(.el-button--success .el-icon svg),
.element-theme-provider :deep(.el-button--success:hover .el-icon),
.element-theme-provider :deep(.el-button--success:hover .el-icon svg) {
  color: white !important;
  fill: white !important;
}

.element-theme-provider :deep(.el-button--primary .el-icon),
.element-theme-provider :deep(.el-button--primary .el-icon svg),
.element-theme-provider :deep(.el-button--danger .el-icon),
.element-theme-provider :deep(.el-button--danger .el-icon svg) {
  color: white !important;
  fill: white !important;
}

/* Default button state - black icons on light background */
.element-theme-provider :deep(.el-button--default .el-icon),
.element-theme-provider :deep(.el-button--default .el-icon svg) {
  color: #000000 !important;
  fill: #000000 !important;
}

/* Hover states for default buttons */
.element-theme-provider :deep(.el-button--default:hover .el-icon),
.element-theme-provider :deep(.el-button--default:hover .el-icon svg) {
  color: white !important;
  fill: white !important;
}
</style>