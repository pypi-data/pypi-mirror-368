from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from _typeshed import Incomplete
from proalgotrader_core.token_managers.base_token_manager import BaseTokenManager as BaseTokenManager

class AngelOneTokenManager(BaseTokenManager):
    token: str | None
    client_id: Incomplete
    totp_key: Incomplete
    mpin: Incomplete
    api_key: Incomplete
    api_secret: Incomplete
    redirect_url: Incomplete
    session: Incomplete
    http_client: Incomplete
    ws_client: Incomplete
    def __init__(self, client_id: str, totp_key: str, mpin: str, api_key: str, api_secret: str, redirect_url: str) -> None: ...
    def set_token(self, token: str) -> None: ...
    def get_token(self) -> str: ...
    def get_http_client(self) -> SmartConnect: ...
    def get_ws_client(self) -> SmartWebSocketV2: ...
