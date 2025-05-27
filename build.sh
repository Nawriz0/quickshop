#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Checking project structure..."
ls -la
pwd
echo "Python path:"
python -c "import sys; print('\n'.join(sys.path))"
echo "Current directory contents:"
ls -R

echo "Creating necessary directories..."
mkdir -p staticfiles media

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "Setting up database directory..."
if [ -n "$RENDER" ]; then
    mkdir -p /data
    # Копируем базу данных только если она существует и /data пустой
    if [ -f db.sqlite3 ] && [ ! -f /data/db.sqlite3 ]; then
        cp db.sqlite3 /data/db.sqlite3
    fi
fi

echo "Running database migrations..."
python manage.py migrate

echo "Testing WSGI application..."
PYTHONPATH=$PYTHONPATH:$PWD python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuickShop.settings')
from QuickShop.wsgi import application
print('WSGI application loaded successfully')
"

echo "Testing gunicorn configuration..."
python -c "
import gunicorn.config
cfg = gunicorn.config.Config()
cfg.set('config', 'gunicorn.conf.py')
print('Gunicorn configuration loaded successfully')
"

echo "Build completed successfully!" 