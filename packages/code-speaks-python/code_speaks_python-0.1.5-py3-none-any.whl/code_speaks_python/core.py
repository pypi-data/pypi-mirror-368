import requests

def say_hello(name: str) -> str:
    """Return a greeting string."""
    return f"Hello, {name}! Welcome to code_speaks_python."

def fetch_url(url: str) -> str:
    """Fetch content from a URL using requests and return first 200 characters."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.text[:200]
    except requests.RequestException as e:
        return f"Error fetching {url}: {e}"
