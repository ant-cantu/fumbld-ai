#!/bin/bash

# Start cron daemon in background
echo "Starting cron daemon..."
service cron start

# Start the main application
echo "Starting Gunicorn application..."
exec gunicorn --workers=5 --timeout=90 --bind=0.0.0.0:8000 app:app
