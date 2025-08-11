# XPawn Python Client

A Python client library for interacting with the XPawn API.

## Installation

```bash
pip install xpawn
```

## Quick Start

```python
import xpawn

# Initialize the client
client = xpawn.Client(api_key='your-api-key')

# Get a prompt by ID
response = client.get_prompt('prompt-id')
print(response)
```

## Configuration

### Timeout
You can set a custom timeout (default is 30 seconds):

```python
client = xpawn.Client(
    api_key='your-api-key',
    timeout=60
)
```

## API Methods

### get_prompt(prompt_id)
Retrieve a prompt by its ID.

**Parameters:**
- `prompt_id` (str): The ID of the prompt to retrieve

**Returns:**
- `dict`: A dictionary containing:
  - `message` (str): The prompt content
  - `tokens_saved` (int): Number of tokens saved

**Example:**
```python
response = client.get_prompt('prompt-123')
```

### health_check()
Perform a health check on the API.

**Returns:**
- `dict`: Health check response

**Example:**
```python
health = client.health_check()
```

## License

MIT License