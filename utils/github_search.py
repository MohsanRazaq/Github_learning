import requests
from config import GITHUB_API_BASE, GITHUB_TOKEN

def _get_headers():
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers

def search_top_repos_by_skill(skill: str, limit: int = 5):
    """Search GitHub for repositories related to a skill.
    Uses the GitHub Search API with the skill as a keyword.
    Returns a list of dicts with keys: name, full_name, description, html_url.
    """
    query = f"{skill} in:name,description,readme"
    url = f"{GITHUB_API_BASE}/search/repositories"
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": limit}
    try:
        resp = requests.get(url, headers=_get_headers(), params=params, timeout=10)
        if resp.status_code != 200:
            return []
        data = resp.json()
        items = data.get("items", [])
        results = []
        for item in items:
            results.append({
                "name": item.get("name"),
                "full_name": item.get("full_name"),
                "description": item.get("description") or "",
                "html_url": item.get("html_url"),
            })
        return results
    except Exception:
        return []
