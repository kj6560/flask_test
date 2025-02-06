import sys
import site
import os

# Path to your virtual environment
venv_path = "/var/www/shiwkesh/nudity/venv"

# Add site-packages of the virtualenv
site.addsitedir(f"{venv_path}/lib/python3.10/site-packages")

# Activate the virtual environment
sys.path.insert(0, "/var/www/shiwkesh/nudity")
sys.path.insert(0, venv_path)
os.environ["PYTHONHOME"] = venv_path
os.environ["PYTHONPATH"] = f"{venv_path}/lib/python3.10/site-packages"

# Import Flask app
from app import myapp as application