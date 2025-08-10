#!/usr/bin/env python3
"""
Advanced ReqNinja examples demonstrating profiles and configuration.
"""

from reqninja import ReqNinjaClient, Config
from pathlib import Path
import tempfile
import yaml
import os


def create_sample_config():
    """Create a sample configuration for testing."""
    config_data = {
        'default_retries': 3,
        'default_timeout': 30,
        'default_headers': {
            'User-Agent': 'ReqNinja-Example/1.0'
        },
        'profiles': {
            'jsonplaceholder': {
                'base_url': 'https://jsonplaceholder.typicode.com',
                'headers': {
                    'Accept': 'application/json'
                }
            },
            'httpbin': {
                'base_url': 'https://httpbin.org',
                'headers': {
                    'X-Custom-Header': 'ReqNinja-Test'
                }
            }
        }
    }
    
    # Create temp config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        yaml.dump(config_data, f)
        return f.name


def example_with_profiles():
    """Example using configuration profiles."""
    print("=== Using Configuration Profiles ===")
    
    config_file = create_sample_config()
    
    try:
        # Create client with custom config
        config = Config(Path(config_file))
        client = ReqNinjaClient(config)
        
        # Use jsonplaceholder profile
        print("Using jsonplaceholder profile:")
        response = client.get("/posts/1", profile="jsonplaceholder")
        print(f"Status: {response.status_code}")
        print(f"URL: {response.url}")
        response.pretty_print()
        print()
        
        # Use httpbin profile
        print("Using httpbin profile:")
        response = client.get("/headers", profile="httpbin")
        print(f"Status: {response.status_code}")
        response.pretty_print()
        print()
        
    finally:
        # Cleanup
        os.unlink(config_file)


def example_authentication():
    """Example with authentication."""
    print("=== Authentication Example ===")
    
    # Bearer token authentication
    auth_config = {
        'type': 'bearer',
        'token': 'example-token-123'
    }
    
    client = ReqNinjaClient()
    response = client.get(
        "https://httpbin.org/bearer",
        auth=auth_config
    )
    
    print("Bearer token authentication:")
    print(f"Status: {response.status_code}")
    response.pretty_print()
    print()


def example_batch_requests():
    """Example of making multiple requests."""
    print("=== Batch Requests Example ===")
    
    client = ReqNinjaClient()
    urls = [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
        "https://jsonplaceholder.typicode.com/posts/3"
    ]
    
    responses = []
    total_time = 0
    
    for url in urls:
        response = client.get(url)
        responses.append(response)
        total_time += response.elapsed_ms
        print(f"✓ {url} - {response.status_code} ({response.elapsed_ms:.2f}ms)")
    
    print(f"\nCompleted {len(responses)} requests in {total_time:.2f}ms total")
    print(f"Average response time: {total_time/len(responses):.2f}ms")
    print()


def example_save_response():
    """Example of saving responses to files."""
    print("=== Save Response Example ===")
    
    client = ReqNinjaClient()
    response = client.get("https://jsonplaceholder.typicode.com/posts/1")
    
    # Save as JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        response.save(f.name, format='json')
        print(f"Response saved to: {f.name}")
        
        # Read it back
        with open(f.name, 'r') as rf:
            content = rf.read()
            print("Saved content preview:")
            print(content[:200] + "..." if len(content) > 200 else content)
        
        # Cleanup
        os.unlink(f.name)
    
    print()


def example_debug_mode():
    """Example of debug information."""
    print("=== Debug Mode Example ===")
    
    client = ReqNinjaClient()
    response = client.post(
        "https://httpbin.org/post",
        json={"message": "Hello ReqNinja!"},
        headers={"X-Debug": "true"}
    )
    
    print("Request details:")
    print(f"  URL: {response.url}")
    print(f"  Method: {response.request.method}")
    print(f"  Status: {response.status_code}")
    print(f"  Time: {response.elapsed_ms:.2f}ms")
    print()
    
    response.pretty_print(show_headers=True)
    print()


if __name__ == "__main__":
    print("ReqNinja Advanced Examples")
    print("=" * 50)
    
    example_with_profiles()
    example_authentication()
    example_batch_requests()
    example_save_response()
    example_debug_mode()
    
    print("Advanced examples completed!")
