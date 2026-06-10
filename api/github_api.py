"""
GitHub API integration module.
Fetches repository data from the GitHub REST API with proper
validation, error handling, and optional token authentication.
"""
import re
import requests
from config import GITHUB_TOKEN, GITHUB_API_BASE


def validate_github_url(url):
    """
    Validate and extract owner/repo from a GitHub URL.
    Supports formats:
      - https://github.com/owner/repo
      - https://github.com/owner/repo/
      - github.com/owner/repo
      - owner/repo
    """
    url = url.strip().rstrip("/")

    # Full URL format
    match = re.match(
        r"^(?:https?://)?github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)$",
        url
    )
    if match:
        return match.group(1), match.group(2)

    # Short format: owner/repo
    match = re.match(
        r"^([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)$",
        url
    )
    if match:
        return match.group(1), match.group(2)

    return None, None


def _get_headers():
    """Build request headers, including auth token if available."""
    headers = {
        "Accept": "application/vnd.github+json"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def fetch_repository_data(url):
    """
    Fetch comprehensive repository data from the GitHub API.
    Returns a dict with all relevant fields, or None on failure.
    """
    owner, repo = validate_github_url(url)

    if not owner or not repo:
        return None

    api_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    headers = _get_headers()

    try:
        response = requests.get(api_url, headers=headers, timeout=15)

        if response.status_code == 404:
            return None
        elif response.status_code == 403:
            return None  # Rate limited
        elif response.status_code != 200:
            return None

        data = response.json()

        return {
            "repo_name": data.get("name", "Unknown"),
            "owner": data.get("owner", {}).get("login", "Unknown"),
            "description": data.get("description") or "No description provided.",
            "language": data.get("language") or "Not specified",
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "watchers": data.get("subscribers_count", 0),
            "size_kb": data.get("size", 0),
            "license": (data.get("license") or {}).get("spdx_id", "None"),
            "has_wiki": data.get("has_wiki", False),
            "default_branch": data.get("default_branch", "main"),
            "created_at": data.get("created_at", ""),
            "updated_at": data.get("updated_at", ""),
            "topics": data.get("topics", []),
            "url": f"https://github.com/{owner}/{repo}",
        }

    except requests.ConnectionError:
        return None
    except requests.Timeout:
        return None
    except requests.RequestException:
        return None
    except (ValueError, KeyError):
        return None


def fetch_languages(owner, repo):
    """Fetch all languages used in a repository."""
    api_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages"
    headers = _get_headers()

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()  # {"Python": 25000, "JavaScript": 12000, ...}
        return {}
    except requests.RequestException:
        return {}


def fetch_contributors_count(owner, repo):
    """Fetch approximate contributor count."""
    api_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contributors"
    headers = _get_headers()

    try:
        response = requests.get(
            api_url, headers=headers,
            params={"per_page": 1, "anon": "true"},
            timeout=10
        )
        if response.status_code == 200:
            # GitHub returns total count in the Link header
            link = response.headers.get("Link", "")
            if 'rel="last"' in link:
                import re as regex
                match = regex.search(r'page=(\d+)>; rel="last"', link)
                if match:
                    return int(match.group(1))
            return len(response.json())
        return 0
    except requests.RequestException:
        return 0