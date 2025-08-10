import pytest
from fetchfox_sdk import (
    FetchFox,
    AsyncFetchFox,
    crawl,
    async_crawl,
    extract,
    async_extract,
    scrape,
    async_scrape,
)

def test_crawl():
    data = crawl({
        "pattern": "https://pokemondb.net/pokedex/*",
        "max_visits": 5,
    })
    assert len(data["results"]["hits"]) > 10

@pytest.mark.asyncio
async def test_crawl_async():
    data = await async_crawl({
        "pattern": "https://pokemondb.net/pokedex/*",
        "max_visits": 5,
    })
    assert len(data["results"]["hits"]) > 10

def test_crawl_fox():
    fox = FetchFox()
    data = fox.crawl({
        "pattern": "https://pokemondb.net/pokedex/*",
        "max_visits": 5,
    })
    assert len(data["results"]["hits"]) > 10

@pytest.mark.asyncio
async def test_crawl_fox_async():
    fox = AsyncFetchFox()
    data = await fox.crawl({
        "pattern": "https://pokemondb.net/pokedex/*",
        "max_visits": 5,
    })
    assert len(data["results"]["hits"]) > 10

def test_extract():
    data = extract({
        "urls": [
            "https://pokemondb.net/pokedex/charmander",
            "https://pokemondb.net/pokedex/pikachu",
        ],
        "template": "pokemon name, number, and HP",
    })
    assert len(data["results"]["items"]) == 2
    assert "pikachu" in str(data["results"]["items"]).lower()
    assert "charmander" in str(data["results"]["items"]).lower()

def test_extract_fox():
    fox = FetchFox()
    data = fox.extract({
        "urls": [
            "https://pokemondb.net/pokedex/charmander",
            "https://pokemondb.net/pokedex/pikachu",
        ],
        "template": "pokemon name, number, and HP",
    })
    assert len(data["results"]["items"]) == 2
    assert "pikachu" in str(data["results"]["items"]).lower()
    assert "charmander" in str(data["results"]["items"]).lower()
def test_extract_fox():
    fox = FetchFox()
    data = fox.extract({
        "urls": [
            "https://pokemondb.net/pokedex/charmander",
            "https://pokemondb.net/pokedex/pikachu",
        ],
        "template": "pokemon name, number, and HP",
    })
    assert len(data["results"]["items"]) == 2
    assert "pikachu" in str(data["results"]["items"]).lower()
    assert "charmander" in str(data["results"]["items"]).lower()

@pytest.mark.asyncio
async def test_extract_async():
    data = await async_extract({
        "urls": [
            "https://pokemondb.net/pokedex/charmander",
            "https://pokemondb.net/pokedex/pikachu",
        ],
        "template": "pokemon name, number, and HP",
    })
    assert len(data["results"]["items"]) == 2
    assert "pikachu" in str(data["results"]["items"]).lower()
    assert "charmander" in str(data["results"]["items"]).lower()


def test_scrape():
    data = scrape({
        "pattern": "https://pokemondb.net/pokedex/*saur",
        "start_urls": ["https://pokemondb.net/pokedex/national"],
        "max_visits": 5,
        "template": "pokemon name, number, and HP",
    })
    assert len(data["results"]["items"]) == 3
    assert "bulbasaur" in str(data["results"]["items"]).lower()
    assert "ivysaur" in str(data["results"]["items"]).lower()
    assert "venusaur" in str(data["results"]["items"]).lower()

@pytest.mark.asyncio
async def test_scrape_async():
    data = await async_scrape({
        "pattern": "https://pokemondb.net/pokedex/*saur",
        "start_urls": ["https://pokemondb.net/pokedex/national"],
        "max_visits": 5,
        "template": "pokemon name, number, and HP",
    })
    assert len(data["results"]["items"]) == 3
    assert "bulbasaur" in str(data["results"]["items"]).lower()
    assert "ivysaur" in str(data["results"]["items"]).lower()
    assert "venusaur" in str(data["results"]["items"]).lower()

def test_scrape_fox():
    fox = FetchFox()
    data = fox.scrape({
        "pattern": "https://pokemondb.net/pokedex/*saur",
        "start_urls": ["https://pokemondb.net/pokedex/national"],
        "max_visits": 5,
        "template": "pokemon name, number, and HP",
    })
    assert len(data["results"]["items"]) == 3
    assert "bulbasaur" in str(data["results"]["items"]).lower()
    assert "ivysaur" in str(data["results"]["items"]).lower()
    assert "venusaur" in str(data["results"]["items"]).lower()

@pytest.mark.asyncio
async def test_scrape_fox_async():
    fox = AsyncFetchFox()
    data = await fox.scrape({
        "pattern": "https://pokemondb.net/pokedex/*saur",
        "start_urls": ["https://pokemondb.net/pokedex/national"],
        "max_visits": 5,
        "template": "pokemon name, number, and HP",
    })
    assert len(data["results"]["items"]) == 3
    assert "bulbasaur" in str(data["results"]["items"]).lower()
    assert "ivysaur" in str(data["results"]["items"]).lower()
    assert "venusaur" in str(data["results"]["items"]).lower()
