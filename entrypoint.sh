#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting server..."
exec gunicorn acessmentAi.wsgi:application --bind 0.0.0.0:8000
