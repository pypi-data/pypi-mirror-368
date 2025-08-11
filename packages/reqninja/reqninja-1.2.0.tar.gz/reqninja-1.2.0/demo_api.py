#!/usr/bin/env python3
"""Demo script for ReqNinja Python API."""

import reqninja

def main():
    print("=== ReqNinja Python API Demo ===\n")
    
    # 1. Simple GET request
    print("1. Simple GET request:")
    try:
        response = reqninja.get('https://httpbin.org/get')
        print(f"   Status: {response.status_code}")
        print(f"   Time: {response.elapsed.total_seconds():.2f}s")
        print(f"   Response keys: {list(response.json().keys())}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. POST with JSON:")
    try:
        response = reqninja.post('https://httpbin.org/post', 
                                json={'name': 'ReqNinja', 'type': 'API Client'})
        print(f"   Status: {response.status_code}")
        data = response.json().get('json', {})
        print(f"   Sent data: {data}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. Custom headers:")
    try:
        response = reqninja.get('https://httpbin.org/headers', 
                               headers={'X-Test': 'ReqNinja-Demo'})
        headers = response.json()['headers']
        print(f"   Custom header received: {headers.get('X-Test', 'Not found')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. Error handling:")
    try:
        response = reqninja.get('https://httpbin.org/status/404')
        print(f"   404 Status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    main()
