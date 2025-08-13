# Olyptik Python SDK

Official Python SDK for the Olyptik API - a powerful web crawling and data extraction service.

## Installation

```bash
pip install olyptik
```

## Quick Start

### Synchronous Usage

```python
from olyptik import Olyptik

# Initialize the client
client = Olyptik(api_key="your_api_key_here")

# Start a crawl
crawl = client.start_crawl({
    "url": "https://example.com",
    "limit": 10
})

print(f"Crawl started with ID: {crawl.id}")

# Get crawl results
results = client.get_crawl_results(crawl.id)
for result in results.data:
    print(f"URL: {result.url}")
    print(f"Title: {result.title}")
```

### Asynchronous Usage

```python
import asyncio
from olyptik import AsyncOlyptik

async def main():
    # Initialize the async client
    client = AsyncOlyptik(api_key="your_api_key_here")
    
    # Start a crawl
    crawl = await client.start_crawl({
        "url": "https://example.com",
        "limit": 10
    })
    
    print(f"Crawl started with ID: {crawl.id}")
    
    # Get crawl results
    results = await client.get_crawl_results(crawl.id)
    for result in results.data:
        print(f"URL: {result.url}")
        print(f"Title: {result.title}")

asyncio.run(main())
```

## Features

- 🚀 Simple and intuitive API
- ⚡ Both synchronous and asynchronous support
- 🔄 Automatic retry logic
- 📝 Full type hints support
- 🛡️ Built-in error handling

## Requirements

- Python 3.8+
- httpx>=0.27.0
- python-dotenv>=1.0.1
- typing-extensions>=4.8.0

## Documentation

For detailed documentation and API reference, visit [https://docs.olyptik.io](https://docs.olyptik.io)

## Support

- 📧 Email: support@olyptik.io
- 🐛 Issues: [GitHub Issues](https://github.com/olyptik/olyptik/issues)
- 🌐 Website: [https://www.olyptik.io](https://www.olyptik.io)

## License

This project is licensed under the MIT License.
