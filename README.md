# Container Network Testing with Testcontainers - Hello World

This is a hello world example demonstrating:
1. Running tests inside a container that make external network calls
2. Using testcontainers to spin up services and make network calls to them

## What This Does

- Runs pytest inside a Docker/Podman container
- Uses testcontainers to spin up nginx and httpbin containers
- Makes HTTP requests to containerized services
- Makes HTTP requests to external APIs (httpbin.org)
- Validates all responses
- Demonstrates full container networking capabilities

## Prerequisites

- Docker or Podman installed
- Docker/Podman socket accessible

## Running Tests Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest -v test_network.py
```

## Running Tests in Container

### Using Podman

```bash
# Build the image
podman build -t network-test-demo .

# Run tests (mount socket for testcontainers)
podman run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock:z \
  network-test-demo
```

### Using Docker

```bash
# Build the image
docker build -t network-test-demo .

# Run tests (mount socket for testcontainers)
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  network-test-demo
```

## What's Being Tested

1. **test_external_api_call**: Makes a GET request to external httpbin.org API
2. **test_testcontainers_with_network_calls**: Uses testcontainers to spin up nginx and makes HTTP requests to it
3. **test_testcontainers_httpbin**: Uses testcontainers to spin up httpbin locally, makes GET and POST requests
4. **test_multiple_external_calls**: Makes multiple GET requests to different external endpoints

## Architecture

```
┌──────────────────────────────────────────────────┐
│   Test Container (Python)                        │
│   - pytest                                       │
│   - testcontainers library                       │
│   - httpx for HTTP requests                      │
│                                                  │
│   ┌────────────────────────────────────────┐    │
│   │  Test Code                             │    │
│   │  1. Starts → Nginx/Httpbin Container   │    │
│   │     (via testcontainers)               │    │
│   │  2. Makes → HTTP requests to container │    │
│   │  3. Makes → External API calls         │    │
│   │  4. Verifies → All responses           │    │
│   └────────────────────────────────────────┘    │
└────────────┬─────────────────────────────────────┘
             ↓ (via Docker socket)
┌────────────┴─────────────────────────────────────┐
│   Docker/Podman Runtime                          │
│   ┌──────────────┐  ┌──────────────┐            │
│   │ Nginx        │  │ Httpbin      │            │
│   │ Container    │  │ Container    │            │
│   └──────────────┘  └──────────────┘            │
└──────────────────────────────────────────────────┘
             ↓ (HTTP/HTTPS to internet)
      ┌──────────────┐
      │   Internet   │
      │ httpbin.org  │
      └──────────────┘
```

## Troubleshooting

### Network Connectivity Issues

If you get connection errors:

```bash
# Test basic connectivity from the container
docker run --rm network-test-demo curl -I https://httpbin.org

# Or test DNS resolution
docker run --rm network-test-demo ping -c 3 httpbin.org
```

### Socket Permission Issues

If you get socket permission errors:

```bash
# Check socket permissions
ls -la /var/run/docker.sock

# Or run with appropriate permissions
sudo docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  network-test-demo
```

### Firewall Issues

If your network has a firewall, ensure outbound HTTPS connections are allowed.

## Notes

- Testcontainers requires access to the Docker/Podman socket
- The socket mount (`-v /var/run/docker.sock:/var/run/docker.sock`) allows the test container to spawn sibling containers
- Tests demonstrate both testcontainers (local) and external network calls
- The `-s` flag in pytest shows print statements during test execution
- The `:z` flag in Podman volume mounts is important for SELinux systems

