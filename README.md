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
   The backend should be running at http://localhost:5000

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
   The frontend should be running at http://localhost:5173

## API Configuration

The application uses TMDB API for movie data. The API key is configured in the `.env` file in the backend directory.

## Database

The application uses SQLite database, which will be created automatically in the `backend/instance` directory when you run the application for the first time.

## Testing the Backend

After starting the Flask application, you can test if the backend is working correctly by:

1. Opening your browser and navigating to: http://localhost:5000/api/movies/popular
2. You should see a JSON response with popular movies data from TMDB.
3. Other available endpoints for testing:
   - Search for movies: http://localhost:5000/api/movies/search?query=YOUR_SEARCH_TERM
   - Get movie details: http://localhost:5000/api/movies/MOVIE_ID (e.g., 550 for Fight Club)