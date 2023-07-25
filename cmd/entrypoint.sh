#!/bin/bash

# Start server
echo "Starting server"
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --reload --timeout 90 --log-level debug  --workers=5 --threads=5 --worker-class=gthread
