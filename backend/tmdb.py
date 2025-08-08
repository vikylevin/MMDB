import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = os.getenv('TMDB_BASE_URL', 'https://api.themoviedb.org/3')

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

def get_popular_movies(page=1, with_genres=None, vote_average_gte=None, vote_average_lte=None, with_original_language=None):
    """Get popular movies list with filters"""
    try:
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'en-US',
            'page': page
        }
        
        # Add filters if provided
        if with_genres:
            params['with_genres'] = with_genres
        if vote_average_gte:
            params['vote_average.gte'] = vote_average_gte
        if vote_average_lte:
            params['vote_average.lte'] = vote_average_lte
        if with_original_language:
            params['with_original_language'] = with_original_language
            
        response = requests.get(
            f'{TMDB_BASE_URL}/discover/movie',
            params=params
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching popular movies: {e}")
        return None

def get_top_rated_movies(page=1, with_genres=None, vote_average_gte=None, vote_average_lte=None, with_original_language=None):
    """Get top rated movies list with filters"""
    try:
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'en-US',
            'page': page,
            'sort_by': 'vote_average.desc',
            'vote_count.gte': 1000  # Ensure minimum vote count for quality
        }
        
        # Add filters if provided
        if with_genres:
            params['with_genres'] = with_genres
        if vote_average_gte:
            params['vote_average.gte'] = vote_average_gte
        if vote_average_lte:
            params['vote_average.lte'] = vote_average_lte
        if with_original_language:
            params['with_original_language'] = with_original_language
            
        response = requests.get(
            f'{TMDB_BASE_URL}/discover/movie',
            params=params
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching top rated movies: {e}")
        return None

def get_upcoming_movies(page=1, with_genres=None, vote_average_gte=None, vote_average_lte=None, with_original_language=None, region=None):
    """Get upcoming movies list with filters and region-specific releases"""
    try:
        from datetime import datetime
        
        # Always use discover endpoint to ensure proper date filtering
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'en-US',
            'page': page,
            'primary_release_date.gte': datetime.now().strftime('%Y-%m-%d'),
            'sort_by': 'primary_release_date.asc'
        }
        
        # Add region parameter for region-specific releases
        if region:
            params['region'] = region
        
        # Add filters if provided
        if with_genres:
            params['with_genres'] = with_genres
        if vote_average_gte:
            params['vote_average.gte'] = vote_average_gte
        if vote_average_lte:
            params['vote_average.lte'] = vote_average_lte
        if with_original_language:
            params['with_original_language'] = with_original_language
            
        response = requests.get(
            f'{TMDB_BASE_URL}/discover/movie',
            params=params
        )
            
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching upcoming movies: {e}")
        return None

def get_movie_genres():
    """Get list of movie genres from TMDB"""
    try:
        response = requests.get(
            f'{TMDB_BASE_URL}/genre/movie/list',
            params={
                'api_key': TMDB_API_KEY,
                'language': 'en-US'
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching movie genres: {e}")
        return None

def get_available_languages():
    """Get list of available languages from TMDB"""
    try:
        response = requests.get(
            f'{TMDB_BASE_URL}/configuration/languages',
            params={
                'api_key': TMDB_API_KEY
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching languages: {e}")
        return None

def get_user_region(request=None):
    """
    Get user's region for localized content based on IP address.
    Returns GB (UK) as default for better movie content availability.
    
    Args:
        request: Flask request object to extract IP from (for future implementation)
    
    Returns:
        str: Two-letter country code (ISO 3166-1 alpha-2)
    """
    # For now, return GB (UK) as default since it has good movie content
    # This can be enhanced later with actual IP geolocation:
    # - Use IP geolocation services (like ipapi.co, geoip2, etc.)
    # - Check request.environ.get('HTTP_X_FORWARDED_FOR') for real IP in production
    # - Parse user's browser Accept-Language header
    # - Allow users to set their preferred region in profile
    
    if request:
        # Future implementation: extract and geolocate IP
        # ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        # return geolocate_ip(ip)
        pass
    
    return 'GB'  # Default to UK for better movie availability
