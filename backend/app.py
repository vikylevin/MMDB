import os
from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from models import db

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS for different environments
allowed_origins = ["http://localhost:5173"]
if os.getenv('FLASK_ENV') == 'production':
    frontend_url = os.getenv('FRONTEND_URL', 'https://movie-review-frontend.onrender.com')
    allowed_origins.append(frontend_url)

CORS(
    app,
    supports_credentials=True,
    origins=allowed_origins,
    allow_headers=["Content-Type", "Authorization"]
)

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

db.init_app(app)
jwt = JWTManager(app)

# Import and register blueprints
from routes import user_bp, auth_bp, movie_bp
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(movie_bp, url_prefix='/api/movie')

# Create tables only when running directly (not during import)
def create_tables():
    """Create database tables if they don't exist"""
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    print('Registered routes:')
    for rule in app.url_map.iter_rules():
        print(f"{rule}")
    app.run(debug=True)
