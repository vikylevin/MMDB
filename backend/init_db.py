#!/usr/bin/env python3
"""
Database initialization script for Render deployment
"""
import os
import sys
from app import app, db

def init_database():
    """Initialize the database tables"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            return True
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

if __name__ == '__main__':
    print("🔄 Initializing database...")
    
    # Check if DATABASE_URL is set
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL environment variable not set!")
        sys.exit(1)
    
    success = init_database()
    if not success:
        sys.exit(1)
    
    print("🎉 Database initialization completed!")
