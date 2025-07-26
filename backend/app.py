from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration for database and API
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:tele@localhost:5432/movie_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = os.getenv('TMDB_BASE_URL')
app.secret_key = os.getenv('SECRET_KEY', 'your_default_secret_key')  # Add secret key configuration

print(f"TMDB_API_KEY: {TMDB_API_KEY}")
print(f"TMDB_BASE_URL: {TMDB_BASE_URL}")

# Initialize database
db = SQLAlchemy(app)

# Database Models
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=False)  # Movie ID from TMDB API
    title = db.Column(db.String(200), nullable=False)  # Movie title
    overview = db.Column(db.Text)  # Movie description
    poster_path = db.Column(db.String(200))  # Path to movie poster image
    vote_average = db.Column(db.Float)  # Average rating from TMDB
    
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# User Model for authentication and user management
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)  # Unique username
    email = db.Column(db.String(120), unique=True, nullable=False)  # Unique email address
    password_hash = db.Column(db.String(128))  # Hashed password for security
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Account creation timestamp

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# User Rating Model for storing user movie ratings
class UserRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Reference to user
    movie_id = db.Column(db.Integer, nullable=False)  # Movie ID being rated
    rating = db.Column(db.Float, nullable=False)  # User's rating value
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Rating timestamp

# Watch List Model for users to save movies they want to watch
class WatchList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Reference to user
    movie_id = db.Column(db.Integer, nullable=False)  # Movie ID saved to watchlist
    added_at = db.Column(db.DateTime, default=datetime.utcnow)  # When movie was added to watchlist

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
        # Limit the number of movies returned per page to 18
        if 'results' in data:
            data['results'] = data['results'][:18]
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

@app.route('/api/movies/<category>', methods=['GET'])
def get_movies_by_category(category):
    print(f"Fetching {category} movies...")
    page = request.args.get('page', 1, type=int)

    # Map route parameters to TMDB's actual paths
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
    
    # Basic params
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-GB',
        'page': page,
    }
    
    # Add region parameter for upcoming movies to get more relevant results
    if category == 'upcoming':
        params['region'] = 'GB'  # Use GB (United Kingdom) region for upcoming movies
        
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'results' in data:
            results = data['results']
            
            # For upcoming movies, filter for future releases and sort by date
            if category == 'upcoming':
                current_date = datetime.now().strftime('%Y-%m-%d')
                # Filter movies with release dates after current date
                results = [
                    movie for movie in results 
                    if movie.get('release_date', '') > current_date
                ]
                # Sort by release date
                results = sorted(results, key=lambda x: x.get('release_date', ''))
            
            # Limit results per page
            data['results'] = results[:18]
            
        return jsonify(data)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

# User authentication routes
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
        session['user_id'] = user.id
        return jsonify({
            'message': 'Logged in successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })

    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/auth/user', methods=['GET'])
def get_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user = User.query.get(session['user_id'])
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    })

# User rating routes
@app.route('/api/movies/<int:movie_id>/rate', methods=['POST'])
def rate_movie(movie_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.json
    rating = UserRating.query.filter_by(
        user_id=session['user_id'],
        movie_id=movie_id
    ).first()

    if rating:
        rating.rating = data['rating']
    else:
        rating = UserRating(
            user_id=session['user_id'],
            movie_id=movie_id,
            rating=data['rating']
        )
        db.session.add(rating)

    db.session.commit()
    return jsonify({'message': 'Rating saved successfully'})

# Watchlist routes
@app.route('/api/watchlist', methods=['GET', 'POST'])
def watchlist():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    if request.method == 'GET':
        items = WatchList.query.filter_by(user_id=session['user_id']).all()
        return jsonify([{
            'movie_id': item.movie_id,
            'added_at': item.added_at.isoformat()
        } for item in items])

    data = request.json
    item = WatchList.query.filter_by(
        user_id=session['user_id'],
        movie_id=data['movie_id']
    ).first()

    if item:
        db.session.delete(item)
        message = 'Movie removed from watchlist'
    else:
        item = WatchList(user_id=session['user_id'], movie_id=data['movie_id'])
        db.session.add(item)
        message = 'Movie added to watchlist'

    db.session.commit()
    return jsonify({'message': message})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)