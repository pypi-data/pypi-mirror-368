# FetchFox SDK
Python library for the Fetchfox API.

FetchFox uses AI to power flexible scraping workflows.

NOTE: This interface is currently subject to change as we respond to early feedback.

## Installation

### Via PyPI

`pip install fetchfox-sdk`

## Quick Start

Sync:

```python
from fetchfox_sdk import FetchFox
fox = FetchFox(api_key="ff_your_api_key")
data = fox.crawl({
    "pattern": "https://pokemondb.net/pokedex/*",
    "max_visits": 5,
})
```

Async:

```python
from fetchfox_sdk import AsyncFetchFox
fox = AsyncFetchFox(api_key="ff_your_api_key")
data = await fox.crawl({
    "pattern": "https://pokemondb.net/pokedex/*",
    "max_visits": 5,
})
```
