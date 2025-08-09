import os
import shutil
import subprocess
from typing import Dict, Any

from proalgotrader_core.api import Api
from proalgotrader_core.order_broker_info import OrderBrokerInfo
from proalgotrader_core.github_repository import GithubRepository


class Project:
    def __init__(self, project_info: Dict[str, Any]):
        self.id: int = project_info["id"]
        self.name: str = project_info["name"]
        self.status: str = project_info["status"]

        self.order_broker_info = OrderBrokerInfo(project_info["broker"])
        self.github_repository: GithubRepository = GithubRepository(
            project_info["strategy"]["github_repository"]
        )

    async def clone_repository(self, api: Api) -> None:
        try:
            if os.path.exists("project"):
                shutil.rmtree("project")

            repository_name = self.github_repository.repository_name

            if os.path.exists(repository_name):
                shutil.rmtree(repository_name)

            repository_owner = self.github_repository.repository_owner

            github_account_id = self.github_repository.github_account_id

            access_token = api.get_github_access_token(github_account_id)

            repository_ssh_url = f"https://{access_token}@github.com/{repository_owner}/{repository_name}.git"

            subprocess.run(
                f"git clone {repository_ssh_url} {repository_name}",
                shell=True,
                check=True,
            )

            if os.path.exists(repository_name):
                shutil.copytree(f"{repository_name}/project", "project")
                shutil.rmtree(repository_name)
        except Exception as e:
            raise Exception(e)
