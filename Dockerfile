# Dockerfile
FROM python:3.11.9-slim

# Set working directory
WORKDIR /app

# Install certs, cron, and system dependencies
RUN apt-get update && apt-get install -y curl ca-certificates cron && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./source /app

# Set up cron job - FIXED: Set permissions after copying files
RUN chmod +x /app/run_nightly_jobs.sh
RUN chmod +x /app/start.sh
RUN crontab /app/crontab

# Create log file for cron jobs
RUN touch /var/log/nightly_jobs.log

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Start with startup script that runs both cron and Gunicorn
CMD ["/app/start.sh"]