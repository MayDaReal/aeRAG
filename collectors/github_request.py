import os
import requests
import time
from typing import Dict, Optional, Any

def github_request(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, return_json: bool = True):
    """
    Makes a GitHub API request with rate limit handling.

    Args:
        url (str): The API endpoint URL.
        params (dict, optional): Additional query parameters.
        return_json (bool): Whether to return the response as JSON.

    Returns:
        dict or requests.Response: JSON response from GitHub API or full response object if return_json=False.
    """

    # If headers are not provided, use the GitHub token from the environment
    if headers is None:
        github_token = os.getenv("GITHUB_TOKEN")  # Read from .env only when needed
        if not github_token:
            raise ValueError("GitHub token is not set. Ensure GITHUB_TOKEN is defined in .env or provided explicitly.")
        headers = {"Authorization": f"token {github_token}"}

    while True:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)

            # Manage rate limit
            if response.status_code == 403 and 'X-RateLimit-Reset' in response.headers:
                reset_time = int(response.headers["X-RateLimit-Reset"])
                wait_time = max(0, reset_time - int(time.time())) + 1
                print(f"⚠️ GitHub rate limit reached. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue 

            # Manage HTTP errors
            if response.status_code != 200:
                print(f"❌ GitHub API Error ({response.status_code}): {response.text}")
                return None

            return response.json() if return_json else response

        except requests.RequestException as e:
            print(f"⚠️ Network error while fetching {url}: {e}")
            return None