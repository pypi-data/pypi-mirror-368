# Contextbase Python SDK

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

The official Python SDK for Contextbase, providing easy-to-use interfaces for context management and data publishing.

## Installation

```bash
pip install contextbase
```

## Quick Start

### Setup

First, set your API key as an environment variable:

```bash
export CONTEXTBASE_API_KEY="your-api-key-here"
```

Or pass it directly when initializing the client:

```python
from contextbase import Contextbase

client = Contextbase(api_key="your-api-key-here")
```

### Basic Usage

#### Publishing Data

```python
from contextbase import Contextbase

client = Contextbase()

# Publish JSON data
response = client.publish(
    context_name="my-app",
    component_name="user-analytics", 
    body={"user_id": 123, "action": "login", "timestamp": "2024-01-15T10:30:00Z"}
)

if response.ok:
    print("Data published successfully!")
    print(f"Response: {response.json}")
else:
    print(f"Error: {response.error.message}")
```

#### Publishing Files

```python
import base64

# Read and encode file
with open("data.txt", "rb") as f:
    file_content = base64.b64encode(f.read()).decode('utf-8')

response = client.publish(
    context_name="documents",
    component_name="reports",
    file={
        "mime_type": "text/plain",
        "base64": file_content,
        "name": "data.txt"
    }
)
```

#### Resolving/Querying Data

```python
# Basic query
response = client.resolve("my-app")

# Query with search term
response = client.resolve(
    context_name="my-app",
    query="user login events"
)

# Query with scopes
response = client.resolve(
    context_name="my-app",
    scopes={"environment": "production", "date_range": "last_week"}
)

if response.ok:
    results = response.json
    print(f"Found {len(results)} results")
```

### Using the Decorator

The `@publish` decorator automatically publishes function results to Contextbase:

```python
from contextbase import publish

@publish(context_name="ml-models", component_name="predictions")
def predict_user_behavior(user_data):
    # Your ML logic here
    prediction = {"user_id": user_data["id"], "likely_to_churn": 0.23}
    return prediction

# Function runs normally, and result is automatically published
result = predict_user_behavior({"id": 123, "activity": "low"})
```

#### Decorator with Error Handling

```python
# Raise exceptions on publish failures
@publish(
    context_name="critical-data", 
    component_name="financial-calculations",
    raise_on_error=True
)
def calculate_risk_score(portfolio):
    return {"risk_score": 0.75, "confidence": 0.92}

# Silently continue on publish failures (default)
@publish(
    context_name="analytics", 
    component_name="user-events",
    raise_on_error=False
)
def track_user_action(user_id, action):
    return {"user_id": user_id, "action": action}
```

#### Decorator with Scopes

```python
@publish(
    context_name="monitoring",
    component_name="system-metrics",
    scopes={"environment": "production", "service": "api"}
)
def collect_metrics():
    return {
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "timestamp": "2024-01-15T10:30:00Z"
    }
```

## Advanced Usage

### Error Handling

```python
from contextbase import Contextbase, ContextbaseError

client = Contextbase()

try:
    response = client.publish("context", "component", body={"data": "value"})
    response.raise_for_status()  # Raises ContextbaseError if response failed
    print("Success!")
except ContextbaseError as e:
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
    for error in e.errors:
        print(f"  - {error}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Response Object Methods

```python
response = client.publish("context", "component", body={"data": "value"})

# Check success
if response.ok:  # or response.is_success
    print("Request successful")

# Access response data
data = response.json          # Parsed JSON response
text = response.text          # Raw response text  
headers = response.headers    # Response headers dict

# Dict-like access
value = response.get("key", "default")
if "field" in response:
    field_value = response["field"]

# Error information
if not response.ok:
    error = response.error
    print(f"Error: {error.message}")
    print(f"Details: {error.errors}")
```

### Custom Configuration

```python
# Custom API URL and key
client = Contextbase(api_key="custom-key")

# Using environment variables
import os
os.environ["CONTEXTBASE_API_URL"] = "https://custom-api.contextbase.co"
os.environ["CONTEXTBASE_API_KEY"] = "your-key"

client = Contextbase()
```

## Error Reference

### ContextbaseError

Raised when the API returns an error response:

```python
try:
    response = client.publish("context", "component", body={})
    response.raise_for_status()
except ContextbaseError as e:
    print(f"Status: {e.status_code}")     # HTTP status code
    print(f"Message: {e.message}")        # Error message
    print(f"Details: {e.errors}")         # List of detailed errors
```

### ValueError

Raised for client-side validation errors:

```python
try:
    # This will raise ValueError
    client.publish("context", "component")  # Missing both body and file
except ValueError as e:
    print(f"Validation error: {e}")
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=contextbase --cov-report=html
```

### Code Formatting

```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
mypy src/
```

## Examples

Check out the `examples/` directory for more detailed usage examples:

- `basic_usage.py` - Simple publish and resolve operations
- `decorator_examples.py` - Using the @publish decorator
- `error_handling.py` - Comprehensive error handling
- `file_upload.py` - Publishing files and binary data

## Support

- **Documentation**: [https://docs.contextbase.co](https://docs.contextbase.co)
- **Issues**: [GitHub Issues](https://github.com/contextbase/python-sdk/issues)
- **Email**: support@contextbase.co

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.