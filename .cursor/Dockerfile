FROM python:3.11-slim

# Install system dependencies and development tools
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m -s /bin/bash ubuntu

# Add ubuntu user to docker group for Docker access
RUN usermod -aG docker ubuntu

# Switch to non-root user
USER ubuntu

# Set working directory to user's home directory
WORKDIR /home/ubuntu

# Pre-install common Python development tools
RUN pip install --no-cache-dir --user \
    pytest \
    httpx \
    docker

# Default command runs the network tests, but can be overridden
CMD ["python", "-m", "pytest", "test_network.py", "-v"]