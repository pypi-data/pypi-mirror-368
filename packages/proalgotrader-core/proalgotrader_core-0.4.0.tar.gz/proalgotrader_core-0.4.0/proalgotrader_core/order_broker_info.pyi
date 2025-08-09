from typing import Any

class OrderBrokerInfo:
    id: int
    broker_uid: str
    broker_title: str
    broker_name: str
    broker_config: dict[str, Any]
    def __init__(self, broker_info: dict[str, Any]) -> None: ...
