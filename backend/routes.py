from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from models import db, User, Movie, Rating, WatchlistItem
from tmdb import fetch_movie_details, search_movies, get_popular_movies

# Create blueprints
auth_bp = Blueprint('auth', __name__)
movie_bp = Blueprint('movie', __name__)
user_bp = Blueprint('user', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ['username', 'password', 'email']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # 创建新用户
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # 生成访问令牌
    access_token = create_access_token(identity=user.id)
    
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
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    
    return jsonify({'error': 'Invalid username or password'}), 401

@movie_bp.route('/<int:movie_id>/watchlist', methods=['POST'])
@jwt_required()
def toggle_watchlist(movie_id):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # 查找电影
    movie = Movie.query.filter_by(tmdb_id=movie_id).first()
    if not movie:
        # 如果电影不在数据库中，从TMDB获取并添加
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
    
    # 检查是否已在watchlist中
    watchlist_item = WatchlistItem.query.filter_by(
        user_id=user_id, movie_id=movie.id
    ).first()
    
    if watchlist_item:
        db.session.delete(watchlist_item)
        db.session.commit()
        return jsonify({'message': 'Removed from watchlist', 'added': False})
    
    watchlist_item = WatchlistItem(user_id=user_id, movie_id=movie.id)
    db.session.add(watchlist_item)
    db.session.commit()
    
    return jsonify({'message': 'Added to watchlist', 'added': True})

@user_bp.route('/watchlist', methods=['GET'])
@jwt_required()
def get_watchlist():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # 获取用户的watchlist电影
    watchlist_items = WatchlistItem.query.filter_by(user_id=user_id).all()
    movies = []
    
    for item in watchlist_items:
        movie = Movie.query.get(item.movie_id)
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

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'watchlist_count': WatchlistItem.query.filter_by(user_id=user_id).count(),
        'ratings_count': Rating.query.filter_by(user_id=user_id).count()
    })
