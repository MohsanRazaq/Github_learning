import requests


def validate_github_url(url):
    try:
        parts = url.strip("/").split("/")

        owner = parts[-2]
        repo = parts[-1]

        return owner, repo

    except:
        return None, None


def fetch_repository_data(url):

    owner, repo = validate_github_url(url)

    if not owner or not repo:
        return None

    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    try:

        headers = {
                "Accept": "application/vnd.github+json"
                }

        response = requests.get(
        api_url,
        headers=headers
        )
        
        
        
        

        if response.status_code != 200:
            return None

        data = response.json()

        return {
            "repo_name": data.get("name"),
            "owner": data.get("owner", {}).get("login"),
            "description": data.get("description"),
            "language": data.get("language"),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "topics": data.get("topics", []),
            "updated_at": data.get("updated_at"),
            "url": url
        }

    except Exception:
        return None