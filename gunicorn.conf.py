import os
import multiprocessing
import sys

# Bind to 0.0.0.0 to make the server accessible from outside
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Number of worker processes
workers = 2
threads = 2

# Set the Python path to include the project directory
base_dir = os.getenv('RENDER_PROJECT_DIR', os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)

# Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuickShop.settings')

# The WSGI application to use
wsgi_app = 'QuickShop.wsgi:application'

# Log level
loglevel = 'debug'

# Access log format
accesslog = '-'
errorlog = '-'

# Preload application for better performance
preload_app = True

# Set working directory
chdir = base_dir 