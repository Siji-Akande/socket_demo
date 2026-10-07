import requests
from pydantic import BaseModel


class Repo(BaseModel):
    full_name: str
    stargazers_count: int


def fetch_repo(name: str) -> Repo:
    response = requests.get(
        f"https://api.github.com/repos/{name}", timeout=10
    )
    response.raise_for_status()
    return Repo(**response.json())


if __name__ == "__main__":
    repo = fetch_repo("python/cpython")
    print(f"{repo.full_name} has {repo.stargazers_count} stars")