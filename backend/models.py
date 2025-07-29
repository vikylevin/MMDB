from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()

# WatchedItem model for tracking watched movies
class WatchedItem(db.Model):
    __tablename__ = 'watched_item'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)  # TMDB id, no ForeignKey
    added_at = db.Column(db.DateTime, server_default=db.func.now())
    __table_args__ = (
        db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_watched'),
    )

# FavoriteItem model for tracking liked movies
class FavoriteItem(db.Model):
    __tablename__ = 'favorite_item'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)  # TMDB id, no ForeignKey
    added_at = db.Column(db.DateTime, server_default=db.func.now())
    __table_args__ = (
        db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_favorite'),
    )

# WatchlistItem model for tracking watch later movies
class WatchlistItem(db.Model):
    __tablename__ = 'watchlist_item'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)  # TMDB id, no ForeignKey
    added_at = db.Column(db.DateTime, server_default=db.func.now())
    __table_args__ = (
        db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_watchlist'),
    )

# Movie model for storing movie details
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    overview = db.Column(db.Text)
    poster_path = db.Column(db.String(200))
    vote_average = db.Column(db.Float)

# User model for storing user information
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Rating model for storing user ratings for movies
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    __table_args__ = (
        db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_rating'),
    )


# Add relationships after all classes are defined
User.watchlist_items = db.relationship('WatchlistItem', backref='user', lazy=True)
User.favorite_items = db.relationship('FavoriteItem', backref='user', lazy=True)
User.watched_items = db.relationship('WatchedItem', backref='user', lazy=True)
User.ratings = db.relationship('Rating', backref='user', lazy=True)
Movie.ratings = db.relationship('Rating', backref='movie', lazy=True)
