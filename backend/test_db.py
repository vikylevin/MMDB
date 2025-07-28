import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get database URL from environment
database_url = os.getenv('DATABASE_URL')
print(f"Trying to connect with URL: {database_url}")

try:
    # Try to connect
    conn = psycopg2.connect(database_url)
    print("Successfully connected to the database!")
    
    # Create a cursor
    cur = conn.cursor()
    
    # Execute a simple query
    cur.execute("SELECT version();")
    
    # Fetch the result
    version = cur.fetchone()
    print(f"PostgreSQL version: {version[0]}")
    
    # Close cursor and connection
    cur.close()
    conn.close()
    print("Connection closed successfully!")
    
except Exception as e:
    print(f"An error occurred: {str(e)}")
