# Use the standard Python 3.10 image
# (Not 'slim', so it includes C++ compilers if needed, and '3.10' has pre-built wheels)
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# 1. Upgrade pip to the latest version
# 2. Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Configuration
ENV PORT=8080
EXPOSE 8080
ENV FLASK_ENV=production

# Start the server
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app