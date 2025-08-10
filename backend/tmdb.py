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
    
    Args:
        request: Flask request object to extract IP from
    
    Returns:
        str: Two-letter country code (ISO 3166-1 alpha-2)
    """
    if request:
        try:
            # Get real IP address, considering proxies and load balancers
            ip = request.environ.get('HTTP_X_FORWARDED_FOR', 
                                   request.environ.get('HTTP_X_REAL_IP', 
                                                     request.remote_addr))
            if ip:
                # Take the first IP if there are multiple (comma-separated)
                ip = ip.split(',')[0].strip()
                
                # Skip local/private IPs
                if not (ip.startswith('127.') or ip.startswith('192.168.') or 
                       ip.startswith('10.') or ip.startswith('172.') or 
                       ip == 'localhost'):
                    
                    # Use a free IP geolocation service
                    import requests
                    try:
                        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=2)
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('status') == 'success':
                                country_code = data.get('countryCode', 'US')
                                print(f"Detected user region: {country_code} for IP: {ip}")
                                return country_code
                    except Exception as e:
                        print(f"IP geolocation failed: {e}")
        except Exception as e:
            print(f"Error getting user region: {e}")
    
    # Default fallback regions for better movie content
    return 'US'  # Default to US for best movie availability
