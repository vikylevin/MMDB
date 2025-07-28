import os
from datetime import datetime, timedelta
import requests
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from dotenv import load_dotenv
from models import db, User, Rating, WatchlistItem, Movie

# Load environment variables
load_dotenv()

# TMDB API Configuration
TMDB_BASE_URL = os.getenv('TMDB_BASE_URL', 'https://api.themoviedb.org/3')
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}}, allow_headers=["Content-Type", "Authorization"])

# Configure Flask app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-super-secret-key')
# Default to development database URL if not set in environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:123456@localhost:5432/movies_db')
# Ensure database URL has the correct prefix
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-super-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Create tables
with app.app_context():
    db.create_all()

# Movie routes
@app.route('/api/movies/popular', methods=['GET'])
def get_popular_movies():
    print("Fetching popular movies...")
    page = request.args.get('page', 1, type=int)
    url = f'{TMDB_BASE_URL}/movie/popular'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-GB',
        'page': page
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if 'results' in data:
            data['results'] = data['results'][:20]  # Changed from 18 to 20 movies per page
        return jsonify(data)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/movies/search', methods=['GET'])
def search_movies():
    query = request.args.get('query', '')
    response = requests.get(
        f'{TMDB_BASE_URL}/search/movie',
        params={
            'api_key': TMDB_API_KEY,
            'query': query,
            'language': 'en-GB'
        }
    )
    return jsonify(response.json())

@app.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    response = requests.get(
        f'{TMDB_BASE_URL}/movie/{movie_id}',
        params={'api_key': TMDB_API_KEY, 'language': 'en-GB'}
    )
    return jsonify(response.json())

@app.route('/api/movies/<category>', methods=['GET'])
def get_movies_by_category(category):
    print(f"Fetching {category} movies...")
    page = request.args.get('page', 1, type=int)

    category_mapping = {
        'popular': 'popular',
        'top-rated': 'top_rated',
        'upcoming': 'upcoming',
        'now-playing': 'now_playing'
    }

    if category not in category_mapping:
        return jsonify({'error': 'Invalid category'}), 400

    tmdb_category = category_mapping[category]
    url = f'{TMDB_BASE_URL}/movie/{tmdb_category}'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-GB',
        'page': page
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if 'results' in data:
            data['results'] = data['results'][:20]  # Limit to 20 movies for all categories
        return jsonify(data)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    if category == 'upcoming':
        params['region'] = 'GB'
        
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if 'results' in data:
            results = data['results']
            if category == 'upcoming':
                current_date = datetime.now().strftime('%Y-%m-%d')
                results = [
                    movie for movie in results 
                    if movie.get('release_date', '') > current_date
                ]
                results = sorted(results, key=lambda x: x.get('release_date', ''))
            data['results'] = results[:18]
        return jsonify(data)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Authentication routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()

    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=str(user.id))  # identity 必须为字符串
        return jsonify({
            'message': 'Logged in successfully',
            'token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })

    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/auth/user', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    })

# Rating routes
@app.route('/api/movies/<int:movie_id>/ratings', methods=['GET', 'POST'])
@jwt_required()
def movie_ratings(movie_id):
    if request.method == 'GET':
        ratings = Rating.query.filter_by(movie_id=movie_id).all()
        return jsonify([{
            'id': rating.id,
            'rating': rating.rating,
            'user_id': rating.user_id,
            'created_at': rating.created_at.isoformat()
        } for rating in ratings])
    
    elif request.method == 'POST':
        if not request.is_json:
            return jsonify({'error': 'Missing JSON'}), 400
        
        data = request.json
        if 'rating' not in data:
            return jsonify({'error': 'Missing rating value'}), 400
            
        user_id = get_jwt_identity()
        rating = Rating(
            movie_id=movie_id,
            user_id=user_id,
            rating=data['rating']
        )
        db.session.add(rating)
        db.session.commit()
        return jsonify({
            'id': rating.id,
            'rating': rating.rating,
            'user_id': rating.user_id,
            'created_at': rating.created_at.isoformat()
        }), 201

# Watchlist routes
@app.route('/api/watchlist/check/<movie_id>', methods=['GET'])
@jwt_required()
def check_watchlist(movie_id):
    print('Received movie_id (check):', movie_id)
    user_id = get_jwt_identity()
    try:
        tmdb_id = int(movie_id)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid TMDB id'}), 400
    item = WatchlistItem.query.filter_by(user_id=user_id, movie_id=tmdb_id).first()
    return jsonify({'in_watchlist': item is not None})

@app.route('/api/watchlist/add/<movie_id>', methods=['POST'])
@jwt_required()
def add_to_watchlist(movie_id):
    print('Received movie_id (add):', movie_id)
    user_id = get_jwt_identity()
    try:
        tmdb_id = int(movie_id)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid TMDB id'}), 400
    item = WatchlistItem.query.filter_by(user_id=user_id, movie_id=tmdb_id).first()
    if item:
        return jsonify({'message': 'Movie already in watchlist'}), 400
    item = WatchlistItem(user_id=user_id, movie_id=tmdb_id)
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Movie added to watchlist'})

@app.route('/api/watchlist/remove/<movie_id>', methods=['POST'])
@jwt_required()
def remove_from_watchlist(movie_id):
    print('Received movie_id (remove):', movie_id)
    user_id = get_jwt_identity()
    try:
        tmdb_id = int(movie_id)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid TMDB id'}), 400
    item = WatchlistItem.query.filter_by(user_id=user_id, movie_id=tmdb_id).first()
    if not item:
        return jsonify({'message': 'Movie not in watchlist'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Movie removed from watchlist'})

@app.route('/api/watchlist', methods=['GET'])
@jwt_required()
def get_watchlist():
    user_id = get_jwt_identity()
    items = WatchlistItem.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'movie_id': item.movie_id,
        'added_at': item.added_at.isoformat()
    } for item in items])

if __name__ == '__main__':
    app.run(debug=True)
