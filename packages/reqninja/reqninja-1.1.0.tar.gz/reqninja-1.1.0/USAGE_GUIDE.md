# ReqNinja Usage Guide

## 🔧 Installation

### Option 1: From PyPI (Recommended)
```bash
pip install reqninja
```

### Option 2: From Source
```bash
git clone https://github.com/vishal-ravi/reqninja.git
cd reqninja
pip install -e .
```

### Option 3: Development Setup
```bash
git clone https://github.com/vishal-ravi/reqninja.git
cd reqninja
python setup_dev.py
```

## 🖥️ CLI Usage Examples

### Basic HTTP Requests
```bash
# Simple GET request
reqninja http get https://api.github.com

# GET with pretty JSON output (default)
reqninja http get https://jsonplaceholder.typicode.com/posts/1

# POST with JSON data
reqninja http post https://httpbin.org/post -j '{"name": "John", "age": 30}'

# PUT request
reqninja http put https://httpbin.org/put -j '{"id": 1, "name": "Updated"}'

# DELETE request
reqninja http delete https://httpbin.org/delete
```

### Authentication
```bash
# Bearer token
reqninja http get https://api.github.com/user --auth "bearer YOUR_TOKEN"

# Basic authentication
reqninja http get https://httpbin.org/basic-auth/user/pass --auth "basic user:pass"

# API key (will be sent as Authorization header)
reqninja http get https://api.example.com/data --auth "bearer your-api-key"
```

### Custom Headers
```bash
# Single header
reqninja http get https://httpbin.org/headers -H "X-Custom-Header: MyValue"

# Multiple headers
reqninja http post https://api.example.com/data \
  -H "Content-Type: application/json" \
  -H "X-API-Version: v2" \
  -H "X-Client: ReqNinja" \
  -j '{"data": "example"}'
```

### Output Modes
```bash
# Raw output (no formatting)
reqninja http get https://api.example.com/data --raw

# Headers only
reqninja http get https://httpbin.org/response-headers --headers-only

# Save response to file
reqninja http get https://api.example.com/data --save response.json

# Debug mode (full request/response details)
reqninja http post https://httpbin.org/post -j '{"test": "data"}' --debug
```

### Configuration Profiles
```bash
# List available profiles
reqninja config list

# Use a specific profile
reqninja http get /api/users --profile production

# Show profile details
reqninja config show production
```

## 💻 Python API Usage

### Basic Requests
```python
from reqninja import get, post, put, delete

# Simple GET request
response = get("https://jsonplaceholder.typicode.com/posts/1")
print(f"Status: {response.status_code}")
print(f"Time: {response.elapsed_ms:.2f}ms")
response.pretty_print()

# POST with JSON
data = {"title": "New Post", "body": "Content", "userId": 1}
response = post("https://jsonplaceholder.typicode.com/posts", json=data)
print(response.json())

# With custom headers
headers = {"User-Agent": "MyApp/1.0", "Accept": "application/json"}
response = get("https://api.example.com/data", headers=headers)
```

### Advanced Usage with Client
```python
from reqninja import ReqNinjaClient, Config

# Create client with custom config
client = ReqNinjaClient()

# Request with authentication
auth_config = {"type": "bearer", "token": "your-token"}
response = client.get("https://api.example.com/protected", auth=auth_config)

# Using profiles
response = client.get("/api/users", profile="production")

# With retries and timeout
response = client.get("https://api.flaky.com/data", retries=5, timeout=30)
```

### Response Handling
```python
from reqninja import get

response = get("https://api.example.com/data")

# Check status
if response.status_code == 200:
    print("Success!")
    
    # Get JSON data
    data = response.json()
    print(data)
    
    # Pretty print
    response.pretty_print()
    
    # Save to file
    response.save("api_response.json")
    
    # Get timing info
    print(f"Request took: {response.elapsed_ms:.2f}ms")
    
    # Access response details
    print(f"Content type: {response.headers.get('content-type')}")
    print(f"Response size: {len(response.content)} bytes")
else:
    print(f"Error: {response.status_code}")
```

## ⚙️ Configuration Setup

### Create Configuration File
Create `~/.reqninja/config.yml`:

```yaml
# Global settings
default_retries: 3
default_timeout: 30
default_headers:
  User-Agent: MyApp/1.0

# Retry policy
retry_policy:
  total: 5
  status_forcelist: [429, 500, 502, 503, 504]
  backoff_factor: 1.0

# Environment profiles
profiles:
  # Development environment
  dev:
    base_url: http://localhost:8000
    headers:
      Authorization: Bearer dev-token-123
    timeout: 10
    
  # Staging environment
  staging:
    base_url: https://staging-api.myapp.com
    headers:
      Authorization: Bearer ${STAGING_TOKEN}
    timeout: 30
    
  # Production environment
  prod:
    base_url: https://api.myapp.com
    headers:
      Authorization: Bearer ${PROD_TOKEN}
    timeout: 30
    retry_policy:
      total: 5
      backoff_factor: 2.0
      
  # GitHub API
  github:
    base_url: https://api.github.com
    headers:
      Authorization: Bearer ${GITHUB_TOKEN}
      Accept: application/vnd.github.v3+json
```

### Using Environment Variables
```bash
# Set environment variables
export STAGING_TOKEN="staging-secret-token"
export PROD_TOKEN="prod-secret-token"
export GITHUB_TOKEN="ghp_your_github_token"

# Use in requests
reqninja http get /user --profile github
reqninja http get /api/data --profile prod
```

## 🛠️ Advanced Use Cases

### API Testing Workflow
```bash
#!/bin/bash
# api_test.sh - API testing script

echo "Testing API endpoints..."

# Health check
echo "1. Health check:"
reqninja http get https://api.myapp.com/health --profile prod

# Authentication test
echo "2. Authentication test:"
reqninja http get https://api.myapp.com/user --profile prod

# Create resource
echo "3. Creating resource:"
reqninja http post https://api.myapp.com/posts --profile prod \
  -j '{"title": "Test Post", "content": "Testing with ReqNinja"}'

# Update resource
echo "4. Updating resource:"
reqninja http put https://api.myapp.com/posts/1 --profile prod \
  -j '{"title": "Updated Post", "content": "Updated with ReqNinja"}'

echo "API tests completed!"
```

### Batch Processing
```python
import reqninja
import time

def batch_api_calls():
    """Process multiple API calls efficiently."""
    client = reqninja.ReqNinjaClient()
    
    # List of endpoints to call
    endpoints = [
        "/api/users/1",
        "/api/users/2", 
        "/api/users/3",
        "/api/posts",
        "/api/comments"
    ]
    
    results = []
    total_time = 0
    
    for endpoint in endpoints:
        print(f"Calling {endpoint}...")
        response = client.get(endpoint, profile="prod")
        
        results.append({
            "endpoint": endpoint,
            "status": response.status_code,
            "time_ms": response.elapsed_ms,
            "size": len(response.content)
        })
        
        total_time += response.elapsed_ms
        
        # Be nice to the API
        time.sleep(0.1)
    
    # Summary
    print(f"\nCompleted {len(results)} requests in {total_time:.2f}ms")
    avg_time = total_time / len(results)
    print(f"Average response time: {avg_time:.2f}ms")
    
    return results

# Run batch processing
if __name__ == "__main__":
    results = batch_api_calls()
```

### Error Handling & Retries
```python
from reqninja import ReqNinjaClient, ReqNinjaError
import time

def robust_api_call(url, max_attempts=3):
    """Make API call with custom retry logic."""
    client = ReqNinjaClient()
    
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt + 1}/{max_attempts}")
            
            response = client.get(url, timeout=10)
            
            if response.status_code == 200:
                print("✅ Success!")
                return response.json()
            elif response.status_code >= 500:
                print(f"⚠️ Server error: {response.status_code}")
                if attempt < max_attempts - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
            else:
                print(f"❌ Client error: {response.status_code}")
                break
                
        except ReqNinjaError as e:
            print(f"❌ Request failed: {e}")
            if attempt < max_attempts - 1:
                time.sleep(2)
                continue
    
    print("❌ All attempts failed")
    return None

# Usage
data = robust_api_call("https://api.unreliable.com/data")
if data:
    print("Got data:", data)
```

## 🔄 Integration Examples

### CI/CD Pipeline Usage
```yaml
# .github/workflows/api-tests.yml
name: API Tests

on: [push, pull_request]

jobs:
  api-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install ReqNinja
        run: pip install reqninja
        
      - name: Test API endpoints
        env:
          API_TOKEN: ${{ secrets.API_TOKEN }}
        run: |
          # Health check
          reqninja http get https://api.myapp.com/health
          
          # Authenticated endpoint
          reqninja http get https://api.myapp.com/user \
            --auth "bearer $API_TOKEN"
```

### Monitoring Script
```python
#!/usr/bin/env python3
"""API monitoring script using ReqNinja."""

import reqninja
import time
import json
from datetime import datetime

def monitor_api(endpoints, interval=60):
    """Monitor API endpoints and log results."""
    client = reqninja.ReqNinjaClient()
    
    while True:
        timestamp = datetime.now().isoformat()
        print(f"\n[{timestamp}] Monitoring API endpoints...")
        
        for endpoint in endpoints:
            try:
                response = client.get(endpoint["url"], timeout=10)
                
                status = "✅ UP" if response.status_code == 200 else "❌ DOWN"
                print(f"{endpoint['name']}: {status} ({response.status_code}) - {response.elapsed_ms:.2f}ms")
                
                # Log to file
                log_entry = {
                    "timestamp": timestamp,
                    "endpoint": endpoint["name"],
                    "url": endpoint["url"],
                    "status_code": response.status_code,
                    "response_time_ms": response.elapsed_ms,
                    "status": "up" if response.status_code == 200 else "down"
                }
                
                with open("api_monitor.log", "a") as f:
                    f.write(json.dumps(log_entry) + "\n")
                    
            except Exception as e:
                print(f"{endpoint['name']}: ❌ ERROR - {e}")
        
        print(f"Next check in {interval} seconds...")
        time.sleep(interval)

# Configuration
endpoints = [
    {"name": "API Health", "url": "https://api.myapp.com/health"},
    {"name": "User Service", "url": "https://api.myapp.com/users/me"},
    {"name": "Database", "url": "https://api.myapp.com/db/status"}
]

if __name__ == "__main__":
    monitor_api(endpoints)
```

This guide shows you how to use ReqNinja for everything from simple API calls to complex automation workflows! 🚀
