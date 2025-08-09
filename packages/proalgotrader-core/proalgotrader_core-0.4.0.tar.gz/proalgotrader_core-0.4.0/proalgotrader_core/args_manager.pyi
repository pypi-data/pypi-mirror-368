import argparse
from _typeshed import Incomplete

def parse_arguments() -> argparse.Namespace: ...

class ArgsManager:
    arguments: Incomplete
    local_key: str
    algo_session_key: Incomplete
    algo_session_secret: Incomplete
    environment: Incomplete
    api_url: Incomplete
    data_ws_url: Incomplete
    def __init__(self) -> None: ...
    def validate_arguments(self) -> None: ...
