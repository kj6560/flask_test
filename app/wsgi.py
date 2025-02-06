import sys
import os

# Ensure the app's directory is in the system path
sys.path.insert(0, os.path.dirname(__file__))

from app import myapp  # Import your Flask app instance

app = myapp  # Correctly assign the Flask app for WSGI
