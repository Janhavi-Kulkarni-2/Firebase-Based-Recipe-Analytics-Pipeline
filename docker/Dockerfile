# Base image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Copy project files into the container
COPY ../Project /app/Project

# Install Python packages
RUN pip install --no-cache-dir pandas python-dateutil firebase-admin matplotlib numpy

# Install cron
RUN apt-get update && apt-get install -y cron

# Create logs folder and give write permissions
RUN mkdir -p /app/logs
RUN chmod 777 /app/logs

# Copy cron schedule file
COPY crontab.txt /etc/cron.d/pipeline-cron

# Give execution rights to cron file
RUN chmod 0644 /etc/cron.d/pipeline-cron

# Apply cron job
RUN crontab /etc/cron.d/pipeline-cron

# Run cron in foreground (for debugging)
CMD cron -f
