FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy test files
COPY . .

# Environment variables for testcontainers
ENV DOCKER_HOST=unix:///var/run/docker.sock

# Run tests
CMD ["pytest", "-v", "-s", "test_network.py"]

