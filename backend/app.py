from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path=env_path)
print(f"Loading .env from: {env_path}")

app = Flask(__name__)
CORS(app)

# Configuration
# Ensure instance folder exists
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

# Explicitly set the database URL with absolute path
db_path = os.path.join(instance_path, 'movies.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# If environment variables are not set, use default values
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '4bd99769f8271938f81a8b9f9be62d7d')
TMDB_BASE_URL = os.getenv('TMDB_BASE_URL', 'https://api.themoviedb.org/3')

print(f"TMDB_API_KEY: {TMDB_API_KEY}")
print(f"TMDB_BASE_URL: {TMDB_BASE_URL}")
print(f"Current working directory: {os.getcwd()}")
print(f"Checking if .env file exists: {os.path.exists('.env')}")

# Enable CORS
from flask_cors import CORS

CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize database
db = SQLAlchemy(app)


# Models
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    overview = db.Column(db.Text)
    poster_path = db.Column(db.String(200))
    vote_average = db.Column(db.Float)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


@app.route('/api/movies/popular', methods=['GET'])
def get_popular_movies():
    print("Fetching popular movies...")
    url = f'{TMDB_BASE_URL}/movie/popular'
    params = {'api_key': TMDB_API_KEY, 'language': 'en-US'}
    print(f"Request URL: {url}")
    print(f"Request params: {params}")
    try:
        print("Making request to TMDB API...")
        response = requests.get(url, params=params, timeout=10)
        print(f"Response status code: {response.status_code}")

        if response.status_code != 200:
            print(f"Error response from TMDB: {response.text}")
            return jsonify({
                'error': f'TMDB API returned status code {response.status_code}',
                'results': []
            }), response.status_code

        data = response.json()
        print(f"Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dictionary'}")

        if 'results' not in data or not isinstance(data['results'], list):
            print(f"Unexpected response format: {data}")
            # Return an empty results array to prevent frontend errors
            return jsonify({'results': [], 'error': 'Unexpected response format from TMDB API'})

        # Ensure we return proper format even if API response structure changes
        return jsonify({
            'results': data.get('results', []),
            'page': data.get('page', 1),
            'total_pages': data.get('total_pages', 1),
            'total_results': data.get('total_results', len(data.get('results', [])))
        })
    except requests.exceptions.Timeout:
        print("Request to TMDB API timed out")
        return jsonify({'error': 'Request to TMDB API timed out', 'results': []}), 504
    except requests.exceptions.ConnectionError:
        print("Connection error when contacting TMDB API")
        return jsonify({'error': 'Could not connect to TMDB API', 'results': []}), 502
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'results': []}), 500


@app.route('/api/movies/search', methods=['GET'])
def search_movies():
    query = request.args.get('query', '')
    response = requests.get(
        f'{TMDB_BASE_URL}/search/movie',
        params={
            'api_key': TMDB_API_KEY,
            'query': query,
            'language': 'en-US'
        }
    )
    return jsonify(response.json())


@app.route('/api/movies/top-rated', methods=['GET'])
def get_top_rated_movies():
    response = requests.get(
        f'{TMDB_BASE_URL}/movie/top_rated',
        params={'api_key': TMDB_API_KEY, 'language': 'en-US'}
    )
    return jsonify(response.json())


@app.route('/api/movies/upcoming', methods=['GET'])
def get_upcoming_movies():
    response = requests.get(
        f'{TMDB_BASE_URL}/movie/upcoming',
        params={'api_key': TMDB_API_KEY, 'language': 'en-US'}
    )
    return jsonify(response.json())


@app.route('/api/movies/trending', methods=['GET'])
def get_trending_movies():
    try:
        print(f"Fetching trending movies from: {TMDB_BASE_URL}/trending/movie/week")
        response = requests.get(
            f'{TMDB_BASE_URL}/trending/movie/week',
            params={'api_key': TMDB_API_KEY, 'language': 'en-US'}
        )
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        print(f"Trending API response code: {response.status_code}")
        data = response.json()
        print(f"Trending API response data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dictionary'}")
        return jsonify(data)
    except Exception as e:
        print(f"Error fetching trending movies: {str(e)}")
        return jsonify({'error': str(e), 'results': []}), 500


@app.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    response = requests.get(
        f'{TMDB_BASE_URL}/movie/{movie_id}',
        params={'api_key': TMDB_API_KEY, 'language': 'en-US'}
    )
    return jsonify(response.json())


@app.route('/api/movies/<int:movie_id>/reviews', methods=['GET', 'POST'])
def movie_reviews(movie_id):
    if request.method == 'GET':
        reviews = Review.query.filter_by(movie_id=movie_id).all()
        return jsonify([{
            'id': review.id,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.isoformat()
        } for review in reviews])

    elif request.method == 'POST':
        data = request.json
        review = Review(
            movie_id=movie_id,
            rating=data['rating'],
            comment=data.get('comment', '')
        )
        db.session.add(review)
        db.session.commit()
        return jsonify({
            'id': review.id,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.isoformat()
        }), 201


@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({
        'status': 'ok',
        'message': 'API is working',
        'tmdb_api_key_set': TMDB_API_KEY is not None,
        'tmdb_base_url_set': TMDB_BASE_URL is not None,
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
