# DevShakti AI SDK

Python SDK for Shakti AI - An OpenAI-compatible LLM API.

## 🚀 Installation

```bash
pip install devshakti-ai
```

## 📚 Documentation

Full documentation, interactive playground, and API reference available at:

### **🔗 https://shakti-one.vercel.app**

## ⚡ Quick Start

```python
from shakti import ChatShakti
import json

# Initialize client
client = ChatShakti(api_key="sk-your-api-key")

# Simple completion
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello"}]
)
print(response['choices'][0]['message']['content'])
```

## 🎯 Streaming Example

```python
from shakti import ChatShakti
import json

client = ChatShakti(api_key="sk-your-api-key")

# Streaming response
for chunk in client.chat.completions.create(
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
):
    chunk_dict = json.loads(chunk)
    content = chunk_dict['choices'][0]['delta'].get('content', '')
    if content:
        print(content, end='', flush=True)
```

## 🎨 Custom Configuration

```python
from shakti import ChatShakti

# Custom base URL and parameters
client = ChatShakti(
    api_key="sk-your-api-key",
    base_url="https://devshakti.serveo.net"  # Optional
)

response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    model="shakti-01-chat",
    temperature=0.7,
    max_tokens=1024,
    stream=False
)
```

## ✨ Features

- ✅ **OpenAI-compatible API** - Easy migration from OpenAI
- ✅ **Streaming support** - Real-time token streaming
- ✅ **Simple Python interface** - Clean, intuitive SDK
- ✅ **Free tier available** - Get started at no cost
- ✅ **Fast responses** - 2-3 second average latency
- ✅ **Rate limiting** - 60 requests/min, 150k tokens/min

## 🔧 API Endpoints

- **Base URL**: `https://devshakti.serveo.net`
- **Chat Completions**: `/v1/chat/completions`
- **Models**: `/v1/models`
- **Health Check**: `/health`

## 📝 Basic Usage

### Simple Request

```python
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "What is Python?"}]
)
```

### With System Prompt

```python
response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are a coding expert."},
        {"role": "user", "content": "Explain async/await"}
    ]
)
```

### Streaming Tokens

```python
for chunk in client.chat.completions.create(
    messages=[{"role": "user", "content": "Write a poem"}],
    stream=True
):
    # Process each token as it arrives
    chunk_dict = json.loads(chunk)
    content = chunk_dict['choices'][0]['delta'].get('content', '')
    if content:
        print(content, end='', flush=True)
```

## 🔑 Get Your API Key

Visit **https://shakti-one.vercel.app** to:
- 🔐 Generate your free API key
- 🎮 Try the interactive playground  
- 📖 Read full documentation
- 💻 See more code examples

## 📊 Rate Limits

- **Requests**: 60 per minute
- **Tokens**: 150,000 per minute
- **Concurrent**: 10 requests

## 🛠️ Requirements

- Python 3.7+
- `requests` library (installed automatically)

## 🤝 Support

- **Documentation**: https://shakti-one.vercel.app
- **GitHub Issues**: https://github.com/shivnathtathe/shakti-sdk/issues
- **Email**: sptathe2001@gmail.com

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🌟 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

<div align="center">
Made with ❤️ by Shivnath Tathe

**[Get Started →](https://shakti-one.vercel.app)**
</div>