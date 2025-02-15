import os

# Get the backend URL from environment variable, with a fallback for local development
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000') 