import json
import re
from urllib.parse import urlencode
import asyncio
import httpx

from .configure import api_key, host


def _camel_to_snake(s: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()


def snake_case(obj: dict) -> dict:
    """Shallow camelCase -> snake_case for object keys."""
    if not isinstance(obj, dict):
        return obj
    return {_camel_to_snake(k): v for k, v in obj.items()}

def _snake_to_camel(s: str) -> str:
    return re.sub(r'_([a-zA-Z])', lambda m: m.group(1).upper(), s)

def camel_case(obj: dict) -> dict:
    """Shallow snake_case -> camelCase for object keys."""
    if not isinstance(obj, dict):
        return obj
    return {_snake_to_camel(k): v for k, v in obj.items()}


def endpoint(path: str, options=None) -> str:
    return f"{host(options)}{path}"


class FetchFoxAPIError(Exception):
    def __init__(self, errors):
        super().__init__(json.dumps(errors))
        self.errors = errors


async def async_call(method: str, path: str, params: dict | None = None):
    """Async FetchFox API call."""
    params = params or {}
    key = api_key(params)

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    url = endpoint(path, params)
    method_upper = method.upper()
    request_kwargs = {"headers": headers}

    if method_upper == "GET":
        if params:
            url = f"{url}?{urlencode(params, doseq=True)}"
    else:
        request_kwargs["content"] = json.dumps(camel_case(params))

    timeout = httpx.Timeout(connect=10.0, read=3600.0, write=30.0, pool=30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.request(method_upper, url, **request_kwargs)
        text = resp.text

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        raise RuntimeError(f"FetchFox returned invalid JSON: {text}")

    if isinstance(data, dict) and "errors" in data and data["errors"]:
        raise FetchFoxAPIError(data["errors"])

    if resp.status_code >= 400:
        payload = {"status": f"Received status={resp.status_code}"}
        if isinstance(data, dict):
            payload |= data
        raise FetchFoxAPIError(payload)

    return data


def call(method: str, path: str, params: dict | None = None):
    """Sync wrapper for call() — runs the async function."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Running inside existing loop (e.g., Jupyter) — nest the async call
        import nest_asyncio
        nest_asyncio.apply()
        return loop.run_until_complete(async_call(method, path, params))
    else:
        return asyncio.run(async_call(method, path, params))
