# Use an official Python base image
FROM python:3.14-slim

WORKDIR /app

# Copy dependencies early for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY app /app/app

# Expose the port your app runs on
EXPOSE 5000

# Run the application
CMD ["flask", "run" , "--host=0.0.0.0"]