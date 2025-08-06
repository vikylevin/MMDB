<script setup>
import { 
  Star, 
  ChatDotRound, 
  VideoPlay,
  Position,
  TrendCharts,
  Calendar,
  StarFilled,
  Reading,
  DataAnalysis,
  QuestionFilled,
  Document,
  Service,
  Warning
} from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const currentYear = new Date().getFullYear();
</script>

<template>
  <footer class="app-footer">
    <div class="footer-container">
      <div class="footer-content">
        <!-- Brand Section -->
        <div class="footer-section brand-section">
          <div class="brand-header">
            <h3 class="brand-title">MMDb</h3>
            <el-icon class="brand-icon"><Star /></el-icon>
          </div>
          <p class="brand-description">
            The ultimate movie database and rating platform. 
            Discover, rate, and track your favorite films with our community.
          </p>
          <div class="social-links">
            <el-button circle size="small" class="social-btn" aria-label="Twitter">
              <el-icon><ChatDotRound /></el-icon>
            </el-button>
            <el-button circle size="small" class="social-btn" aria-label="Instagram">
              <el-icon><Position /></el-icon>
            </el-button>
            <el-button circle size="small" class="social-btn" aria-label="YouTube">
              <el-icon><VideoPlay /></el-icon>
            </el-button>
            <el-button circle size="small" class="social-btn" aria-label="GitHub">
              <el-icon><Document /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- Browse Movies Section -->
        <div class="footer-section">
          <h4 class="section-title">Browse Movies</h4>
          <nav class="footer-nav">
            <router-link to="/movies/popular" class="footer-link">
              <el-icon><TrendCharts /></el-icon>
              Popular Movies
            </router-link>
            <router-link to="/movies/top-rated" class="footer-link">
              <el-icon><Star /></el-icon>
              Top Rated
            </router-link>
            <router-link to="/movies/upcoming" class="footer-link">
              <el-icon><Calendar /></el-icon>
              Upcoming Releases
            </router-link>
            <router-link to="/movies/now-playing" class="footer-link">
              <el-icon><VideoPlay /></el-icon>
              Now Playing
            </router-link>
            <a href="#" class="footer-link">
              <el-icon><Reading /></el-icon>
              Genre Explorer
            </a>
          </nav>
        </div>

        <!-- Features Section -->
        <div class="footer-section">
          <h4 class="section-title">Features</h4>
          <nav class="footer-nav">
            <a href="#" class="footer-link">
              <el-icon><Star /></el-icon>
              Personal Ratings
            </a>
            <router-link to="/profile" class="footer-link">
              <el-icon><StarFilled /></el-icon>
              Watchlist
            </router-link>
            <a href="#" class="footer-link">
              <el-icon><ChatDotRound /></el-icon>
              Movie Reviews
            </a>
            <a href="#" class="footer-link">
              <el-icon><TrendCharts /></el-icon>
              Recommendations
            </a>
            <a href="#" class="footer-link">
              <el-icon><DataAnalysis /></el-icon>
              Statistics
            </a>
          </nav>
        </div>

        <!-- Support Section -->
        <div class="footer-section">
          <h4 class="section-title">Support</h4>
          <nav class="footer-nav">
            <a href="#" class="footer-link">
              <el-icon><QuestionFilled /></el-icon>
              Help Center
            </a>
            <a href="#" class="footer-link">
              <el-icon><Document /></el-icon>
              API Documentation
            </a>
            <a href="#" class="footer-link">
              <el-icon><Position /></el-icon>
              Contact Us
            </a>
            <a href="#" class="footer-link">
              <el-icon><Service /></el-icon>
              Community Guidelines
            </a>
            <a href="#" class="footer-link">
              <el-icon><Warning /></el-icon>
              Bug Report
            </a>
          </nav>
        </div>
      </div>

      <!-- Bottom Section -->
      <el-divider />
      
      <div class="footer-bottom">
        <div class="copyright-section">
          <p class="copyright-text">© {{ currentYear }} MMDb. All rights reserved.</p>
          <span class="separator">•</span>
          <p class="tagline">Powered by movie lovers, for movie lovers</p>
        </div>
        <div class="legal-links">
          <a href="#" class="legal-link">Privacy Policy</a>
          <a href="#" class="legal-link">Terms of Service</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background-color: var(--bg-color-soft, #f8f9fa);
  border-top: 1px solid var(--border-color, #e5e7eb);
  margin-top: auto;
}

.footer-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 3rem 2rem;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
}

.footer-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.brand-section {
  max-width: 300px;
}

.brand-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.brand-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color, #1f2937);
  margin: 0;
}

.brand-icon {
  color: #f59e0b;
  font-size: 1rem;
}

.brand-description {
  font-size: 0.875rem;
  color: var(--text-color-light, #6b7280);
  line-height: 1.5;
  margin-bottom: 1.5rem;
}

.social-links {
  display: flex;
  gap: 0.5rem;
}

.social-btn {
  width: 32px;
  height: 32px;
  background-color: transparent;
  border: 1px solid var(--border-color, #e5e7eb);
  color: var(--text-color-light, #6b7280);
  transition: all 0.2s ease;
}

.social-btn:hover {
  background-color: var(--secondary-color, #3b82f6);
  border-color: var(--secondary-color, #3b82f6);
  color: white;
  transform: translateY(-1px);
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color, #1f2937);
  margin: 0 0 1rem 0;
}

.footer-nav {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.footer-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-color-light, #6b7280);
  text-decoration: none;
  transition: color 0.2s ease;
  padding: 0.25rem 0;
}

.footer-link:hover {
  color: var(--secondary-color, #3b82f6);
}

.footer-link .el-icon {
  font-size: 0.875rem;
  opacity: 0.7;
}

.footer-bottom {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
  text-align: center;
}

@media (min-width: 640px) {
  .footer-bottom {
    flex-direction: row;
    justify-content: space-between;
    text-align: left;
  }
}

.copyright-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
}

@media (min-width: 640px) {
  .copyright-section {
    flex-direction: row;
    gap: 1rem;
  }
}

.copyright-text,
.tagline {
  font-size: 0.875rem;
  color: var(--text-color-light, #6b7280);
  margin: 0;
}

.separator {
  display: none;
  color: var(--text-color-light, #6b7280);
}

@media (min-width: 640px) {
  .separator {
    display: inline;
  }
  
  .tagline {
    display: block;
  }
}

@media (max-width: 639px) {
  .tagline {
    display: none;
  }
}

.legal-links {
  display: flex;
  gap: 1.5rem;
}

.legal-link {
  font-size: 0.875rem;
  color: var(--text-color-light, #6b7280);
  text-decoration: none;
  transition: color 0.2s ease;
}

.legal-link:hover {
  color: var(--secondary-color, #3b82f6);
}

/* Dark mode adjustments */
:deep(.el-divider) {
  border-color: var(--border-color, #e5e7eb);
  margin: 2rem 0;
}

/* Element Plus overrides */
:deep(.el-button) {
  border-radius: 50%;
}

:deep(.el-button:focus) {
  outline: none;
}
</style>
