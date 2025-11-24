# Use the slim image to keep things lightweight
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies required for building lxml and grpcio
# (This fixes the "pip install" compilation errors)
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Configuration
ENV PORT=8080
EXPOSE 8080
ENV FLASK_ENV=production

# Start the server
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
