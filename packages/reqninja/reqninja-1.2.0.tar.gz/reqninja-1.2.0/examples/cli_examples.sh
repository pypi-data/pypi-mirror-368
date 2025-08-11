#!/bin/bash
# ReqNinja CLI Examples
# Run these commands to test the CLI functionality

echo "ReqNinja CLI Examples"
echo "===================="

echo
echo "1. Basic GET request:"
reqninja http GET https://jsonplaceholder.typicode.com/posts/1

echo
echo "2. POST request with JSON data:"
reqninja http POST https://httpbin.org/post \
  -j '{"name": "ReqNinja", "version": "1.0"}'

echo
echo "3. Request with custom headers:"
reqninja http GET https://httpbin.org/headers \
  -H "X-Custom-Header: ReqNinja-Test" \
  -H "Accept: application/json"

echo
echo "4. Basic authentication:"
reqninja http GET https://httpbin.org/basic-auth/user/pass \
  --auth "basic user:pass"

echo
echo "5. Bearer token authentication:"
reqninja http GET https://httpbin.org/bearer \
  --auth "bearer test-token-123"

echo
echo "6. Request with timeout:"
reqninja http GET https://httpbin.org/delay/2 \
  --timeout 5

echo
echo "7. Show only headers:"
reqninja http GET https://httpbin.org/response-headers \
  --headers-only

echo
echo "8. Raw output:"
reqninja http GET https://httpbin.org/json \
  --raw

echo
echo "9. Debug mode:"
reqninja http POST https://httpbin.org/post \
  -d "test data" \
  --debug

echo
echo "10. Save response to file:"
reqninja http GET https://jsonplaceholder.typicode.com/posts/1 \
  --save response.json

echo
echo "11. Using profiles (requires config setup):"
echo "First, let's see available profiles:"
reqninja config list

echo
echo "Examples completed!"
echo "Check the saved response.json file."
