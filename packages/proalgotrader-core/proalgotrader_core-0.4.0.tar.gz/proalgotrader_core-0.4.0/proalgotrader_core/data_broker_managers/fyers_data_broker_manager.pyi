import abc
from _typeshed import Incomplete
from abc import ABC
from fyers_apiv3.fyersModel import FyersModel as FyersModel
from proalgotrader_core.algo_session import AlgoSession as AlgoSession
from proalgotrader_core.api import Api as Api
from proalgotrader_core.base_symbol import BaseSymbol as BaseSymbol
from proalgotrader_core.broker_symbol import BrokerSymbol as BrokerSymbol
from proalgotrader_core.data_broker_managers.base_data_broker_manager import BaseDataBrokerManager as BaseDataBrokerManager
from proalgotrader_core.token_managers.fyers_token_manager import FyersTokenManager as FyersTokenManager
from typing import Any

class FyersDataBrokerManager(BaseDataBrokerManager, ABC, metaclass=abc.ABCMeta):
    api: Incomplete
    algo_session: Incomplete
    token_manager: Incomplete
    http_client: FyersModel
    resolutions: Incomplete
    subscribers: list[BrokerSymbol]
    def __init__(self, api: Api, algo_session: AlgoSession) -> None: ...
    def start_connection(self) -> None: ...
    def close_connection(self) -> None: ...
    def subscribe(self, broker_symbol) -> None: ...
    def get_equity_symbol_name(self, broker_title: str, payload: dict[str, Any], base_symbol: BaseSymbol) -> dict[str, Any]: ...
    def get_future_symbol_name(self, broker_title: str, payload: dict[str, Any], base_symbol: BaseSymbol) -> dict[str, Any]: ...
    def get_option_symbol_name(self, broker_title: str, payload: dict[str, Any], base_symbol: BaseSymbol) -> dict[str, Any]: ...
