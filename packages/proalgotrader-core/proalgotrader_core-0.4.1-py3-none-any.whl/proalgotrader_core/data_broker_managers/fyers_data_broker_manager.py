from abc import ABC
from datetime import timedelta
from typing import Any, Dict, List

from fyers_apiv3.fyersModel import FyersModel

from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.base_symbol import BaseSymbol
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.data_broker_managers.base_data_broker_manager import (
    BaseDataBrokerManager,
)
from proalgotrader_core.token_managers.fyers_token_manager import FyersTokenManager


class FyersDataBrokerManager(BaseDataBrokerManager, ABC):
    def __init__(self, api: Api, algo_session: AlgoSession) -> None:
        self.api = api
        self.algo_session = algo_session

        broker_config = self.algo_session.project.order_broker_info.broker_config

        self.token_manager = FyersTokenManager(
            username=broker_config["username"],
            totp_key=broker_config["totp_key"],
            pin=broker_config["pin"],
            client_id=broker_config["client_id"],
            secret_key=broker_config["secret_key"],
            redirect_url=broker_config["redirect_url"],
        )

        self.http_client: FyersModel = self.token_manager.http_client

        self.resolutions = {
            timedelta(minutes=1): "1",
            timedelta(minutes=3): "3",
            timedelta(minutes=5): "5",
            timedelta(minutes=15): "15",
            timedelta(minutes=30): "30",
            timedelta(hours=1): "60",
            timedelta(hours=2): "120",
            timedelta(hours=3): "180",
            timedelta(hours=4): "240",
            timedelta(days=1): "D",
        }

        self.subscribers: List[BrokerSymbol] = []

    def start_connection(self):
        pass

    def close_connection(self):
        pass

    def subscribe(self, broker_symbol):
        pass

    def get_equity_symbol_name(
        self, broker_title: str, payload: Dict[str, Any], base_symbol: BaseSymbol
    ) -> Dict[str, Any]:
        return {
            "symbol_name": "test",
            "symbol_token": "test",
            "exchange_token": "test",
        }

    def get_future_symbol_name(
        self, broker_title: str, payload: Dict[str, Any], base_symbol: BaseSymbol
    ) -> Dict[str, Any]:
        return {
            "symbol_name": "test",
            "symbol_token": "test",
            "exchange_token": "test",
        }

    def get_option_symbol_name(
        self, broker_title: str, payload: Dict[str, Any], base_symbol: BaseSymbol
    ) -> Dict[str, Any]:
        return {
            "symbol_name": "test",
            "symbol_token": "test",
            "exchange_token": "test",
        }
