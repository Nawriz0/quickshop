#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Checking project structure..."
ls -la
pwd

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

echo "Build completed successfully!" 