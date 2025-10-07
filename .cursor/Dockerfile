FROM python:3.11-slim

# Install system dependencies and development tools
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m -s /bin/bash ubuntu

# Switch to non-root user
USER ubuntu

# Set working directory to user's home directory
WORKDIR /home/ubuntu

# Pre-install common Python development tools
RUN pip install --no-cache-dir --user \
    pytest \
    httpx