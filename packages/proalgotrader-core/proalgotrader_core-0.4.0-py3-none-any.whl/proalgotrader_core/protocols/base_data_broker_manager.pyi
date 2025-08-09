import abc
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from proalgotrader_core.algo_session import AlgoSession as AlgoSession
from proalgotrader_core.api import Api as Api
from proalgotrader_core.bar import Bar as Bar
from proalgotrader_core.base_symbol import BaseSymbol as BaseSymbol
from proalgotrader_core.broker_symbol import BrokerSymbol as BrokerSymbol
from typing import Any

class BaseDataBrokerManagerProtocol(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def __init__(self, api: Api, algo_session: AlgoSession): ...
    @abstractmethod
    def start_connection(self) -> None: ...
    @abstractmethod
    def close_connection(self) -> None: ...
    @abstractmethod
    def subscribe(self, broker_symbol: BrokerSymbol) -> None: ...
    @abstractmethod
    def fetch_quotes(self, broker_symbol: BrokerSymbol) -> None: ...
    @abstractmethod
    def fetch_bars(self, broker_symbol: BrokerSymbol, timeframe: timedelta, fetch_from: datetime, fetch_to: datetime) -> list[Bar]: ...
    @abstractmethod
    def get_broker_symbols(self, broker_title: str, payload: dict[str, Any], base_symbol: BaseSymbol) -> dict[str, Any]: ...
