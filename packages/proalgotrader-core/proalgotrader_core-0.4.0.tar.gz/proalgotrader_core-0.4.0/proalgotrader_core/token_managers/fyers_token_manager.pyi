from _typeshed import Incomplete
from fyers_apiv3.FyersWebsocket.data_ws import FyersDataSocket
from fyers_apiv3.fyersModel import FyersModel
from proalgotrader_core.token_managers.base_token_manager import BaseTokenManager as BaseTokenManager
from typing import Any

AUTH_URL: str
API_URL: str
URL_SEND_LOGIN_OTP_V2: Incomplete
URL_VERIFY_TOTP: Incomplete
URL_VERIFY_PIN_V2: Incomplete
URL_TOKEN: Incomplete
URL_VALIDATE_AUTH_CODE: Incomplete
session: Incomplete

class FyersTokenManager(BaseTokenManager):
    username: Incomplete
    totp_key: Incomplete
    pin: Incomplete
    client_id: Incomplete
    secret_key: Incomplete
    redirect_url: Incomplete
    ws_client: FyersDataSocket | None
    http_client: FyersModel | None
    ws_access_token: str | None
    http_access_token: str | None
    app_id: Incomplete
    app_type: Incomplete
    def __init__(self, username: str, totp_key: str, pin: str, client_id: str, secret_key: str, redirect_url: str) -> None: ...
    def set_token(self, token: str) -> None: ...
    def get_token(self) -> str: ...
    def login_otp(self) -> Any: ...
    def verify_otp(self, request_key: str, attempt: int = 1) -> Any: ...
    def verify_pin(self, request_key: str) -> Any: ...
    def get_auth_code(self, access_token: str) -> str: ...
