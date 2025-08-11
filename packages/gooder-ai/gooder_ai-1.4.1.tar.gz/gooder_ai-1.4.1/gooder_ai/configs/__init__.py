import requests


def load_starter_config() -> dict:
    """
    Fetches the starter configuration JSON data from a remote URL.
    """
    url = "https://raw.githubusercontent.com/EricVSiegel/ml-viz-docs/refs/heads/main/src/pages/UserConfig/config.json"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()
