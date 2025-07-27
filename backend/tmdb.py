import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

def fetch_movie_details(movie_id):
    """Get movie details from TMDB API"""
    try:
        response = requests.get(
            f'{TMDB_BASE_URL}/movie/{movie_id}',
            params={
                'api_key': TMDB_API_KEY,
                'language': 'en-US'
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching movie details: {e}")
        return None

def search_movies(query, page=1):
    """Search for movies"""
    try:
        response = requests.get(
            f'{TMDB_BASE_URL}/search/movie',
            params={
                'api_key': TMDB_API_KEY,
                'language': 'en-US',
                'query': query,
                'page': page,
                'include_adult': False
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error searching movies: {e}")
        return None

def get_popular_movies(page=1):
    """Get popular movies list"""
    try:
        response = requests.get(
            f'{TMDB_BASE_URL}/movie/popular',
            params={
                'api_key': TMDB_API_KEY,
                'language': 'en-US',
                'page': page
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching popular movies: {e}")
        return None
