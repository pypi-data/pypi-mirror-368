from .configure import configure
from .crawl import crawl, async_crawl
from .extract import extract, async_extract
from .scrape import scrape, async_scrape

class FetchFox:
    def __init__(self, api_key=None, host=None):
        configure(api_key, host)

    def crawl(self, args):
        return crawl(args)

    def extract(self, args):
        return extract(args)

    def scrape(self, args):
        return scrape(args)

class AsyncFetchFox:
    def __init__(self, api_key=None, host=None):
        configure(api_key, host)

    async def crawl(self, args):
        return await async_crawl(args)

    async def extract(self, args):
        return await async_extract(args)

    async def scrape(self, args):
        return await async_scrape(args)
