# Movie Review App - Render Deployment Guide

## Prerequisites
1. GitHub/GitLab repository with your code
2. Render account (https://render.com)
3. TMDB API key (https://www.themoviedb.org/settings/api)

## Deployment Steps

### Option 1: Using render.yaml (Recommended)
1. Push your code to GitHub/GitLab
2. Connect your repository to Render
3. Render will automatically detect the `render.yaml` file and create the services

### Option 2: Manual Setup

#### Backend Deployment
1. Create a new Web Service on Render
2. Connect your repository
3. Configure:
   - **Environment**: Python 3
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && python -c "from app import app, db; app.app_context().push(); db.create_all()" && gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Root Directory**: Leave empty (monorepo)

#### Database Setup
1. Create a PostgreSQL database on Render
2. Copy the database connection string

#### Frontend Deployment
1. Create a new Static Site on Render
2. Configure:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

#### Environment Variables
Set these in your backend service:
- `DATABASE_URL`: Your PostgreSQL connection string
- `SECRET_KEY`: A secure random string
- `TMDB_API_KEY`: Your TMDB API key
- `FLASK_ENV`: production
- `FRONTEND_URL`: Your frontend URL (for CORS)

Set these in your frontend service:
- `VITE_API_BASE_URL`: Your backend service URL

## Important Notes
1. Make sure your TMDB API key is valid
2. Database tables will be created automatically on first deployment
3. Frontend needs to know the backend URL via environment variable
4. CORS is configured to allow your frontend domain

## Local Development
1. Backend: `cd backend && python app.py`
2. Frontend: `cd frontend && npm run dev`
3. Make sure PostgreSQL is running locally
