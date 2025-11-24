# Use the standard Python image (includes build tools for lxml)
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8080 (Standard for Google Cloud Run / many PaaS)
ENV PORT=8080
EXPOSE 8080

# Define environment variable for production
ENV FLASK_ENV=production

# Run gunicorn when the container launches
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app