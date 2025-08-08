#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Start the Flask application
gunicorn --bind 0.0.0.0:$PORT app:app
