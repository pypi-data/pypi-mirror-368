# ReqNinja CLI Usage Guide

## ✅ Correct Command Syntax

ReqNinja CLI uses the following command structure:

```bash
reqninja http <method> <url> [options]
```

### Examples of Correct Usage

```bash
# GET requests
reqninja http get https://api.example.com/users
reqninja http get http://localhost:3000/api/data

# POST requests
reqninja http post https://api.example.com/users -j '{"name": "John", "email": "john@example.com"}'
reqninja http post https://jsonplaceholder.typicode.com/posts -d "title=Test&body=Content"

# PUT requests
reqninja http put https://api.example.com/users/123 -j '{"name": "Updated Name"}'

# PATCH requests
reqninja http patch https://api.example.com/users/123 -j '{"email": "new@example.com"}'

# DELETE requests
reqninja http delete https://api.example.com/users/123
```

## ❌ Common Mistakes and Solutions

### 1. Using `https` instead of `http`

**Wrong:**
```bash
reqninja https get https://api.example.com/data
```

**Correct:**
```bash
reqninja http get https://api.example.com/data
```

**Note:** The `http` command handles both HTTP and HTTPS URLs automatically.

### 2. Using uppercase HTTP methods

**Wrong:**
```bash
reqninja http GET https://api.example.com/data
reqninja http POST https://api.example.com/data
```

**Correct:**
```bash
reqninja http get https://api.example.com/data
reqninja http post https://api.example.com/data
```

**Note:** HTTP methods should be lowercase: `get`, `post`, `put`, `patch`, `delete`.

## 🔧 Available Options

```bash
# Headers
reqninja http get https://api.example.com/data -H "Authorization:Bearer token123"

# Authentication
reqninja http get https://api.example.com/data -a "bearer token123"
reqninja http get https://api.example.com/data -a "basic user:password"

# JSON data
reqninja http post https://api.example.com/data -j '{"key": "value"}'

# Form data
reqninja http post https://api.example.com/data -d "key=value&other=data"

# Save response to file
reqninja http get https://api.example.com/data -s response.json

# Show only headers
reqninja http get https://api.example.com/data --headers-only

# Raw response format
reqninja http get https://api.example.com/data --raw

# Timeout and retries
reqninja http get https://api.example.com/data -t 30 -r 3

# Debug information
reqninja http get https://api.example.com/data --debug
```

## 📋 Quick Reference

| Command | Description |
|---------|-------------|
| `reqninja --help` | Show main help |
| `reqninja http --help` | Show HTTP command help |
| `reqninja http <method> --help` | Show method-specific help |
| `reqninja config --help` | Show configuration help |

## 🚀 Getting Started

1. **Simple GET request:**
   ```bash
   reqninja http get https://jsonplaceholder.typicode.com/posts/1
   ```

2. **POST with JSON:**
   ```bash
   reqninja http post https://jsonplaceholder.typicode.com/posts \
     -j '{"title": "My Post", "body": "Post content", "userId": 1}'
   ```

3. **GET with authentication:**
   ```bash
   reqninja http get https://api.github.com/user \
     -a "bearer your_github_token"
   ```

## 🆘 Error Messages

ReqNinja provides helpful error messages when you use incorrect syntax:

- **For `https` command:** Suggests using `reqninja http` instead
- **For uppercase methods:** Suggests using lowercase methods
- **For missing arguments:** Shows proper command structure

## 💡 Tips

1. **Protocol handling:** Use `reqninja http` for both HTTP and HTTPS URLs
2. **Method casing:** Always use lowercase methods (`get`, not `GET`)
3. **JSON data:** Use `-j` for JSON, `-d` for form data
4. **Headers:** Multiple headers can be specified with multiple `-H` flags
5. **Help:** Use `--help` at any level for detailed usage information
