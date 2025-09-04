"""
Unit tests for Flask API routes
"""
import unittest
import json
import os
from unittest.mock import patch, Mock
from flask import Flask
from flask_jwt_extended import JWTManager
from models import db, User, Movie, Rating, Review


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
    jwt = JWTManager(app)
    
    # Import and register blueprints
    from routes import auth_bp, movie_bp, user_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(movie_bp, url_prefix='/api/movie')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    return app


class TestMovieAPI(unittest.TestCase):
    """Test cases for movie API endpoints"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create test Flask app
        self.app = create_test_app()
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test user
            self.test_user = User(
                username='testuser',
                email='test@example.com'
            )
            self.test_user.set_password('testpassword')
            db.session.add(self.test_user)
            
            # Create test movie
            self.test_movie = Movie(
                tmdb_id=550,
                title='Fight Club',
                overview='A ticking-time-bomb insomniac...',
                vote_average=8.4,
                poster_path='/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg'
            )
            db.session.add(self.test_movie)
            db.session.commit()
    
    def tearDown(self):
        """Clean up after each test method"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def get_auth_token(self):
        """Helper method to get JWT token for authenticated requests"""
        response = self.client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })
        data = json.loads(response.data)
        return data.get('access_token')

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/movie/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')

    @patch('routes.requests.get')
    def test_get_popular_movies(self, mock_get):
        """Test popular movies endpoint"""
        # Arrange
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'page': 1,
            'results': [
                {
                    'id': 550,
                    'title': 'Fight Club',
                    'vote_average': 8.4
                }
            ],
            'total_results': 1
        }
        mock_get.return_value = mock_response
        
        # Act
        response = self.client.get('/api/movie/popular')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)

    @patch('routes.requests.get')
    def test_search_movies(self, mock_get):
        """Test movie search endpoint"""
        # Arrange
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'page': 1,
            'results': [
                {
                    'id': 550,
                    'title': 'Fight Club',
                    'vote_average': 8.4
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Act
        response = self.client.get('/api/movie/search?query=Fight Club')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('results', data)

    def test_rate_movie_unauthorized(self):
        """Test rating a movie without authentication"""
        response = self.client.post('/api/movie/550/rate', json={
            'rating': 4
        })
        self.assertEqual(response.status_code, 401)

    def test_rate_movie_authorized(self):
        """Test rating a movie with authentication"""
        # Get auth token
        token = self.get_auth_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Rate the movie
        with patch('routes.fetch_movie_details') as mock_fetch:
            mock_fetch.return_value = {
                'id': 550,
                'title': 'Fight Club',
                'overview': 'Test overview',
                'poster_path': '/test.jpg',
                'vote_average': 8.4
            }
            
            response = self.client.post('/api/movie/550/rate', 
                                      json={'rating': 4},
                                      headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['rating'], 4)

    def test_get_movie_rating_unauthorized(self):
        """Test getting movie rating without authentication"""
        response = self.client.get('/api/movie/550/rating')
        self.assertEqual(response.status_code, 401)

    def test_invalid_rating_value(self):
        """Test rating a movie with invalid rating value"""
        token = self.get_auth_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test rating too high
        response = self.client.post('/api/movie/550/rate',
                                  json={'rating': 6},
                                  headers=headers)
        self.assertEqual(response.status_code, 400)
        
        # Test negative rating
        response = self.client.post('/api/movie/550/rate',
                                  json={'rating': -1},
                                  headers=headers)
        self.assertEqual(response.status_code, 400)


class TestUserAPI(unittest.TestCase):
    """Test cases for user authentication and profile endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_test_app()
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_registration(self):
        """Test user registration endpoint"""
        response = self.client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123'
        })
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertIn('user', data)

    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username"""
        # Register first user
        self.client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test1@example.com',
            'password': 'password123'
        })
        
        # Try to register with same username
        response = self.client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'password456'
        })
        
        self.assertEqual(response.status_code, 400)

    def test_user_login_success(self):
        """Test successful user login"""
        # Register user first
        self.client.post('/api/auth/register', json={
            'username': 'loginuser',
            'email': 'login@example.com',
            'password': 'loginpass123'
        })
        
        # Login
        response = self.client.post('/api/auth/login', json={
            'username': 'loginuser',
            'password': 'loginpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
