# Movie Review Website

A movie review website built with Vue.js frontend and Flask backend, using TMDB API for movie data.

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the Flask application:
   ```
   python app.py
   ```
   The backend should be running at https://mmdb-f1b3.onrender.com (production) or http://localhost:5000 (development)

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the development server:
   ```
   npm run dev
   ```
   The frontend should be running at https://mmdb-web.onrender.com (production) or http://localhost:5173 (development)

## API Configuration

The application uses TMDB API for movie data. The API key is configured in the `.env` file in the backend directory.

## Database

The application uses PostgreSQL database hosted on Render for both production and development environments.

## Testing the Backend

After starting the Flask application, you can test if the backend is working correctly by:

1. Opening your browser and navigating to: https://mmdb-f1b3.onrender.com/api/movie/popular (production) or http://localhost:5000/api/movie/popular (development)
2. You should see a JSON response with popular movies data from TMDB.
3. Other available endpoints for testing:
   - Search for movies: https://mmdb-f1b3.onrender.com/api/movie/search?query=YOUR_SEARCH_TERM (production) or http://localhost:5000/api/movie/search?query=YOUR_SEARCH_TERM (development)
   - Get movie details: https://mmdb-f1b3.onrender.com/api/movie/MOVIE_ID (production) or http://localhost:5000/api/movie/MOVIE_ID (development) (e.g., 550 for Fight Club)