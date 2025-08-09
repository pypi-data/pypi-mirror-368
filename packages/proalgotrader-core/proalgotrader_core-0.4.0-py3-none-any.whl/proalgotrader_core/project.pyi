from _typeshed import Incomplete
from proalgotrader_core.api import Api as Api
from proalgotrader_core.github_repository import GithubRepository as GithubRepository
from proalgotrader_core.order_broker_info import OrderBrokerInfo as OrderBrokerInfo
from typing import Any

class Project:
    id: int
    name: str
    status: str
    order_broker_info: Incomplete
    github_repository: GithubRepository
    def __init__(self, project_info: dict[str, Any]) -> None: ...
    async def clone_repository(self, api: Api) -> None: ...
