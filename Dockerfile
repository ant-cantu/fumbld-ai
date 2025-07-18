# Dockerfile
FROM python:3.11.9-slim

# Set working directory
WORKDIR /app

# Install certs and system dependencies
RUN apt-get update && apt-get install -y curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./source /app

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Start with Gunicorn
CMD ["gunicorn", "--workers=5", "--timeout=90", "--bind=0.0.0.0:8000", "app:app"]