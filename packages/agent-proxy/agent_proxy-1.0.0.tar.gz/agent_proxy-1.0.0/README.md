# HTTP Proxy CLI

A lightweight HTTP proxy CLI tool that intercepts and logs all requests to/from a specific target site.

## Features

- ✅ **Command-line interface** with rich argument support
- ✅ **Intercepts all HTTP methods** (GET, POST, PUT, DELETE, etc.)
- ✅ **Complete logging** of requests and responses
- ✅ **Configurable output** formats (JSON or plain text)
- ✅ **Flexible logging** levels and file locations
- ✅ **Real-time statistics** and testing tools

## Quick Start

### Installation

**Option 1: Install as package (recommended)**
```bash
cd simple-proxy
pip install -e .
```

**Option 2: Install dependencies**
```bash
cd simple-proxy
pip install -r requirements.txt
```

### CLI Usage

**Basic usage:**
```bash
# Start proxy with default settings
http-proxy --target https://api.example.com

# Custom port and host
http-proxy --target https://httpbin.org --port 8080 --host 0.0.0.0

# Custom logging
http-proxy --target https://jsonplaceholder.typicode.com \
           --log-file my_logs.json \
           --log-level DEBUG \
           --log-format json
```

### CLI Commands

**Main proxy command:**
```bash
http-proxy --target https://api.example.com [OPTIONS]
```

**Show statistics:**
```bash
proxy-stats --log-file proxy_requests.log
```

**Test target connectivity:**
```bash
proxy-test --target https://api.example.com --path /health
```

### CLI Arguments

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--target` | `-t` | **required** | Target URL to proxy requests to |
| `--host` | `-h` | `127.0.0.1` | Host to bind the proxy server to |
| `--port` | `-p` | `8000` | Port to bind the proxy server to |
| `--log-file` | `-l` | `proxy_requests.log` | Log file path |
| `--log-level` | `-v` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `--log-format` | `-f` | `json` | Log format (json or plain) |
| `--no-console` | | `False` | Disable console logging output |
| `--reload` | | `False` | Enable auto-reload for development |
| `--workers` | `-w` | `1` | Number of worker processes |

### Examples

**Basic proxy setup:**
```bash
# Proxy to httpbin.org on port 8080
http-proxy --target https://httpbin.org --port 8080

# Test with curl
curl http://localhost:8080/get
curl -X POST http://localhost:8080/post -d '{"test": "data"}'
```

**Advanced logging:**
```bash
# Debug mode with plain text logs
http-proxy --target https://api.github.com \
           --log-level DEBUG \
           --log-format plain \
           --log-file github_logs.txt

# Quiet mode (no console output)
http-proxy --target https://api.example.com --no-console
```

**Production setup:**
```bash
# Bind to all interfaces with multiple workers
http-proxy --target https://api.example.com \
           --host 0.0.0.0 \
           --port 80 \
           --workers 4 \
           --log-level WARNING
```

### Testing and Statistics

**Check proxy statistics:**
```bash
# Show basic stats
proxy-stats

# Custom log file
proxy-stats --log-file custom_logs.json
```

**Test target connectivity:**
```bash
# Basic connectivity test
proxy-test --target https://api.example.com

# Test specific endpoint
proxy-test --target https://api.example.com --path /health
```

### Log Format

**JSON format (default):**
```json
{
  "type": "request",
  "request_id": "req_1234567890",
  "timestamp": "2024-01-15T10:30:00.123456",
  "method": "POST",
  "url": "https://api.example.com/users",
  "headers": {
    "content-type": "application/json",
    "authorization": "Bearer token123"
  },
  "body": "{\"name\": \"John\", \"email\": \"john@example.com\"}",
  "size": 45
}
```

**Plain text format:**
```
2024-01-15 10:30:00 - INFO - REQUEST [req_1234567890] POST https://api.example.com/users - Headers: 5 - Body: 45 bytes
```

### Python Module Usage

**Direct usage:**
```python
from src.proxy import SimpleProxy
from src.logger import ProxyLogger

# Create custom logger
logger = ProxyLogger(log_file="custom.log", log_format="json")

# Create proxy
proxy = SimpleProxy("https://api.example.com", logger)
app = proxy.create_app()

# Run with uvicorn
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Development

**Install in development mode:**
```bash
pip install -e .
```

**Run tests:**
```bash
python -m src.cli --help
python -m src.cli --target https://httpbin.org --port 8080
```

### Log Files

- `proxy_requests.log`: Detailed request/response logs
- Console output: Real-time request tracking

### Error Handling

The CLI handles common errors gracefully:
- **Invalid URLs**: Validates target URLs start with http:// or https://
- **Connection errors**: Returns appropriate HTTP status codes
- **Timeout handling**: Configurable timeouts with proper error responses
- **Port conflicts**: Clear error messages for port binding issues