import os
import requests
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_cors import cross_origin
from models import db, User, Movie, Rating, Review, WatchLaterItem, WatchedItem, LikedItem, ReviewLike, ReviewComment
from tmdb import fetch_movie_details, get_popular_movies, get_top_rated_movies, get_upcoming_movies, get_movie_genres, get_available_languages, get_user_region

# Define blueprints
auth_bp = Blueprint('auth', __name__)
movie_bp = Blueprint('movie', __name__)
user_bp = Blueprint('user', __name__)

# TMDB configuration
TMDB_BASE_URL = os.getenv('TMDB_BASE_URL', 'https://api.themoviedb.org/3')
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

# Add /api/movie/<int:movie_id>/reviews route after blueprint definitions
@movie_bp.route('/<int:movie_id>/reviews', methods=['GET'])
def get_movie_reviews(movie_id):
    """
    Return reviews for a movie from local database with interaction data
    """
    current_user_id = None
    # Get current user if authenticated (optional for viewing reviews)
    try:
        from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
    except:
        pass
    
    # Find the movie in local database
    movie = Movie.query.filter_by(tmdb_id=movie_id).first()
    if not movie:
        return jsonify([])
    
    # Get all reviews for this movie
    reviews = Review.query.filter_by(movie_id=movie.id).order_by(Review.created_at.desc()).all()
    review_list = []
    
    for review in reviews:
        user = User.query.get(review.user_id)
        
        # Count likes for this review
        like_count = ReviewLike.query.filter_by(review_id=review.id).count()
        
        # Count comments for this review
        comment_count = ReviewComment.query.filter_by(review_id=review.id).count()
        
        # Check if current user has liked this review
        user_has_liked = False
        if current_user_id:
            user_has_liked = ReviewLike.query.filter_by(
                user_id=current_user_id, 
                review_id=review.id
            ).first() is not None
        
        review_data = {
            'id': review.id,
            'author': user.username if user else 'Unknown',
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.isoformat() if review.created_at else None,
            'updated_at': review.updated_at.isoformat() if review.updated_at else None,
            'like_count': like_count,
            'comment_count': comment_count,
            'user_has_liked': user_has_liked
        }
        review_list.append(review_data)
    
    return jsonify(review_list)

@movie_bp.route('/<int:movie_id>/reviews', methods=['POST'])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def submit_movie_review(movie_id):
    """
    Submit a review for a movie. This also handles rating updates.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    rating = data.get('rating')
    comment = data.get('comment', '').strip()
    
    if not rating or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # Find or create movie in local DB
    movie = Movie.query.filter_by(tmdb_id=movie_id).first()
    if not movie:
        movie_data = fetch_movie_details(movie_id)
        if not movie_data:
            return jsonify({'error': 'Movie not found'}), 404
        movie = Movie(
            tmdb_id=movie_id,
            title=movie_data['title'],
            overview=movie_data.get('overview', ''),
            poster_path=movie_data.get('poster_path', ''),
            vote_average=movie_data.get('vote_average', 0.0)
        )
        db.session.add(movie)
        db.session.commit()
    
    # Update or create rating
    existing_rating = Rating.query.filter_by(user_id=user_id, movie_id=movie.id).first()
    if existing_rating:
        existing_rating.rating = rating
        existing_rating.updated_at = db.func.now()
    else:
        new_rating = Rating(user_id=user_id, movie_id=movie.id, rating=rating)
        db.session.add(new_rating)
    
    # Update or create review (if comment provided)
    if comment:
        existing_review = Review.query.filter_by(user_id=user_id, movie_id=movie.id).first()
        if existing_review:
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.updated_at = db.func.now()
        else:
            new_review = Review(user_id=user_id, movie_id=movie.id, rating=rating, comment=comment)
            db.session.add(new_review)
    
    # Auto-mark as watched when reviewing
    watched_item = WatchedItem.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if not watched_item:
        watched_item = WatchedItem(user_id=user_id, movie_id=movie_id)
        db.session.add(watched_item)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Review submitted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to submit review'}), 500

# Add a catch-all OPTIONS handler for all /api/user/* routes
@user_bp.route('/<path:path>', methods=['OPTIONS'])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
def user_options(path):
    return '', 200

 # Watched movies API
@user_bp.route('/watched', methods=['GET', 'OPTIONS'])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def get_watched():
    """
    Return detailed info for all movies in the user's watched list.
    If a movie is not in the local Movie table, fetch from TMDB and add it.
    """
    user_id = get_jwt_identity()
    watched_items = WatchedItem.query.filter_by(user_id=user_id).all()
    movies = []
    for item in watched_items:
        # item.movie_id contains TMDB ID, not local database ID
        movie = Movie.query.filter_by(tmdb_id=item.movie_id).first()
        if not movie:
            # If the movie is not in the local DB, try to fetch from TMDB and add it
            try:
                movie_data = fetch_movie_details(item.movie_id)
                if movie_data:
                    movie = Movie(
                        tmdb_id=movie_data['id'],
                        title=movie_data['title'],
                        overview=movie_data.get('overview', ''),
                        poster_path=movie_data.get('poster_path', ''),
                        vote_average=movie_data.get('vote_average', 0.0)
                    )
                    db.session.add(movie)
                    db.session.commit()
            except:
                continue
        if movie:
            movie_info = {
                'id': movie.tmdb_id,
                'title': movie.title,
                'overview': movie.overview,
                'poster_path': movie.poster_path,
                'vote_average': movie.vote_average,
                'added_at': item.added_at.isoformat() if hasattr(item, 'added_at') else None
            }
            
            # Try to get genres from TMDB but don't block if it fails
            try:
                movie_data = fetch_movie_details(movie.tmdb_id)
                if movie_data and 'genres' in movie_data:
                    movie_info['genres'] = movie_data['genres']
                elif movie_data and 'genre_ids' in movie_data:
                    movie_info['genre_ids'] = movie_data['genre_ids']
            except:
                # If TMDB request fails, just continue without genres
                pass
            
            movies.append(movie_info)
    return jsonify(movies)
# --- Toggle watched status for a movie for the current user ---
@user_bp.route('/watched', methods=['POST'])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def toggle_watched():
    """
    Toggle watched status for a movie for the current user.
    Request JSON: { "movie_id": 123 }
    Response: { "watched": true/false }
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    movie_id = data.get('movie_id')
    if not movie_id:
        return jsonify({'error': 'Missing movie_id'}), 400

    # Find or create movie in local DB
    movie = Movie.query.filter_by(tmdb_id=movie_id).first()
    if not movie:
        movie_data = fetch_movie_details(movie_id)
        if not movie_data:
            return jsonify({'error': 'Movie not found'}), 404
        movie = Movie(
            tmdb_id=movie_id,
            title=movie_data['title'],
            overview=movie_data.get('overview', ''),
            poster_path=movie_data.get('poster_path', ''),
            vote_average=movie_data.get('vote_average', 0.0)
        )
        db.session.add(movie)
        db.session.commit()

    # Check if already in watched
    watched = WatchedItem.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if watched:
        db.session.delete(watched)
        db.session.commit()
        return jsonify({'watched': False})
    else:
        watched = WatchedItem(user_id=user_id, movie_id=movie_id)
        db.session.add(watched)
        db.session.commit()
        return jsonify({'watched': True})

@movie_bp.route('/popular', methods=['GET'])
def popular_movies_route():
    """Return a list of popular movies from TMDB."""
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
            data['results'] = data['results'][:20]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@movie_bp.route('/search', methods=['GET'])
def search_movies():
    """Search for movies by query string using TMDB."""
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

@movie_bp.route('/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    """Return details for a specific movie by TMDB id."""
    response = requests.get(
        f'{TMDB_BASE_URL}/movie/{movie_id}',
        params={'api_key': TMDB_API_KEY, 'language': 'en-GB'}
    )
    return jsonify(response.json())

@movie_bp.route('/category/<category>', methods=['GET'])
def get_movies_by_category(category):
    """Return movies by category with optional filters (popular, top-rated, upcoming, now-playing)."""
    page = request.args.get('page', 1, type=int)
    
    # Get filter parameters
    with_genres = request.args.get('with_genres')  # comma-separated genre IDs
    vote_average_gte = request.args.get('vote_average_gte', type=float)
    vote_average_lte = request.args.get('vote_average_lte', type=float)
    with_original_language = request.args.get('with_original_language')
    
    category_mapping = {
        'popular': 'popular',
        'top-rated': 'top_rated',
        'upcoming': 'upcoming',
        'now-playing': 'now_playing'
    }
    
    if category not in category_mapping:
        return jsonify({'error': 'Invalid category'}), 400
    
    try:
        # Use discover endpoint for filtered results
        if category == 'popular':
            data = get_popular_movies(
                page=page,
                with_genres=with_genres,
                vote_average_gte=vote_average_gte,
                vote_average_lte=vote_average_lte,
                with_original_language=with_original_language
            )
        elif category == 'top-rated':
            data = get_top_rated_movies(
                page=page,
                with_genres=with_genres,
                vote_average_gte=vote_average_gte,
                vote_average_lte=vote_average_lte,
                with_original_language=with_original_language
            )
        elif category == 'upcoming':
            # Get user's region based on IP address for region-specific upcoming movies
            user_region = get_user_region(request)
            data = get_upcoming_movies(
                page=page,
                with_genres=with_genres,
                vote_average_gte=vote_average_gte,
                vote_average_lte=vote_average_lte,
                with_original_language=with_original_language,
                region=user_region
            )
        else:  # now-playing - fallback to original API
            tmdb_category = category_mapping[category]
            url = f'{TMDB_BASE_URL}/movie/{tmdb_category}'
            params = {
                'api_key': TMDB_API_KEY,
                'language': 'en-GB',
                'page': page
            }
            response = requests.get(url, params=params)
            data = response.json()
        
        if data and 'results' in data:
            results = data['results']
            # Remove manual filtering for upcoming movies - let TMDB handle pagination
            data['results'] = results
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@movie_bp.route('/genres', methods=['GET'])
def get_movie_genres():
    """Return list of movie genres from TMDB."""
    try:
        data = get_movie_genres()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@movie_bp.route('/languages', methods=['GET'])
def get_available_languages():
    """Return list of available languages from TMDB."""
    try:
        data = get_available_languages()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500







# --- Get all liked movies for the current user ---
@user_bp.route('/likes', methods=['GET', 'OPTIONS'])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def get_likes():
    """
    Return detailed info for all movies in the user's likes.
    If a movie is not in the local Movie table, fetch from TMDB and add it.
    """
    user_id = get_jwt_identity()
    liked_items = LikedItem.query.filter_by(user_id=user_id).all()
    movies = []
    for item in liked_items:
        # item.movie_id contains TMDB ID, not local database ID
        movie = Movie.query.filter_by(tmdb_id=item.movie_id).first()
        if not movie:
            # Fetch from TMDB and add to DB
            try:
                movie_data = fetch_movie_details(item.movie_id)
                if movie_data:
                    movie = Movie(
                        tmdb_id=movie_data['id'],
                        title=movie_data['title'],
                        overview=movie_data.get('overview', ''),
                        poster_path=movie_data.get('poster_path', ''),
                        vote_average=movie_data.get('vote_average', 0.0)
                    )
                    db.session.add(movie)
                    db.session.commit()
            except:
                continue
        if movie:
            movie_info = {
                'id': movie.tmdb_id,
                'title': movie.title,
                'overview': movie.overview,
                'poster_path': movie.poster_path,
                'vote_average': movie.vote_average,
                'added_at': item.added_at.isoformat() if hasattr(item, 'added_at') else None
            }
            
            # Try to get genres from TMDB but don't block if it fails
            try:
                movie_data = fetch_movie_details(movie.tmdb_id)
                if movie_data and 'genres' in movie_data:
                    movie_info['genres'] = movie_data['genres']
                elif movie_data and 'genre_ids' in movie_data:
                    movie_info['genre_ids'] = movie_data['genre_ids']
            except:
                # If TMDB request fails, just continue without genres
                pass
            
            movies.append(movie_info)
    return jsonify(movies)

@user_bp.route('/likes', methods=['POST'])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def toggle_like():
    """
    Toggle like (add/remove) for a movie for the current user.
    Request JSON: { "movie_id": 123 }
    Response: { "added": true/false }
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    movie_id = data.get('movie_id')
    if not movie_id:
        return jsonify({'error': 'Missing movie_id'}), 400

    # Find or create movie in local DB
    movie = Movie.query.filter_by(tmdb_id=movie_id).first()
    if not movie:
        movie_data = fetch_movie_details(movie_id)
        if not movie_data:
            return jsonify({'error': 'Movie not found'}), 404
        movie = Movie(
            tmdb_id=movie_id,
            title=movie_data['title'],
            overview=movie_data.get('overview', ''),
            poster_path=movie_data.get('poster_path', ''),
            vote_average=movie_data.get('vote_average', 0.0)
        )
        db.session.add(movie)
        db.session.commit()

    # Check if already liked
    liked = LikedItem.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if liked:
        db.session.delete(liked)
        db.session.commit()
        return jsonify({'added': False})
    else:
        liked = LikedItem(user_id=user_id, movie_id=movie_id)
        db.session.add(liked)
        db.session.commit()
        return jsonify({'added': True})
    """
    Return detailed info for all movies in the user's watch later list.
    If a movie is not in the local Movie table, fetch from TMDB and add it.
    """
    user_id = get_jwt_identity()
    watch_later_items = WatchLaterItem.query.filter_by(user_id=user_id).all()
    movies = []
    for item in watch_later_items:
        # Try to get movie from local DB
        movie = Movie.query.filter_by(tmdb_id=item.movie_id).first()
        if not movie:
            # Fetch from TMDB and add to DB
            movie_data = fetch_movie_details(item.movie_id)
            if movie_data:
                movie = Movie(
                    tmdb_id=movie_data['id'],
                    title=movie_data['title'],
                    overview=movie_data.get('overview', ''),
                    poster_path=movie_data.get('poster_path', ''),
                    vote_average=movie_data.get('vote_average', 0.0)
                )
                db.session.add(movie)
                db.session.commit()
        if movie:
            movies.append({
                'id': movie.tmdb_id,
                'title': movie.title,
                'overview': movie.overview,
                'poster_path': movie.poster_path,
                'vote_average': movie.vote_average,
                'added_at': item.added_at.isoformat()
            })
    return jsonify(movies)



@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['username', 'password', 'email']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if username and email already exist
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Generate access token
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(k in data for k in ['username', 'password']):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    
    return jsonify({'error': 'Invalid username or password'}), 401

@movie_bp.route('/<int:movie_id>/watch-later', methods=['POST'])
@jwt_required()
def toggle_watch_later(movie_id):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Find movie
    movie = Movie.query.filter_by(tmdb_id=movie_id).first()
    if not movie:
        # If movie not in database, fetch from TMDB and add it
        movie_data = fetch_movie_details(movie_id)
        if not movie_data:
            return jsonify({'error': 'Movie not found'}), 404
            
        movie = Movie(
            tmdb_id=movie_id,
            title=movie_data['title'],
            overview=movie_data.get('overview', ''),
            poster_path=movie_data.get('poster_path', ''),
            vote_average=movie_data.get('vote_average', 0.0)
        )
        db.session.add(movie)
        db.session.commit()
    
    # Check if movie is already in watch later list
    watch_later_item = WatchLaterItem.query.filter_by(
        user_id=user_id, movie_id=movie_id
    ).first()
    
    if watch_later_item:
        db.session.delete(watch_later_item)
        db.session.commit()
        return jsonify({'message': 'Removed from watch later', 'added': False})
    
    watch_later_item = WatchLaterItem(user_id=user_id, movie_id=movie_id)
    db.session.add(watch_later_item)
    db.session.commit()
    
    return jsonify({'message': 'Added to watch later', 'added': True})

@user_bp.route('/watch-later', methods=['GET', 'OPTIONS'])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def get_watch_later():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get user's watch later movies
    watch_later_items = WatchLaterItem.query.filter_by(user_id=user_id).all()
    movies = []
    
    for item in watch_later_items:
        movie = Movie.query.filter_by(tmdb_id=item.movie_id).first()
        if movie:
            movie_info = {
                'id': movie.tmdb_id,
                'title': movie.title,
                'overview': movie.overview,
                'poster_path': movie.poster_path,
                'vote_average': movie.vote_average,
                'added_at': item.added_at.isoformat()
            }
            
            # Try to get genres from TMDB but don't block if it fails
            try:
                movie_data = fetch_movie_details(movie.tmdb_id)
                if movie_data and 'genres' in movie_data:
                    movie_info['genres'] = movie_data['genres']
                elif movie_data and 'genre_ids' in movie_data:
                    movie_info['genre_ids'] = movie_data['genre_ids']
            except:
                # If TMDB request fails, just continue without genres
                pass
            
            movies.append(movie_info)
    
    return jsonify(movies)

# Backward compatibility aliases
@user_bp.route('/watchlist', methods=['GET', 'OPTIONS'])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def get_watchlist():
    """Backward compatibility alias for get_watch_later"""
    return get_watch_later()

@movie_bp.route('/<int:movie_id>/watchlist', methods=['POST'])
@jwt_required()
def toggle_watchlist(movie_id):
    """Backward compatibility alias for toggle_watch_later"""
    return toggle_watch_later(movie_id)

@user_bp.route('/profile', methods=['GET', 'OPTIONS'])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'watch_later_count': WatchLaterItem.query.filter_by(user_id=user_id).count(),
        'ratings_count': Rating.query.filter_by(user_id=user_id).count()
    })

# --- Movie rating routes ---
@movie_bp.route('/<int:movie_id>/rate', methods=['POST', 'OPTIONS'])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def rate_movie(movie_id):
    """
    Rate a movie for the current user.
    Request JSON: { "rating": 4.5 }
    Response: { "success": true, "rating": 4.5 }
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    rating_value = data.get('rating')
    
    if rating_value is None:
        return jsonify({'error': 'Missing rating value'}), 400
    
    if not (0 <= rating_value <= 5):
        return jsonify({'error': 'Rating must be between 0 and 5'}), 400
    
    # Find or create movie in local DB
    movie = Movie.query.filter_by(tmdb_id=movie_id).first()
    if not movie:
        movie_data = fetch_movie_details(movie_id)
        if not movie_data:
            return jsonify({'error': 'Movie not found'}), 404
        movie = Movie(
            tmdb_id=movie_id,
            title=movie_data['title'],
            overview=movie_data.get('overview', ''),
            poster_path=movie_data.get('poster_path', ''),
            vote_average=movie_data.get('vote_average', 0.0)
        )
        db.session.add(movie)
        db.session.commit()
    
    # Check if user has already rated this movie
    existing_rating = Rating.query.filter_by(
        user_id=user_id, movie_id=movie.id
    ).first()
    
    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating_value
    else:
        # Create new rating
        new_rating = Rating(
            user_id=user_id,
            movie_id=movie.id,
            rating=rating_value
        )
        db.session.add(new_rating)
    
    # IMPORTANT: Also update the rating in Review table if a review exists
    existing_review = Review.query.filter_by(
        user_id=user_id, movie_id=movie.id
    ).first()
    
    if existing_review:
        # Update the rating in the review to keep consistency
        existing_review.rating = rating_value
        existing_review.updated_at = db.func.now()
    
    # Auto-add to watched list when rating a movie (if rating > 0)
    if rating_value > 0:
        existing_watched = WatchedItem.query.filter_by(
            user_id=user_id, movie_id=movie_id
        ).first()
        
        if not existing_watched:
            watched_item = WatchedItem(
                user_id=user_id,
                movie_id=movie_id
            )
            db.session.add(watched_item)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'rating': rating_value
    })

@movie_bp.route('/<int:movie_id>/rating', methods=['GET', 'OPTIONS'])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def get_movie_rating(movie_id):
    """
    Get the current user's rating for a specific movie.
    Response: { "rating": 4.5 } or { "rating": null }
    """
    user_id = get_jwt_identity()
    
    # Find movie in local DB
    movie = Movie.query.filter_by(tmdb_id=movie_id).first()
    if not movie:
        return jsonify({'rating': None})
    
    # Get user's rating for this movie
    rating = Rating.query.filter_by(
        user_id=user_id, movie_id=movie.id
    ).first()
    
    return jsonify({
        'rating': rating.rating if rating else None
    })

@user_bp.route('/reviews', methods=['GET', 'OPTIONS'])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def get_user_reviews():
    """
    Get all reviews made by the current user.
    Response: [ { "movie_id": 123, "movie_title": "Movie Name", "rating": 4.5, "review": "Great movie!", "created_at": "..." } ]
    """
    user_id = get_jwt_identity()
    
    # Get all reviews by user with movie details
    reviews_query = db.session.query(Review, Movie).join(
        Movie, Review.movie_id == Movie.id
    ).filter(Review.user_id == user_id).all()
    
    reviews = []
    for review, movie in reviews_query:
        review_data = {
            'id': review.id,
            'movie_id': movie.tmdb_id,
            'movie_title': movie.title,
            'movie_poster': movie.poster_path,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.isoformat() if review.created_at else None,
            'updated_at': review.updated_at.isoformat() if review.updated_at else None
        }
        reviews.append(review_data)
    
    # Also include ratings without reviews for completeness
    ratings_without_reviews = db.session.query(Rating, Movie).join(
        Movie, Rating.movie_id == Movie.id
    ).filter(
        Rating.user_id == user_id,
        ~Rating.movie_id.in_(
            db.session.query(Review.movie_id).filter_by(user_id=user_id)
        )
    ).all()
    
    for rating, movie in ratings_without_reviews:
        review_data = {
            'id': f"rating_{rating.id}",  # Distinguish from review IDs
            'movie_id': movie.tmdb_id,
            'movie_title': movie.title,
            'movie_poster': movie.poster_path,
            'rating': rating.rating,
            'comment': None,  # No comment for ratings without reviews
            'created_at': rating.created_at.isoformat() if rating.created_at else None,
            'updated_at': rating.updated_at.isoformat() if rating.updated_at else None
        }
        reviews.append(review_data)
    
    # Sort by creation date (most recent first)
    reviews.sort(key=lambda x: x['created_at'] or '', reverse=True)
    
    return jsonify(reviews)

# Review interaction routes
@movie_bp.route('/reviews/<int:review_id>/like', methods=['POST'])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def toggle_review_like(review_id):
    """
    Toggle like status for a review
    """
    user_id = get_jwt_identity()
    
    # Check if review exists
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    
    # Check if user has already liked this review
    existing_like = ReviewLike.query.filter_by(
        user_id=user_id, 
        review_id=review_id
    ).first()
    
    if existing_like:
        # Unlike: remove the like
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    else:
        # Like: add a new like
        new_like = ReviewLike(user_id=user_id, review_id=review_id)
        db.session.add(new_like)
        db.session.commit()
        liked = True
    
    # Get updated like count
    like_count = ReviewLike.query.filter_by(review_id=review_id).count()
    
    return jsonify({
        'liked': liked,
        'like_count': like_count
    })

@movie_bp.route('/reviews/<int:review_id>/comments', methods=['GET'])
def get_review_comments(review_id):
    """
    Get all comments for a specific review
    """
    # Check if review exists
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    
    # Get all comments for this review
    comments = ReviewComment.query.filter_by(review_id=review_id).order_by(ReviewComment.created_at.asc()).all()
    comment_list = []
    
    for comment in comments:
        user = User.query.get(comment.user_id)
        comment_data = {
            'id': comment.id,
            'username': user.username if user else 'Unknown',
            'comment': comment.comment,
            'created_at': comment.created_at.isoformat() if comment.created_at else None
        }
        comment_list.append(comment_data)
    
    return jsonify(comment_list)

@movie_bp.route('/reviews/<int:review_id>/comments', methods=['POST'])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def add_review_comment(review_id):
    """
    Add a comment to a review
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    comment_text = data.get('comment', '').strip()
    if not comment_text:
        return jsonify({'error': 'Comment text is required'}), 400
    
    # Check if review exists
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    
    # Create new comment
    new_comment = ReviewComment(
        user_id=user_id,
        review_id=review_id,
        comment=comment_text
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    # Return the new comment
    user = User.query.get(user_id)
    return jsonify({
        'id': new_comment.id,
        'author': user.username if user else 'Unknown',
        'comment': new_comment.comment,
        'created_at': new_comment.created_at.isoformat()
    }), 201

# Review management routes
@movie_bp.route('/reviews/<int:review_id>', methods=['PUT'])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def update_review(review_id):
    """
    Update a review (only by the author)
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Check if review exists and belongs to current user
    review = Review.query.filter_by(id=review_id, user_id=user_id).first()
    if not review:
        return jsonify({'error': 'Review not found or you do not have permission to edit it'}), 404
    
    # Validate input
    rating = data.get('rating')
    comment = data.get('comment', '').strip()
    
    if not rating or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # Update review
    review.rating = rating
    review.comment = comment if comment else None
    review.updated_at = db.func.now()
    
    # Also update the rating record
    rating_record = Rating.query.filter_by(user_id=user_id, movie_id=review.movie_id).first()
    if rating_record:
        rating_record.rating = rating
        rating_record.updated_at = db.func.now()
    
    db.session.commit()
    
    # Return updated review
    user = User.query.get(user_id)
    return jsonify({
        'id': review.id,
        'author': user.username if user else 'Unknown',
        'rating': review.rating,
        'comment': review.comment,
        'created_at': review.created_at.isoformat(),
        'updated_at': review.updated_at.isoformat()
    })

@movie_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@cross_origin(origins=["http://localhost:5173"], supports_credentials=True)
@jwt_required()
def delete_review(review_id):
    """
    Delete a review (only by the author)
    """
    user_id = get_jwt_identity()
    
    # Check if review exists and belongs to current user
    review = Review.query.filter_by(id=review_id, user_id=user_id).first()
    if not review:
        return jsonify({'error': 'Review not found or you do not have permission to delete it'}), 404
    
    # Delete the review (cascade will handle likes and comments)
    db.session.delete(review)
    db.session.commit()
    
    return jsonify({'message': 'Review deleted successfully'})
