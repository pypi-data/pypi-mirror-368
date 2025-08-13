import requests

def say_hello(name: str):
    """Prints a greeting."""
    print(f"Hello, {name}! Welcome to pydemo.")

def fetch_url(url: str):
    """Fetches content from a URL using requests."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        print(f"Content fetched from {url}:\n{response.text[:200]}...")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
