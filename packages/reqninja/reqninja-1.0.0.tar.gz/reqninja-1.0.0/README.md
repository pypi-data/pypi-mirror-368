# ReqNinja

[![PyPI version](https://badge.fury.io/py/reqninja.svg)](https://badge.fury.io/py/reqninja)
[![Python Support](https://img.shields.io/pypi/pyversions/reqninja.svg)](https://pypi.org/project/reqninja/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/vishal-ravi/reqninja/workflows/tests/badge.svg)](https://github.com/vishal-ravi/reqninja/actions)
[![Coverage](https://codecov.io/gh/vishal-ravi/reqninja/branch/main/graph/badge.svg)](https://codecov.io/gh/vishal-ravi/reqninja)

ReqNinja is a Python package and CLI tool for API testing, automation, and debugging — blending the simplicity of curl with the power and flexibility of Python's requests.

## 🚀 Features

- **Retries & Backoff**: Automatic retry logic for flaky APIs with customizable policies
- **Fast Timing**: Instantly see how long each request takes
- **Pretty Output**: Syntax-highlighted JSON straight in your terminal
- **Authentication**: Bearer tokens, Basic Auth, OAuth2, and API keys via config
- **Config Profiles**: Quickly switch environments or base URLs
- **Response Saving**: Export results to .json or .txt files
- **Multiple Output Modes**: Raw, pretty JSON, tabular view, show headers
- **Powerful CLI**: Run API calls with a simple command, no Python required
- **Debug Mode**: Print full request/response details with timing breakdowns
- **Productivity Boost**: Pipe support, save/run commands, batch mode
- **Extensible**: Plugin system for custom output or request logic

## 📦 Installation

### From PyPI (recommended)
```bash
pip install reqninja
```

### From Source
```bash
git clone https://github.com/vishal-ravi/reqninja.git
cd reqninja
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/vishal-ravi/reqninja.git
cd reqninja
python setup_dev.py
```

## 🖥️ Quickstart: CLI Mode

### GET Request with Pretty Output

```bash
reqninja http GET https://jsonplaceholder.typicode.com/posts/1
```

### POST JSON with Custom Headers

```bash
reqninja http POST https://httpbin.org/post \
  -d '{"name":"Vishal"}' \
  -H "Content-Type: application/json"
```

### Show Raw Output

```bash
reqninja http GET /data --raw
```

### Save Response

```bash
reqninja http GET /users --save results.json
```

### Switch Profile

```bash
reqninja http GET /users --profile prod
```

### View Timing and Debug Info

```bash
reqninja http GET /users --debug
```

## 💻 Quickstart: Python Library

```python
from reqninja import get, post

response = get("https://jsonplaceholder.typicode.com/posts/1", retries=3)
print(response.json())  # Pretty printed automatically
```

## 🛠 Config Example (~/.reqninja/config.yml)

```yaml
default_retries: 3
default_headers:
  Content-Type: application/json
profiles:
  prod:
    base_url: https://api.myapp.com
    headers:
      Authorization: Bearer ${TOKEN}
  staging:
    base_url: https://staging.api.myapp.com
retry_policy:
  total: 5
  status_forcelist: [429, 500, 502, 503, 504]
  backoff_factor: 0.5
```

## 🔒 Authentication Made Simple

Pass tokens and credentials via CLI:

- `--auth bearer <TOKEN>`
- `--auth basic user:pass`

Or set them in your config file under the desired profile.

## 🏆 Productivity Shortcuts

- **Pipe**: `cat payload.json | reqninja http POST https://api.com/data`
- **Save a Command**: `reqninja save getUser "GET /users/1"`
- **Run Saved Command**: `reqninja run getUser`
- **Batch Mode**: Send a list of API calls from a file

## 🐞 Debugging

```bash
reqninja http POST /login --debug
```

Prints the full request, headers, body, and a timing breakdown for deeper inspection.

## 📝 Roadmap

- 🔑 Plugin system for custom output/auth logic
- 🎨 Templated payloads for batch/bulk requests
- 💡 Open response in browser (--open)
- 📁 Advanced response export filters

## 🙌 Why Use ReqNinja?

A single, modern tool for both quick API experiments and robust automation — with the polish, safety, and visibility pro devs expect.

## 📚 Documentation

For complete documentation, visit [reqninja.readthedocs.io](https://reqninja.readthedocs.io)

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
