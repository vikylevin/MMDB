#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start the Flask application
gunicorn --bind 0.0.0.0:$PORT app:app
