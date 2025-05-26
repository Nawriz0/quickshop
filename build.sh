#!/usr/bin/env bash
# exit on error
set -o errexit

# Установка зависимостей
pip install -r requirements.txt

# Очистка старых статических файлов
python manage.py collectstatic --no-input --clear

# Копируем базу данных в /data если мы на Render
if [ -n "$RENDER" ]; then
    mkdir -p /data
    cp db.sqlite3 /data/db.sqlite3 || true
fi

# Миграции базы данных
python manage.py migrate 