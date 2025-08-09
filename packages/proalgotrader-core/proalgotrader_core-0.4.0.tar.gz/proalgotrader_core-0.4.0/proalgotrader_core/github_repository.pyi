from typing import Any

class GithubRepository:
    id: int
    repository_owner: str
    repository_name: str
    repository_full_name: str
    repository_ssh_url: str
    github_account_id: int
    def __init__(self, github_repository_info: dict[str, Any]) -> None: ...
