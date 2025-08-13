# HRFH - HTTP Response Fuzzy Hashing

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/pypi-v0.1.19-blue.svg)](https://pypi.org/project/hrfh/)

A Python library for generating fuzzy hashes of HTTP responses, useful for identifying similar web content, detecting CDN configurations, and analyzing web infrastructure.

## Features

- **Fast Processing**: Efficient HTTP response parsing and hashing
- **Fuzzy Hashing**: Generate consistent hashes for similar content
- **Content Masking**: Intelligent masking of dynamic content (timestamps, IDs, etc.)
- **Multiple Formats**: Support for raw HTTP responses and JSON data
- **Python 3.7+**: Compatible with modern Python versions
- **Easy Integration**: Simple API for embedding in your projects

## Installation

### From PyPI (Recommended)

```bash
pip install hrfh
```

### From Source

```bash
git clone https://github.com/yourusername/hrfh.git
cd hrfh
uv sync
```

## Quick Start

### Basic Usage

```python
from hrfh.utils.parser import create_http_response_from_bytes

# Parse HTTP response from bytes
response = create_http_response_from_bytes(
    b"""HTTP/1.0 200 OK\r\nServer: nginx\r\nServer: apache\r\nETag: ea67ba7f802fb5c6cfa13a6b6d27adc6\r\n\r\n"""
)

# Get basic response info
print(response)
# Output: <HTTPResponse 1.1.1.1:80 200 OK>

# Get masked content (with dynamic parts masked)
print(response.masked)
# Output: HTTP/1.0 200 OK
#         ETag: [MASK]
#         Server: apache
#         Server: nginx

# Generate fuzzy hash for similarity detection
print(response.fuzzy_hash())
# Output: ba15cc1f9ad3ef632d0ce7798f7fa44718f1e7fcc2c0f94c1a702f647b79923b
```

### Interactive Example

```python
>>> from hrfh.utils.parser import create_http_response_from_bytes
>>> response = create_http_response_from_bytes(b"""HTTP/1.0 200 OK\r\nServer: nginx\r\nServer: apache\r\nETag: ea67ba7f802fb5c6cfa13a6b6d27adc6\r\n\r\n""")
>>> print(response)
<HTTPResponse 1.1.1.1:80 200 OK>
>>> print(response.masked)
HTTP/1.0 200 OK
ETag: [MASK]
Server: apache
Server: nginx
>>> print(response.fuzzy_hash())
ba15cc1f9ad3ef632d0ce7798f7fa44718f1e7fcc2c0f94c1a702f647b79923b
```

## API Reference

### Core Classes

#### HTTPResponse

Main class for representing HTTP responses with fuzzy hashing capabilities.

```python
from hrfh.models import HTTPResponse

response = HTTPResponse(
    ip="1.2.3.4",
    port=80,
    version="HTTP/1.1",
    status_code=200,
    status_reason="OK",
    headers=[("Server", "nginx"), ("Content-Type", "text/html")],
    body=b"<html>Hello World</html>"
)
```

**Key Methods:**
- `fuzzy_hash()`: Generate fuzzy hash for similarity detection
- `masked`: Get masked content with dynamic parts hidden
- `dump()`: Get formatted HTTP response string

#### HTTPRequest

Class for representing HTTP requests.

```python
from hrfh.models import HTTPRequest

request = HTTPRequest(
    ip="1.2.3.4",
    port=80,
    method="GET",
    version="HTTP/1.1",
    headers=[("Host", "example.com")],
    body=b""
)
```

### Utility Functions

#### Parsing Functions

```python
from hrfh.utils.parser import (
    create_http_response_from_bytes,
    create_http_response_from_json,
    create_http_request_from_json
)

# Parse from raw HTTP response bytes
response = create_http_response_from_bytes(http_bytes)

# Parse from JSON data
response = create_http_response_from_json(json_data)
request = create_http_request_from_json(json_data)
```

## Advanced Usage

### Working with JSON Data

```python
import json
from hrfh.utils.parser import create_http_response_from_json

# Load HTTP response data from JSON file
with open('response_data.json', 'r') as f:
    data = json.load(f)

response = create_http_response_from_json(data)
hash_value = response.fuzzy_hash()
```

**Example JSON format:**
```json
{
  "ip": "104.103.147.116",
  "timestamp": 1717146116,
  "status_code": 400,
  "status_reason": "Bad Request",
  "headers": {
    "Server": "AkamaiGHost",
    "Content-Type": "text/html",
    "Content-Length": "312"
  },
  "body": "<HTML><HEAD><TITLE>Invalid URL</TITLE></HEAD><BODY>...</BODY></HTML>"
}
```

### Batch Processing

```python
import os
from hrfh.utils.parser import create_http_response_from_json

def process_responses(data_dir):
    results = {}

    for cdn_dir in os.listdir(data_dir):
        cdn_path = os.path.join(data_dir, cdn_dir)
        if os.path.isdir(cdn_path):
            for json_file in os.listdir(cdn_path):
                if json_file.endswith('.json'):
                    file_path = os.path.join(cdn_path, json_file)
                    with open(file_path, 'r') as f:
                        data = json.load(f)

                    response = create_http_response_from_json(data)
                    hash_value = response.fuzzy_hash()
                    results[hash_value] = response

    return results

# Usage
results = process_responses('data/')
for hash_val, response in results.items():
    print(f"{hash_val[:16]} {response}")
```

## Development

### Setting Up Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/hrfh.git
   cd hrfh
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Run tests**
   ```bash
   uv run pytest
   ```

4. **Type checking**
   ```bash
   uv run mypy hrfh/
   ```

### Project Structure

```
hrfh/
├── hrfh/                    # Main package
│   ├── models/             # Data models (HTTPRequest, HTTPResponse)
│   ├── utils/              # Utility functions
│   │   ├── parser.py       # HTTP parsing utilities
│   │   ├── masker.py       # Content masking logic
│   │   ├── hasher.py       # Hashing algorithms
│   │   └── tokenizer.py    # HTML tokenization
│   └── __main__.py         # CLI entry point
├── tests/                   # Test suite
├── data/                    # Sample data for testing
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

### Running the CLI Tool

```bash
# Install the package in development mode
uv sync

# Run the CLI tool
uv run hrfh --help

# Process a specific file
uv run hrfh data/akamai/104.103.147.116.json

# Process from stdin
cat data/akamai/104.103.147.116.json | uv run hrfh -
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=hrfh

# Run specific test file
uv run pytest tests/test_http_response.py
```

## Examples

### CDN Analysis

```python
from hrfh.utils.parser import create_http_response_from_bytes

# Analyze responses from different CDNs
akamai_response = create_http_response_from_bytes(akamai_bytes)
cloudflare_response = create_http_response_from_bytes(cloudflare_bytes)

# Compare hashes to detect similar content
if akamai_response.fuzzy_hash() == cloudflare_response.fuzzy_hash():
    print("Same content served from different CDNs")
```

### Content Change Detection

```python
# Monitor for content changes
old_hash = response.fuzzy_hash()

# After some time...
new_response = create_http_response_from_bytes(new_bytes)
new_hash = new_response.fuzzy_hash()

if old_hash != new_hash:
    print("Content has changed!")
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/hrfh/issues)
- **Documentation**: [GitHub Wiki](https://github.com/yourusername/hrfh/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/hrfh/discussions)

## Acknowledgments

- Built with [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- Uses [NLTK](https://www.nltk.org/) for natural language processing
- Inspired by fuzzy hashing techniques for digital forensics
