#!/usr/bin/env python3
"""
Database initialization script for Render deployment
"""
import os
import sys
from app import app, db

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = ['DATABASE_URL', 'SECRET_KEY', 'TMDB_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL')[:50]}...")  # Show first 50 chars only
    return True

def init_database():
    """Initialize the database tables"""
    try:
        with app.app_context():
            # Test database connection first
            print("🔄 Testing database connection...")
            db.engine.execute("SELECT 1")
            print("✅ Database connection successful!")
            
            # Create all tables
            print("🔄 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            return True
    except Exception as e:
        print(f"❌ Error with database: {e}")
        return False

if __name__ == '__main__':
    print("🔄 Initializing database...")
    
    if not check_environment():
        sys.exit(1)
    
    success = init_database()
    if not success:
        sys.exit(1)
    
    print("🎉 Database initialization completed!")
