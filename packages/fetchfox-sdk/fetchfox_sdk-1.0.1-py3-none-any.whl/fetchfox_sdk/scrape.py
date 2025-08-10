from .api import async_call, call

async def async_scrape(args: dict):
    return await async_call("POST", "/api/scrape", args)

def scrape(args: dict):
    return call("POST", "/api/scrape", args)
