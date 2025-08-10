import os

# Default configuration
config = {
    "host": "https://api.fetchfox.ai",
    "api_key": None
}

def safe_env(key: str):
    return os.environ.get(key)

def configure(api_key=None, host=None):
    """Configure the global FetchFox settings."""
    if api_key:
        config["api_key"] = api_key
    if host:
        config["host"] = host

def api_key(options=None):
    """Get API key from options, config, or environment."""
    options = options or {}
    return (
        options.get("api_key")
        or config.get("api_key")
        or safe_env("FETCHFOX_API_KEY")
    )

def host(options=None):
    """Get API host from options, config, or environment."""
    options = options or {}
    return (
        options.get("host")
        or config.get("host")
        or safe_env("FETCHFOX_HOST")
    )

def app_host(options=None):
    """Get App host (replace 'api.fetchfox.ai' with 'app.fetchfox.ai')."""
    h = host(options)
    if h:
        return h.replace("api.fetchfox.ai", "app.fetchfox.ai")
    return None
