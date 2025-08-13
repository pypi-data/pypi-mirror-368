# Shakti SDK 🚀

A Python SDK for interacting with the Shakti Chat API - an OpenAI-compatible chat completion service.

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Features ✨

- 🔄 **Streaming Support** - Real-time token streaming for responsive applications
- 🎯 **OpenAI Compatible** - Familiar API design for easy migration
- ⚡ **Async Ready** - Built for high-performance applications
- 🛡️ **Type Hints** - Full type annotation support for better IDE experience
- 🔧 **Configurable** - Timeout, retry, and SSL verification options
- 📝 **System Messages** - Easy system prompt configuration

## Installation 📦

```bash
pip install shakti-sdk
```

Or install from source:

```bash
git clone https://github.com/yourusername/shakti-sdk.git
cd shakti-sdk
pip install -e .
```

## Quick Start 🏃‍♂️

```python
from shakti import ChatShakti

# Initialize client
client = ChatShakti(api_key="your-api-key")

# Simple completion
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response['choices'][0]['message']['content'])
```

## Usage Examples 💡

### Basic Chat Completion

```python
from shakti import ChatShakti

client = ChatShakti(api_key="your-api-key")

response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in simple terms"}
    ],
    temperature=0.7,
    max_tokens=150
)

print(response['choices'][0]['message']['content'])
```

### Streaming Responses

```python
import json

# Stream tokens as they're generated
for chunk in client.chat.completions.create(
    messages=[{"role": "user", "content": "Write a story about a robot"}],
    stream=True
):
    chunk_dict = json.loads(chunk)
    content = chunk_dict['choices'][0]['delta'].get('content', '')
    if content:
        print(content, end='', flush=True)
```

### Custom Configuration

```python
# Use custom base URL and timeout
client = ChatShakti(
    api_key="your-api-key",
    base_url="https://devshakti.serveo.net",
    timeout=60,  # 60 seconds timeout
    max_retries=3
)

# Test connection
if client.test_connection():
    print("✅ Connected successfully!")
```

### Multi-turn Conversations

```python
messages = [
    {"role": "system", "content": "You are a Python expert."},
    {"role": "user", "content": "How do I read a CSV file?"},
    {"role": "assistant", "content": "You can use pandas: `df = pd.read_csv('file.csv')`"},
    {"role": "user", "content": "What if I don't want to use pandas?"}
]

response = client.chat.completions.create(
    messages=messages,
    temperature=0.5
)
```

### Advanced Parameters

```python
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello"}],
    model="shakti-01-chat",  # Specify model
    temperature=0.8,         # Control randomness (0-2)
    top_p=0.95,             # Nucleus sampling
    max_tokens=1024,        # Maximum response length
    stream=False            # Non-streaming mode
)
```

## API Reference 📚

### ChatShakti

The main client class for interacting with the Shakti API.

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | Required | Your API key for authentication |
| `base_url` | `str` | `"https://devshakti.serveo.net"` | API base URL |
| `timeout` | `int` | `30` | Request timeout in seconds |
| `max_retries` | `int` | `3` | Maximum retry attempts |
| `verify_ssl` | `bool` | `True` | Whether to verify SSL certificates |

#### Methods

##### `chat.completions.create()`

Create a chat completion.

**Parameters:**
- `messages` (List[Dict]): List of message objects with 'role' and 'content'
- `model` (str): Model to use (default: "shakti-01-chat")
- `stream` (bool): Enable streaming mode (default: False)
- `temperature` (float): Sampling temperature 0-2 (default: 0.7)
- `top_p` (float): Nucleus sampling 0-1 (default: 0.95)
- `max_tokens` (int): Maximum tokens to generate (default: 1024)

**Returns:**
- Dict: Complete response (non-streaming)
- Iterator[str]: JSON strings of chunks (streaming)

##### `test_connection()`

Test if the API is reachable.

**Returns:**
- `bool`: True if connection successful, False otherwise

## Error Handling 🛠️

```python
from shakti import ChatShakti

client = ChatShakti(api_key="your-api-key")

try:
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Hello"}]
    )
except TimeoutError:
    print("Request timed out")
except Exception as e:
    print(f"An error occurred: {e}")
```

## Environment Variables 🔐

You can set your API key as an environment variable:

```bash
export SHAKTI_API_KEY="your-api-key"
```

Then use it in your code:

```python
import os
from shakti import ChatShakti

client = ChatShakti(api_key=os.getenv("SHAKTI_API_KEY"))
```

## Requirements 📋

- Python 3.7+
- requests>=2.25.0

## Development 🔨

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/shivnathtathe/shakti-sdk.git
cd shakti-sdk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Running Tests

```bash
python -m pytest tests/
```

### Project Structure

```
shakti-sdk/
├── shakti/
│   ├── __init__.py
│   ├── client.py     
│   └── chat.py       
├── tests/
│   └── test_client.py
├── setup.py
├── README.md
└── LICENSE
```

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support 💬

- 📧 Email: support@shakti.ai
- 🐛 Issues: [GitHub Issues](https://github.com/shivnathtathe/shakti-sdk/issues)
- 💡 Discussions: [GitHub Discussions](https://github.com/shivnathtathe/shakti-sdk/discussions)

## Acknowledgments 🙏

- Inspired by OpenAI's Python SDK
- Built with ❤️ for the developer community

---

**Note**: This SDK is in active development. Please report any issues or feature requests on our GitHub repository.