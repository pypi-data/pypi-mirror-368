from .api import async_call, call

async def async_crawl(args: dict):
    return await async_call("POST", "/api/crawl", args)

def crawl(args: dict):
    return call("POST", "/api/crawl", args)
