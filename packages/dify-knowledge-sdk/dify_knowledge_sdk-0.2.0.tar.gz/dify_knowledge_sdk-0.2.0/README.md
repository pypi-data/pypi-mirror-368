# Dify Knowledge Base SDK

A comprehensive Python SDK for interacting with Dify's Knowledge Base API. This SDK provides easy-to-use methods for managing datasets (knowledge bases), documents, segments, and metadata through Dify's REST API.

## Features

- 📚 **Complete API Coverage**: Support for all Dify Knowledge Base API endpoints
- 🔐 **Authentication**: Secure API key-based authentication
- 📄 **Document Management**: Create, update, delete documents from text or files
- 🗂️ **Dataset Operations**: Full CRUD operations for knowledge bases
- ✂️ **Segment Control**: Manage document segments (chunks) with fine-grained control
- 🏷️ **Metadata Support**: Create and manage custom metadata fields
- 🌐 **HTTP Client**: Built on httpx for reliable and fast HTTP communications
- ⚠️ **Error Handling**: Comprehensive error handling with custom exceptions
- 📊 **Progress Monitoring**: Track document indexing progress
- 🔒 **Type Safety**: Full type hints with Pydantic models

## Installation

```bash
pip install dify-sdk
```

## Quick Start

```python
from dify_sdk import DifyDatasetClient

# Initialize the client
client = DifyDatasetClient(api_key="your-api-key-here")

# Create a new dataset (knowledge base)
dataset = client.create_dataset(
    name="My Knowledge Base",
    permission="only_me"
)

# Create a document from text
doc_response = client.create_document_by_text(
    dataset_id=dataset.id,
    name="Sample Document",
    text="This is a sample document for the knowledge base.",
    indexing_technique="high_quality"
)

# List all documents
documents = client.list_documents(dataset.id)
print(f"Total documents: {documents.total}")

# Close the client
client.close()
```

## Configuration

### API Key

Get your API key from the Dify knowledge base API page:

1. Go to your Dify knowledge base
2. Navigate to the **API** section in the left sidebar
3. Generate or copy your API key from the **API Keys** section

### Base URL

By default, the SDK uses `https://api.dify.ai` as the base URL. You can customize this:

```python
client = DifyDatasetClient(
    api_key="your-api-key",
    base_url="https://your-custom-dify-instance.com",
    timeout=60.0  # Custom timeout in seconds
)
```

## Core Features

### Dataset Management

```python
# Create a dataset
dataset = client.create_dataset(
    name="Technical Documentation",
    permission="only_me",
    description="Internal technical docs"
)

# List datasets with pagination
datasets = client.list_datasets(page=1, limit=20)

# Delete a dataset
client.delete_dataset(dataset_id)
```

### Document Operations

#### From Text

```python
# Create document from text
doc_response = client.create_document_by_text(
    dataset_id=dataset_id,
    name="API Documentation",
    text="Complete API documentation content...",
    indexing_technique="high_quality",
    process_rule_mode="automatic"
)
```

#### From File

```python
# Create document from file
doc_response = client.create_document_by_file(
    dataset_id=dataset_id,
    file_path="./documentation.pdf",
    indexing_technique="high_quality"
)
```

#### Custom Processing Rules

```python
# Custom processing configuration
process_rule_config = {
    "rules": {
        "pre_processing_rules": [
            {"id": "remove_extra_spaces", "enabled": True},
            {"id": "remove_urls_emails", "enabled": True}
        ],
        "segmentation": {
            "separator": "###",
            "max_tokens": 500
        }
    }
}

doc_response = client.create_document_by_file(
    dataset_id=dataset_id,
    file_path="document.txt",
    process_rule_mode="custom",
    process_rule_config=process_rule_config
)
```

### Segment Management

```python
# Create segments
segments_data = [
    {
        "content": "First segment content",
        "answer": "Answer for first segment",
        "keywords": ["keyword1", "keyword2"]
    },
    {
        "content": "Second segment content",
        "answer": "Answer for second segment",
        "keywords": ["keyword3", "keyword4"]
    }
]

segments = client.create_segments(dataset_id, document_id, segments_data)

# List segments
segments = client.list_segments(dataset_id, document_id)

# Update a segment
client.update_segment(
    dataset_id=dataset_id,
    document_id=document_id,
    segment_id=segment_id,
    segment_data={
        "content": "Updated content",
        "keywords": ["updated", "keywords"],
        "enabled": True
    }
)

# Delete a segment
client.delete_segment(dataset_id, document_id, segment_id)
```

### Metadata Management

```python
# Create metadata fields
category_field = client.create_metadata_field(
    dataset_id=dataset_id,
    field_type="string",
    name="category"
)

priority_field = client.create_metadata_field(
    dataset_id=dataset_id,
    field_type="number",
    name="priority"
)

# Update document metadata
metadata_operations = [
    {
        "document_id": document_id,
        "metadata_list": [
            {
                "id": category_field.id,
                "value": "technical",
                "name": "category"
            },
            {
                "id": priority_field.id,
                "value": "5",
                "name": "priority"
            }
        ]
    }
]

client.update_document_metadata(dataset_id, metadata_operations)
```

### Progress Monitoring

```python
# Monitor document indexing progress
status = client.get_document_indexing_status(dataset_id, batch_id)

if status.data:
    indexing_info = status.data[0]
    print(f"Status: {indexing_info.indexing_status}")
    print(f"Progress: {indexing_info.completed_segments}/{indexing_info.total_segments}")
```

## Error Handling

The SDK provides comprehensive error handling with specific exception types:

```python
from dify_sdk.exceptions import (
    DifyAPIError,
    DifyAuthenticationError,
    DifyValidationError,
    DifyNotFoundError,
    DifyConflictError,
    DifyServerError,
    DifyConnectionError,
    DifyTimeoutError
)

try:
    dataset = client.create_dataset(name="Test Dataset")
except DifyAuthenticationError:
    print("Invalid API key")
except DifyValidationError as e:
    print(f"Validation error: {e}")
except DifyConflictError as e:
    print(f"Conflict: {e}")  # e.g., duplicate dataset name
except DifyAPIError as e:
    print(f"API error: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Error code: {e.error_code}")
```

## Advanced Usage

For more advanced scenarios, see the [examples](./examples/) directory:

- [Basic Usage](./examples/basic_usage.py) - Simple operations and getting started
- [Advanced Usage](./examples/advanced_usage.py) - Complex workflows, batch operations, and monitoring

## API Reference

### Client Configuration

```python
DifyDatasetClient(
    api_key: str,           # Required: Your Dify API key
    base_url: str,          # Optional: API base URL (default: "https://api.dify.ai")
    timeout: float          # Optional: Request timeout in seconds (default: 30.0)
)
```

### Supported File Types

The SDK supports uploading the following file types:

- `txt` - Plain text files
- `md`, `markdown` - Markdown files
- `pdf` - PDF documents
- `html` - HTML files
- `xlsx` - Excel spreadsheets
- `docx` - Word documents
- `csv` - CSV files

### Rate Limits

Please respect Dify's API rate limits. The SDK includes automatic error handling for rate limit responses.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/dify/dify-sdk-python.git
cd dify-sdk-python

# Install dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black dify_sdk/
isort dify_sdk/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Dify Documentation](https://docs.dify.ai/)
- 🐛 [Issue Tracker](https://github.com/dify/dify-sdk-python/issues)
- 💬 [Community Discussions](https://github.com/dify/dify/discussions)

## Changelog

### v0.1.0

- Initial release
- Full Dify Knowledge Base API support
- Complete CRUD operations for datasets, documents, segments, and metadata
- Comprehensive error handling
- Type-safe models with Pydantic
- File upload support
- Progress monitoring
- Examples and documentation
