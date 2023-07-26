#!/bin/bash


echo "Step [1/4] Collecting static files .."
python manage.py collectstatic --noinput

echo "Step [2/4] Applying database migrations .."
python manage.py migrate --noinput

echo "Step [3/4] Seeding database .."
python manage.py loaddata config/fixtures/super_users.json

echo "Step [4/4] Starting server"
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --reload --timeout 90 --log-level debug  --workers=5 --threads=5 --worker-class=gthread
