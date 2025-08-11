#!/usr/bin/env python3
"""
Basic ReqNinja examples demonstrating core functionality.
"""

from reqninja import get, post, put, delete
import json


def example_get_request():
    """Example of making a GET request."""
    print("=== GET Request Example ===")
    
    response = get("https://jsonplaceholder.typicode.com/posts/1")
    
    print(f"Status: {response.status_code}")
    print(f"Time: {response.elapsed_ms:.2f}ms")
    print("Response:")
    response.pretty_print()
    print()


def example_post_request():
    """Example of making a POST request with JSON data."""
    print("=== POST Request Example ===")
    
    data = {
        "title": "ReqNinja Test",
        "body": "This is a test post from ReqNinja",
        "userId": 1
    }
    
    response = post(
        "https://jsonplaceholder.typicode.com/posts",
        json=data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Time: {response.elapsed_ms:.2f}ms")
    print("Response:")
    response.pretty_print()
    print()


def example_with_headers():
    """Example with custom headers."""
    print("=== Request with Custom Headers ===")
    
    headers = {
        "User-Agent": "ReqNinja-Example/1.0",
        "Accept": "application/json"
    }
    
    response = get(
        "https://httpbin.org/headers",
        headers=headers
    )
    
    response.pretty_print()
    print()


def example_error_handling():
    """Example of error handling."""
    print("=== Error Handling Example ===")
    
    try:
        response = get("https://httpbin.org/status/404")
        print(f"Status: {response.status_code}")
        
        if response.status_code >= 400:
            print("Request failed!")
            response.pretty_print()
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def example_timeout_and_retries():
    """Example with timeout and retry configuration."""
    print("=== Timeout and Retries Example ===")
    
    response = get(
        "https://httpbin.org/delay/1",
        timeout=5,
        retries=2
    )
    
    print(f"Status: {response.status_code}")
    print(f"Time: {response.elapsed_ms:.2f}ms")
    print()


if __name__ == "__main__":
    print("ReqNinja Basic Examples")
    print("=" * 50)
    
    example_get_request()
    example_post_request()
    example_with_headers()
    example_error_handling()
    example_timeout_and_retries()
    
    print("Examples completed!")
