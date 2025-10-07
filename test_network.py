"""
Hello World tests demonstrating:
1. External network calls from a container
2. Testcontainers spinning up services and making network calls to them
"""
import pytest
import httpx
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


def test_external_api_call():
    """Test that we can make network calls to external APIs."""
    
    # Make a call to a public API
    url = "https://httpbin.org/get"
    
    print(f"\n🚀 Making external network call to: {url}")
    
    # Make an external network call using httpx
    response = httpx.get(url, timeout=10.0)
    
    # Verify the response
    assert response.status_code == 200
    json_data = response.json()
    assert "headers" in json_data
    
    print(f"✅ Successfully made external network call!")
    print(f"📊 Response status: {response.status_code}")
    print(f"📝 Response has headers: {list(json_data['headers'].keys())[:3]}...")


def test_testcontainers_with_network_calls():
    """Test using testcontainers to spin up a service and make network calls to it."""
    
    print("\n🔧 Starting container with testcontainers...")
    
    # Use testcontainers to start an nginx container
    with DockerContainer("nginx:alpine") as container:
        container.with_exposed_ports(80)
        
        # Get the mapped port and host
        host = container.get_container_host_ip()
        port = container.get_exposed_port(80)
        url = f"http://{host}:{port}/"
        
        print(f"🐳 Container started at: {url}")
        
        # Make network call to the containerized service
        response = httpx.get(url, timeout=10.0)
        
        assert response.status_code == 200
        assert "nginx" in response.text.lower() or "welcome" in response.text.lower()
        
        print(f"✅ Successfully connected to testcontainer!")
        print(f"📊 Response status: {response.status_code}")
        print(f"📝 Response length: {len(response.text)} bytes")


def test_testcontainers_httpbin():
    """Test using testcontainers with httpbin for more complex interactions."""
    
    print("\n🔧 Starting httpbin container with testcontainers...")
    
    with DockerContainer("kennethreitz/httpbin") as container:
        container.with_exposed_ports(80)
        wait_for_logs(container, "Listening at:", timeout=30)
        
        host = container.get_container_host_ip()
        port = container.get_exposed_port(80)
        base_url = f"http://{host}:{port}"
        
        print(f"🐳 Httpbin container started at: {base_url}")
        
        # Test GET request
        get_response = httpx.get(f"{base_url}/get", timeout=10.0)
        assert get_response.status_code == 200
        print(f"  ✓ GET request successful")
        
        # Test POST request
        post_data = {"container": "test", "testcontainers": True}
        post_response = httpx.post(f"{base_url}/post", json=post_data, timeout=10.0)
        assert post_response.status_code == 200
        assert post_response.json()["json"] == post_data
        print(f"  ✓ POST request successful")
        
        print(f"✅ Testcontainer httpbin tests passed!")


def test_multiple_external_calls():
    """Test making multiple external network calls."""
    
    urls = [
        "https://httpbin.org/uuid",
        "https://httpbin.org/json",
        "https://httpbin.org/user-agent",
    ]
    
    print(f"\n🔄 Testing multiple external network calls")
    
    # Make multiple requests to different endpoints
    for i, url in enumerate(urls, 1):
        response = httpx.get(url, timeout=10.0)
        assert response.status_code == 200
        print(f"  ✓ Request {i}/{len(urls)} to {url.split('/')[-1]} successful")
    
    print("✅ All external network calls completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

