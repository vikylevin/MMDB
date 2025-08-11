<template>
  <div class="movie-filters">
    <el-card class="filter-card">
      <template #header>
        <div class="filter-header">
          <h3><i class="el-icon-filter"></i> Filters</h3>
          <el-button type="primary" size="small" @click="clearFilters">Clear All</el-button>
        </div>
      </template>
      
      <!-- Genre Filter -->
      <div class="filter-section">
        <h4><i class="el-icon-film"></i> Genres</h4>
        <div class="genre-tags">
          <template v-for="genreItem in genres" :key="genreItem.id">
            <el-tag
              v-if="genreItem && genreItem.id"
              :type="selectedGenres.includes(genreItem.id) ? 'primary' : 'info'"
              :effect="selectedGenres.includes(genreItem.id) ? 'dark' : 'plain'"
              class="genre-tag"
              @click="toggleGenre(genreItem.id)"
            >
              {{ genreItem.name }}
            </el-tag>
          </template>
          <!-- Loading state -->
          <div v-if="genres.length === 0" class="loading-text">
            Loading genres...
          </div>
        </div>
      </div>

      <!-- Rating Filter -->
      <div class="filter-section">
        <h4><i class="el-icon-star-on"></i> Rating Range</h4>
        <div class="rating-filter">
          <div class="rating-display">
            <span class="rating-value">{{ ratingRange[0] }}</span>
            <span class="rating-separator">-</span>
            <span class="rating-value">{{ ratingRange[1] }}</span>
          </div>
          <el-slider
            v-model="ratingRange"
            :min="0"
            :max="10"
            :step="0.5"
            range
            :marks="ratingMarks"
            @change="updateFilters"
          />
        </div>
      </div>

      <!-- Language Filter -->
      <div class="filter-section">
        <h4><i class="el-icon-globe"></i> Language</h4>
        <el-select
          v-model="selectedLanguage"
          placeholder="Search languages..."
          size="default"
          style="width: 100%"
          filterable
          clearable
          @change="updateFilters"
        >
          <el-option label="All Languages" value="" />
          <el-option
            v-for="language in allLanguages"
            :key="language.iso_639_1"
            :label="`${language.english_name}${language.name ? ` (${language.name})` : ''}`"
            :value="language.iso_639_1"
          />
        </el-select>
      </div>

      <!-- Apply Filters Button -->
      <div class="filter-section">
        <el-button 
          type="primary" 
          size="default" 
          style="width: 100%"
          @click="applyFilters"
          :disabled="!hasFilterChanges"
        >
          <i class="el-icon-search"></i>
          Apply Filters
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'https://mmdb-f1b3.onrender.com/api';

const emit = defineEmits(['filtersChanged']);

const genres = ref([]);
const allLanguages = ref([]);
const selectedGenres = ref([]);
const ratingRange = ref([0, 10]);
const selectedLanguage = ref('');

// Track applied filters vs current selections
const appliedFilters = ref({
  genres: null,
  ratingMin: 0,
  ratingMax: 10,
  language: null
});

const hasFilterChanges = computed(() => {
  const currentFilters = {
    genres: selectedGenres.value.length > 0 ? selectedGenres.value.join(',') : null,
    ratingMin: ratingRange.value[0],
    ratingMax: ratingRange.value[1],
    language: selectedLanguage.value || null
  };
  
  return JSON.stringify(currentFilters) !== JSON.stringify(appliedFilters.value);
});

// Rating marks for the slider
const ratingMarks = ref({
  0: '0',
  2.5: '2.5',
  5: '5',
  7.5: '7.5',
  10: '10'
});

const fetchGenres = async () => {
  try {
    const response = await axios.get(`${API_URL}/movie/genres`);
    if (response.data && response.data.genres) {
      genres.value = response.data.genres;
      // Check for any null or undefined IDs
      genres.value.forEach((genre, index) => {
        if (!genre || genre.id === null || genre.id === undefined) {
          console.warn(`Genre at index ${index} has invalid data:`, genre);
        }
      });
    }
  } catch (error) {
    console.error('Error fetching genres:', error);
  }
};

const fetchLanguages = async () => {
  try {
    const response = await axios.get(`${API_URL}/movie/languages`);
    if (response.data && Array.isArray(response.data)) {
      // Process languages and add Chinese alias
      const processedLanguages = response.data.map(lang => {
        if (lang.iso_639_1 === 'zh') {
          return { ...lang, english_name: 'Chinese (Mandarin)' };
        }
        if (lang.iso_639_1 === 'cn') {
          return { ...lang, english_name: 'Chinese (Cantonese)' };
        }
        return lang;
      });
      
      // Sort languages alphabetically by English name
      allLanguages.value = processedLanguages.sort((a, b) => 
        a.english_name.localeCompare(b.english_name)
      );
    }
  } catch (error) {
    console.error('Error fetching languages:', error);
    // Fallback to comprehensive language list if API fails
    allLanguages.value = [
      { iso_639_1: 'en', english_name: 'English', name: 'English' },
      { iso_639_1: 'zh', english_name: 'Chinese (Mandarin)', name: '普通话' },
      { iso_639_1: 'cn', english_name: 'Chinese (Cantonese)', name: '广州话' },
      { iso_639_1: 'es', english_name: 'Spanish', name: 'Español' },
      { iso_639_1: 'hi', english_name: 'Hindi', name: 'हिन्दी' },
      { iso_639_1: 'ar', english_name: 'Arabic', name: 'العربية' },
      { iso_639_1: 'pt', english_name: 'Portuguese', name: 'Português' },
      { iso_639_1: 'bn', english_name: 'Bengali', name: 'বাংলা' },
      { iso_639_1: 'ru', english_name: 'Russian', name: 'Русский' },
      { iso_639_1: 'ja', english_name: 'Japanese', name: '日本語' },
      { iso_639_1: 'jv', english_name: 'Javanese', name: '' },
      { iso_639_1: 'ko', english_name: 'Korean', name: '한국어' },
      { iso_639_1: 'fr', english_name: 'French', name: 'Français' },
      { iso_639_1: 'de', english_name: 'German', name: 'Deutsch' },
      { iso_639_1: 'tr', english_name: 'Turkish', name: 'Türkçe' },
      { iso_639_1: 'ur', english_name: 'Urdu', name: 'اردو' },
      { iso_639_1: 'it', english_name: 'Italian', name: 'Italiano' },
      { iso_639_1: 'vi', english_name: 'Vietnamese', name: 'Tiếng Việt' },
      { iso_639_1: 'pl', english_name: 'Polish', name: 'Polski' },
      { iso_639_1: 'uk', english_name: 'Ukrainian', name: 'Українська' },
      { iso_639_1: 'nl', english_name: 'Dutch', name: 'Nederlands' },
      { iso_639_1: 'th', english_name: 'Thai', name: 'ภาษาไทย' },
      { iso_639_1: 'sv', english_name: 'Swedish', name: 'svenska' },
      { iso_639_1: 'da', english_name: 'Danish', name: 'Dansk' },
      { iso_639_1: 'no', english_name: 'Norwegian', name: 'Norsk' },
      { iso_639_1: 'fi', english_name: 'Finnish', name: 'suomi' },
      { iso_639_1: 'he', english_name: 'Hebrew', name: 'עברית' },
      { iso_639_1: 'cs', english_name: 'Czech', name: 'Český' },
      { iso_639_1: 'hu', english_name: 'Hungarian', name: 'Magyar' },
      { iso_639_1: 'ro', english_name: 'Romanian', name: 'Română' },
      { iso_639_1: 'bg', english_name: 'Bulgarian', name: 'български език' },
      { iso_639_1: 'hr', english_name: 'Croatian', name: 'Hrvatski' },
      { iso_639_1: 'sr', english_name: 'Serbian', name: 'Srpski' },
      { iso_639_1: 'sk', english_name: 'Slovak', name: 'Slovenčina' },
      { iso_639_1: 'sl', english_name: 'Slovenian', name: 'Slovenščina' },
      { iso_639_1: 'et', english_name: 'Estonian', name: 'Eesti' },
      { iso_639_1: 'lv', english_name: 'Latvian', name: 'Latviešu' },
      { iso_639_1: 'lt', english_name: 'Lithuanian', name: 'Lietuvių' }
    ].sort((a, b) => a.english_name.localeCompare(b.english_name));
  }
};

const toggleGenre = (genreId) => {
  const index = selectedGenres.value.indexOf(genreId);
  if (index > -1) {
    selectedGenres.value.splice(index, 1);
  } else {
    selectedGenres.value.push(genreId);
  }
  // Don't auto-apply filters, just update selection
};

const updateFilters = () => {
  // This is called when individual filters change, but doesn't apply them
  // Just for internal state updates
};

const applyFilters = () => {
  const filters = {
    genres: selectedGenres.value.length > 0 ? selectedGenres.value.join(',') : null,
    ratingMin: ratingRange.value[0],
    ratingMax: ratingRange.value[1],
    language: selectedLanguage.value || null
  };
  
  appliedFilters.value = { ...filters };
  emit('filtersChanged', filters);
};

const handleFilterChange = () => {
  // Legacy function for backward compatibility
  applyFilters();
};

const clearFilters = () => {
  selectedGenres.value = [];
  ratingRange.value = [0, 10];
  selectedLanguage.value = '';
  applyFilters(); // Immediately apply the cleared state
};

onMounted(() => {
  fetchGenres();
  fetchLanguages();
});
</script>

<style scoped>
.movie-filters {
  margin-bottom: 20px;
}

.filter-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s ease;
}

.filter-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0;
}

.filter-header h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-section {
  margin-bottom: 24px;
}

.filter-section:last-child {
  margin-bottom: 0;
}

.filter-section h4 {
  margin: 0 0 12px 0;
  color: var(--text-color);
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Genre Tags Styling */
.genre-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.genre-tag {
  cursor: pointer;
  border-radius: 20px;
  padding: 6px 12px;
  font-size: 12px;
  transition: all 0.3s ease;
  border: 1px solid #dcdfe6;
  background: #ffffff;
  color: #606266;
}

.genre-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #909399;
}

.genre-tag.el-tag--primary {
  background: #303133;
  border-color: #303133;
  color: white;
}

/* Rating Filter Styling */
.rating-filter {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e4e7ed;
}

.rating-display {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: 600;
}

.rating-value {
  background: #606266;
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
  min-width: 40px;
  text-align: center;
}

.rating-separator {
  color: var(--text-color);
  font-size: 14px;
}

:deep(.el-slider__runway) {
  background-color: #e4e7ed;
  height: 6px;
  border-radius: 3px;
}

:deep(.el-slider__bar) {
  background: #606266;
  height: 6px;
  border-radius: 3px;
}

:deep(.el-slider__button) {
  width: 16px;
  height: 16px;
  border: 2px solid #606266;
  background: white;
  box-shadow: 0 2px 6px rgba(96, 98, 102, 0.3);
}

:deep(.el-slider__button:hover) {
  border-color: #303133;
  transform: scale(1.1);
}

:deep(.el-slider__marks-text) {
  font-size: 12px;
  color: #909399;
}

/* Select Styling */
:deep(.el-select) {
  width: 100%;
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  transition: all 0.3s ease;
}

:deep(.el-select .el-input__wrapper:hover) {
  border-color: #c0c4cc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

:deep(.el-select .el-input__wrapper.is-focus) {
  border-color: #606266;
  box-shadow: 0 0 0 2px rgba(96, 98, 102, 0.2);
}

:deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 12px 12px 0 0;
}

:deep(.el-card__body) {
  padding: 20px;
}

/* Button Styling */
:deep(.el-button--primary) {
  background: #606266;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  padding: 8px 16px;
}

:deep(.el-button--primary:hover) {
  background: #303133;
  transform: translateY(-1px);
  box-shadow: 0 3px 8px rgba(48, 49, 51, 0.3);
}

:deep(.el-button--primary:disabled) {
  background: #c0c4cc;
  border-color: #c0c4cc;
  transform: none;
  box-shadow: none;
}

/* Apply Filters Button */
.filter-section .el-button {
  font-size: 14px;
  padding: 12px 24px;
  font-weight: 600;
}

.filter-section .el-button i {
  margin-right: 6px;
}

.loading-text {
  color: #999;
  font-size: 12px;
  padding: 8px;
  text-align: center;
  font-style: italic;
}

/* Responsive Design */
@media (max-width: 768px) {
  .genre-tags {
    gap: 6px;
  }
  
  .genre-tag {
    font-size: 11px;
    padding: 4px 8px;
  }
  
  .rating-filter {
    padding: 12px;
  }
  
  :deep(.el-card__body) {
    padding: 16px;
  }
}
</style>
