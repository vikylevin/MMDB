import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: 'dist',
    copyPublicDir: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'element-plus'],
          utils: ['axios', 'js-cookie']
        }
      }
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    historyApiFallback: true
  },
  preview: {
    host: '0.0.0.0',
    port: 4173,
    historyApiFallback: true
  }
})
