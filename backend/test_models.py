"""
Unit tests for database models
"""
import unittest
import os
from datetime import datetime
from werkzeug.security import check_password_hash
from flask import Flask
from flask_jwt_extended import JWTManager
from models import db, User, Movie, Rating, Review, WatchLaterItem, LikedItem


def create_test_app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Initialize extensions
    db.init_app(app)
    JWTManager(app)
    
    return app


class TestDatabaseModels(unittest.TestCase):
    """Test cases for database models"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_test_app()
        
        with self.app.app_context():
            db.create_all()
            
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_model_creation(self):
        """Test User model creation and password hashing"""
        with self.app.app_context():
            # Create user
            user = User(
                username='testuser',
                email='test@example.com'
            )
            user.set_password('testpassword123')
            
            db.session.add(user)
            db.session.commit()
            
            # Verify user creation
            saved_user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(saved_user)
            self.assertEqual(saved_user.email, 'test@example.com')
            
            # Verify password hashing
            self.assertTrue(saved_user.check_password('testpassword123'))
            self.assertFalse(saved_user.check_password('wrongpassword'))
            
            # Verify password is hashed
            self.assertNotEqual(saved_user.password_hash, 'testpassword123')

    def test_user_unique_constraints(self):
        """Test user unique constraints for username and email"""
        with self.app.app_context():
            # Create first user
            user1 = User(username='user1', email='user1@example.com')
            user1.set_password('password123')
            db.session.add(user1)
            db.session.commit()
            
            # Try to create user with same username
            user2 = User(username='user1', email='different@example.com')
            user2.set_password('password456')
            db.session.add(user2)
            
            with self.assertRaises(Exception):
                db.session.commit()
            
            db.session.rollback()
            
            # Try to create user with same email
            user3 = User(username='different', email='user1@example.com')
            user3.set_password('password789')
            db.session.add(user3)
            
            with self.assertRaises(Exception):
                db.session.commit()

    def test_movie_model_creation(self):
        """Test Movie model creation"""
        with self.app.app_context():
            movie = Movie(
                tmdb_id=550,
                title='Fight Club',
                overview='A ticking-time-bomb insomniac...',
                poster_path='/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg',
                vote_average=8.4
            )
            
            db.session.add(movie)
            db.session.commit()
            
            # Verify movie creation
            saved_movie = Movie.query.filter_by(tmdb_id=550).first()
            self.assertIsNotNone(saved_movie)
            self.assertEqual(saved_movie.title, 'Fight Club')
            self.assertEqual(saved_movie.vote_average, 8.4)

    def test_rating_model_creation(self):
        """Test Rating model creation and relationships"""
        with self.app.app_context():
            # Create user and movie
            user = User(username='rater', email='rater@example.com')
            user.set_password('password123')
            db.session.add(user)
            
            movie = Movie(
                tmdb_id=550,
                title='Fight Club',
                vote_average=8.4
            )
            db.session.add(movie)
            db.session.commit()
            
            # Create rating
            rating = Rating(
                user_id=user.id,
                movie_id=movie.id,
                rating=4
            )
            db.session.add(rating)
            db.session.commit()
            
            # Verify rating creation
            saved_rating = Rating.query.filter_by(user_id=user.id, movie_id=movie.id).first()
            self.assertIsNotNone(saved_rating)
            self.assertEqual(saved_rating.rating, 4)

    def test_review_model_creation(self):
        """Test Review model creation"""
        with self.app.app_context():
            # Create user and movie
            user = User(username='reviewer', email='reviewer@example.com')
            user.set_password('password123')
            db.session.add(user)
            
            movie = Movie(
                tmdb_id=550,
                title='Fight Club',
                vote_average=8.4
            )
            db.session.add(movie)
            db.session.commit()
            
            # Create review
            review = Review(
                user_id=user.id,
                movie_id=movie.id,
                rating=5,
                comment='Great movie!'
            )
            db.session.add(review)
            db.session.commit()
            
            # Verify review creation
            saved_review = Review.query.filter_by(user_id=user.id, movie_id=movie.id).first()
            self.assertIsNotNone(saved_review)
            self.assertEqual(saved_review.comment, 'Great movie!')
            self.assertEqual(saved_review.rating, 5)

    def test_watch_later_model(self):
        """Test WatchLaterItem model"""
        with self.app.app_context():
            # Create user
            user = User(username='watcher', email='watcher@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Create watch later item
            watch_item = WatchLaterItem(
                user_id=user.id,
                movie_id=550  # TMDB ID
            )
            db.session.add(watch_item)
            db.session.commit()
            
            # Verify creation
            saved_item = WatchLaterItem.query.filter_by(user_id=user.id, movie_id=550).first()
            self.assertIsNotNone(saved_item)
            self.assertEqual(saved_item.movie_id, 550)

    def test_liked_item_model(self):
        """Test LikedItem model"""
        with self.app.app_context():
            # Create user
            user = User(username='liker', email='liker@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Create liked item
            liked_item = LikedItem(
                user_id=user.id,
                movie_id=550  # TMDB ID
            )
            db.session.add(liked_item)
            db.session.commit()
            
            # Verify creation
            saved_item = LikedItem.query.filter_by(user_id=user.id, movie_id=550).first()
            self.assertIsNotNone(saved_item)
            self.assertEqual(saved_item.movie_id, 550)

    def test_model_timestamps(self):
        """Test automatic timestamp creation"""
        with self.app.app_context():
            # Create a rating to test timestamps
            user = User(username='timetest', email='time@example.com')
            user.set_password('password123')
            db.session.add(user)
            
            movie = Movie(
                tmdb_id=550,
                title='Fight Club',
                vote_average=8.4
            )
            db.session.add(movie)
            db.session.commit()
            
            rating = Rating(
                user_id=user.id,
                movie_id=movie.id,
                rating=4
            )
            db.session.add(rating)
            db.session.commit()
            
            # Check that created_at is set
            self.assertIsNotNone(rating.created_at)
            self.assertIsInstance(rating.created_at, datetime)


if __name__ == '__main__':
    unittest.main()
