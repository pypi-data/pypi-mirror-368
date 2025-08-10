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

#### Publishing Files (Super Easy!)

```python
# Upload any file by just providing the path - no boilerplate needed!
response = client.publish(
    context_name="documents",
    component_name="reports",
    file="path/to/your/document.pdf"  # That's it! 
)

# Or use the convenience method
response = client.publish_file("documents", "reports", "report.pdf")

# Works with any file type - PDFs, images, text files, etc.
client.publish("images", "screenshots", file="screenshot.png")
client.publish("data", "exports", file="data.csv")
client.publish("code", "notebooks", file="analysis.ipynb")
```

**What happens automatically:**
- ✅ MIME type detection (image/png, application/pdf, text/csv, etc.)
- ✅ Base64 encoding 
- ✅ File name extraction
- ✅ Error handling for missing files

#### Advanced File Upload

```python
# For advanced use cases, you can still provide manual file data
response = client.publish(
    context_name="documents",
    component_name="reports",
    file={
        "mime_type": "application/pdf",
        "base64": "JVBERi0xLjQK...",  # Your base64 content
        "name": "custom-report.pdf"
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

#### For JSON Data

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

#### For File Output

```python
# Automatically upload function output as a file
@publish(
    context_name="reports", 
    component_name="daily-summary",
    as_file=True,
    file_name="summary.txt"
)
def generate_daily_report():
    return "Daily Summary: All systems operational!"

# Content is automatically uploaded as a text file
report = generate_daily_report()

# Works with binary data too
@publish(
    context_name="images",
    component_name="generated-charts", 
    as_file=True,
    file_name="chart.png"
)
def create_chart():
    # Return binary PNG data
    return generate_png_bytes()
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

## Real-World Examples

### Document Processing Pipeline

```python
from contextbase import Contextbase, publish

client = Contextbase()

# Upload original document
response = client.publish_file("documents", "originals", "contract.pdf")

@publish("documents", "processed", as_file=True)
def extract_text(pdf_path):
    # Your PDF processing logic
    return extracted_text

@publish("documents", "summaries") 
def summarize_document(text):
    # Your summarization logic
    return {"summary": summary, "key_points": points}
```

### ML Model Outputs

```python
@publish("ml-pipeline", "feature-engineering", as_file=True, file_name="features.csv")
def prepare_features(raw_data):
    # Return CSV content as string
    return features_dataframe.to_csv()

@publish("ml-pipeline", "predictions")
def make_predictions(features):
    # Return JSON predictions
    return {"predictions": predictions_list, "confidence": avg_confidence}
```

### Log Analysis

```python
# Upload log files
client.publish_file("logs", "raw", "app.log")
client.publish_file("logs", "raw", "error.log")

@publish("logs", "analysis")
def analyze_logs():
    return {
        "error_count": 42,
        "top_errors": ["ConnectionTimeout", "ValidationError"],
        "peak_hours": ["14:00", "18:00"]
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

## File Upload Reference

### Supported File Types

The SDK automatically detects MIME types for common file extensions:

- **Documents**: `.pdf`, `.doc`, `.docx`, `.txt`, `.md`
- **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`
- **Data**: `.csv`, `.json`, `.xml`, `.yaml`, `.xlsx`
- **Code**: `.py`, `.js`, `.html`, `.css`, `.sql`, `.ipynb`
- **Archives**: `.zip`, `.tar`, `.gz`, `.rar`
- **Media**: `.mp4`, `.mp3`, `.wav`, `.avi`

For unknown extensions, defaults to `application/octet-stream`.

### File Upload Options

```python
# Method 1: File path (simplest)
client.publish("docs", "reports", file="report.pdf")

# Method 2: Convenience method
client.publish_file("docs", "reports", "report.pdf")

# Method 3: Pathlib Path object
from pathlib import Path
client.publish("docs", "reports", file=Path("report.pdf"))

# Method 4: Manual file data (advanced)
client.publish("docs", "reports", file={
    "mime_type": "application/pdf",
    "base64": "base64-encoded-content",
    "name": "report.pdf"
})
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

try:
    # This will also raise ValueError
    client.publish("context", "component", file="/nonexistent/file.txt")
except ValueError as e:
    print(f"File error: {e}")
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

# Run specific test file
pytest tests/test_file_upload.py -v
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
- `file_upload_examples.py` - Comprehensive file upload examples
- `decorator_examples.py` - Using the @publish decorator
- `error_handling.py` - Comprehensive error handling

## Support

- **Documentation**: [https://docs.contextbase.co](https://docs.contextbase.co)
- **Issues**: [GitHub Issues](https://github.com/contextbase/python-sdk/issues)
- **Email**: support@contextbase.co

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.