from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = os.getenv('TMDB_BASE_URL')

print(f"TMDB_API_KEY: {TMDB_API_KEY}")
print(f"TMDB_BASE_URL: {TMDB_BASE_URL}")

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
    params = {'api_key': TMDB_API_KEY, 'language': 'zh-CN'}
    print(f"Request URL: {url}")
    print(f"Request params: {params}")
    try:
        response = requests.get(url, params=params)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text[:200]}...")  # Print first 200 chars of response
        return jsonify(response.json())
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
            'language': 'zh-CN'
        }
    )
    return jsonify(response.json())


@app.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    response = requests.get(
        f'{TMDB_BASE_URL}/movie/{movie_id}',
        params={'api_key': TMDB_API_KEY, 'language': 'zh-CN'}
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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
