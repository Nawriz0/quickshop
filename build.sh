#!/usr/bin/env bash
# exit on error
set -o errexit

# Установка зависимостей
pip install -r requirements.txt

# Очистка старых статических файлов
python manage.py collectstatic --no-input --clear

# Миграции базы данных
python manage.py migrate 