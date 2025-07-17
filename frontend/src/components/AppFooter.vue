<script setup>
// Get current year for copyright
const currentYear = new Date().getFullYear();
</script>

<template>
  <footer class="app-footer">
    <div class="footer-container">
      <div class="footer-content">
        <div class="footer-section">
          <h3>About MMDb</h3>
          <p>Your go-to platform for discovering, reviewing, and discussing the latest movies from around the world.</p>
        </div>

        <div class="footer-section">
          <h3>Quick Links</h3>
          <ul>
            <li><router-link to="/">Home</router-link></li>
            <li><router-link to="/movies/popular">Popular Movies</router-link></li>
            <li><router-link to="/movies/top-rated">Top Rated</router-link></li>
            <li><router-link to="/privacy">Privacy Policy</router-link></li>
          </ul>
        </div>

        <div class="footer-section">
          <h3>Connect With Us</h3>
          <div class="social-links">
            <a href="#" aria-label="Facebook"><i class="el-icon-eleme"></i></a>
            <a href="#" aria-label="Twitter"><i class="el-icon-eleme"></i></a>
            <a href="#" aria-label="Instagram"><i class="el-icon-eleme"></i></a>
          </div>
        </div>
      </div>

      <div class="copyright">
        <p>&copy; {{ currentYear }} MMDb. All rights reserved.</p>
        <p>Powered by TMDB API</p>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background-color: var(--primary-color);
  color: #fff;
  padding: 2rem 0;
  margin-top: 2rem;
}

.footer-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1rem;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.footer-section h3 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: var(--secondary-color);
}

.footer-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-section li {
  margin-bottom: 0.5rem;
}

.footer-section a {
  color: #fff;
  text-decoration: none;
  transition: color 0.2s;
}

.footer-section a:hover {
  color: var(--secondary-color);
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-links a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  transition: background-color 0.2s;
}

.social-links a:hover {
  background-color: var(--secondary-color);
}

.copyright {
  text-align: center;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}
</style>
