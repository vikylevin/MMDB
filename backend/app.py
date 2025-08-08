import os
from datetime import timedelta
from flask import Flask, request, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from models import db

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS for different environments  
allowed_origins = ["https://mmdb-web.onrender.com"]

# Add localhost for development if not in production
if os.getenv('FLASK_ENV') == 'development':
    allowed_origins.append("http://localhost:5173")

# Always add frontend URL if it's set and not already in the list
frontend_url = os.getenv('FRONTEND_URL')
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

# For production, ensure production URL is always included
production_frontend = "https://mmdb-web.onrender.com"
if production_frontend not in allowed_origins:
    allowed_origins.append(production_frontend)

print(f"CORS allowed origins: {allowed_origins}")

CORS(
    app,
    supports_credentials=True,
    origins=allowed_origins,
    allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Headers", "Origin", "Accept", "X-Requested-With"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    expose_headers=["Content-Range", "X-Content-Range"],
    send_wildcard=False,
    vary_header=True
)

# Configure Flask app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-super-secret-key')
# Use production database by default, fallback to localhost for development
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://movies_user:jfR7w5dDKVkAqUBVnYa8JZKIAV8K2WXk@dpg-d2b3c4umcj7s73e51pag-a.virginia-postgres.render.com/movie_db_2vtg')
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

# Add a global OPTIONS handler for CORS preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        origin = request.headers.get('Origin')
        # Check if origin is in allowed list
        if origin in allowed_origins:
            response.headers.add("Access-Control-Allow-Origin", origin)
        else:
            # For debugging - always allow in development
            response.headers.add("Access-Control-Allow-Origin", "https://mmdb-web.onrender.com")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

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
