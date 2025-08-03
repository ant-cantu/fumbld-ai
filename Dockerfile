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

# Create a modified crontab that uses bash explicitly
RUN echo "0 0 * * * /bin/bash /app/run_nightly_jobs.sh >> /var/log/nightly_jobs.log 2>&1" > /app/crontab_bash && \
    crontab /app/crontab_bash

# Create log file for cron jobs
RUN touch /var/log/nightly_jobs.log

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Start with bash explicitly
CMD ["/bin/bash", "/app/start.sh"]