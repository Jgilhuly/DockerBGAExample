#!/usr/bin/env python3
"""
Docker Agent Demo Script

This script demonstrates how a background agent can use Docker programmatically
to perform common containerization tasks. It shows both CLI commands via subprocess
and Python Docker library usage.
"""

import subprocess
import sys
import time
import json
from pathlib import Path
import docker
import httpx


def run_command(cmd, capture_output=True, check=True):
    """Run a shell command and return the result."""
    print(f"🔧 Running: {cmd}")
    try:
        result = subprocess.run(
            cmd.split() if isinstance(cmd, str) else cmd,
            capture_output=capture_output,
            text=True,
            check=check
        )
        if capture_output and result.stdout:
            print(f"✅ Output: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        if capture_output and e.stderr:
            print(f"❌ Error: {e.stderr.strip()}")
        raise


def demo_docker_cli_commands():
    """Demonstrate Docker CLI usage via subprocess."""
    print("\n" + "="*50)
    print("🐳 DOCKER CLI COMMANDS DEMO")
    print("="*50)
    
    # Check Docker version
    print("\n📋 Checking Docker version...")
    run_command("docker --version")
    
    # List current containers
    print("\n📦 Listing current containers...")
    run_command("docker ps -a")
    
    # List current images
    print("\n🖼️  Listing current images...")
    run_command("docker images")
    
    # Pull a lightweight image
    print("\n⬇️  Pulling Alpine Linux image...")
    run_command("docker pull alpine:latest")
    
    # Run a simple container
    print("\n🚀 Running a simple Alpine container...")
    result = run_command("docker run --rm alpine:latest echo 'Hello from Docker container!'")
    
    # Create and run a container with networking
    print("\n🌐 Running container with network test...")
    run_command([
        "docker", "run", "--rm", 
        "alpine:latest", "sh", "-c", 
        "ping -c 3 google.com || echo 'Network test complete'"
    ])


def demo_python_docker_library():
    """Demonstrate Docker Python library usage."""
    print("\n" + "="*50)
    print("🐍 PYTHON DOCKER LIBRARY DEMO")
    print("="*50)
    
    # Initialize Docker client
    print("\n🔌 Connecting to Docker daemon...")
    try:
        client = docker.from_env()
        print(f"✅ Connected to Docker daemon")
        
        # Get Docker info
        info = client.info()
        print(f"📊 Docker version: {info['ServerVersion']}")
        print(f"📊 Total containers: {info['Containers']}")
        print(f"📊 Running containers: {info['ContainersRunning']}")
        
    except Exception as e:
        print(f"❌ Failed to connect to Docker daemon: {e}")
        return
    
    # List images
    print("\n🖼️  Listing images with Python client...")
    images = client.images.list()
    for image in images[:5]:  # Just show first 5
        tags = image.tags[0] if image.tags else '<none>'
        print(f"  📦 {tags} ({image.short_id})")
    
    # Pull an image
    print("\n⬇️  Pulling nginx:alpine image...")
    try:
        image = client.images.pull("nginx:alpine")
        print(f"✅ Pulled image: {image.tags[0]} ({image.short_id})")
    except Exception as e:
        print(f"⚠️  Image pull issue: {e}")
    
    # Run a container
    print("\n🚀 Creating and running nginx container...")
    try:
        container = client.containers.run(
            "nginx:alpine",
            name="agent-demo-nginx",
            ports={'80/tcp': None},  # Let Docker assign a random port
            detach=True,
            remove=True  # Auto-remove when stopped
        )
        
        # Wait for container to start
        time.sleep(2)
        container.reload()
        
        print(f"✅ Container started: {container.name} ({container.short_id})")
        print(f"📊 Status: {container.status}")
        
        # Get container info
        port_info = container.ports.get('80/tcp')
        if port_info:
            host_port = port_info[0]['HostPort']
            print(f"🌐 Nginx available on port: {host_port}")
            
            # Try to make a request to the container
            try:
                response = httpx.get(f"http://localhost:{host_port}", timeout=5.0)
                print(f"✅ HTTP request successful! Status: {response.status_code}")
            except Exception as e:
                print(f"ℹ️  HTTP request info: {e}")
        
        # Stop and remove container
        print(f"⏹️  Stopping container...")
        container.stop()
        print(f"✅ Container stopped and removed")
        
    except Exception as e:
        print(f"❌ Container operation failed: {e}")


def demo_container_management():
    """Demonstrate container lifecycle management."""
    print("\n" + "="*50)
    print("🔄 CONTAINER LIFECYCLE MANAGEMENT DEMO")
    print("="*50)
    
    client = docker.from_env()
    
    # Create a simple container that runs in background
    print("\n🚀 Creating a long-running container...")
    try:
        container = client.containers.run(
            "alpine:latest",
            command="sh -c 'while true; do echo Hello Agent $(date); sleep 5; done'",
            name="agent-demo-worker",
            detach=True
        )
        
        print(f"✅ Container created: {container.name} ({container.short_id})")
        
        # Monitor container for a bit
        print("📊 Monitoring container logs...")
        time.sleep(8)
        
        # Get logs
        logs = container.logs(tail=3).decode('utf-8')
        print(f"📝 Recent logs:\n{logs}")
        
        # Get container stats
        container.reload()
        print(f"📊 Container status: {container.status}")
        
        # Stop the container
        print("⏹️  Stopping container...")
        container.stop()
        
        # Remove the container
        print("🗑️  Removing container...")
        container.remove()
        
        print("✅ Container lifecycle completed")
        
    except Exception as e:
        print(f"❌ Container management failed: {e}")
        # Cleanup in case of error
        try:
            cleanup_container = client.containers.get("agent-demo-worker")
            cleanup_container.remove(force=True)
            print("🧹 Cleanup completed")
        except:
            pass


def demo_image_operations():
    """Demonstrate image operations."""
    print("\n" + "="*50)
    print("🖼️  IMAGE OPERATIONS DEMO")
    print("="*50)
    
    client = docker.from_env()
    
    # Build a simple image from a Dockerfile string
    print("\n🏗️  Building a custom image...")
    
    dockerfile_content = """
FROM alpine:latest
RUN echo "This is a demo image built by agent" > /demo.txt
CMD cat /demo.txt
"""
    
    try:
        # Create temporary dockerfile
        temp_dockerfile = Path("/tmp/agent_demo_dockerfile")
        temp_dockerfile.write_text(dockerfile_content)
        
        # Build image
        image, build_logs = client.images.build(
            path="/tmp",
            dockerfile="agent_demo_dockerfile",
            tag="agent-demo:latest",
            rm=True
        )
        
        print(f"✅ Image built: {image.tags[0]} ({image.short_id})")
        
        # Run container from our custom image
        print("🚀 Running container from custom image...")
        result = client.containers.run(
            "agent-demo:latest",
            remove=True
        )
        print(f"📝 Container output: {result.decode('utf-8').strip()}")
        
        # Clean up the image
        print("🗑️  Removing custom image...")
        client.images.remove("agent-demo:latest", force=True)
        
        # Clean up temp file
        temp_dockerfile.unlink()
        
        print("✅ Image operations completed")
        
    except Exception as e:
        print(f"❌ Image operations failed: {e}")


def main():
    """Main demo function."""
    print("🤖 DOCKER AGENT DEMONSTRATION")
    print("This script shows how background agents can use Docker")
    print("=" * 60)
    
    try:
        # Check if Docker is available
        run_command("docker info", capture_output=False)
        print("✅ Docker is available and running")
        
        # Run all demos
        demo_docker_cli_commands()
        demo_python_docker_library()
        demo_container_management()
        demo_image_operations()
        
        print("\n" + "="*60)
        print("🎉 ALL DOCKER AGENT DEMOS COMPLETED SUCCESSFULLY!")
        print("🤖 Background agents can now use these patterns for:")
        print("   • Container lifecycle management")
        print("   • Image building and deployment")
        print("   • Service orchestration")
        print("   • Development environment setup")
        print("   • Testing and CI/CD operations")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("🔧 Make sure Docker is installed and running")
        print("🔧 Make sure Docker socket is accessible")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
