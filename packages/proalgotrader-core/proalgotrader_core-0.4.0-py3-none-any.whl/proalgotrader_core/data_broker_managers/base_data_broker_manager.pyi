import abc
from _typeshed import Incomplete
from proalgotrader_core.algo_session import AlgoSession as AlgoSession
from proalgotrader_core.api import Api as Api
from proalgotrader_core.base_symbol import BaseSymbol as BaseSymbol
from proalgotrader_core.protocols.base_data_broker_manager import BaseDataBrokerManagerProtocol as BaseDataBrokerManagerProtocol
from typing import Any

class BaseDataBrokerManager(BaseDataBrokerManagerProtocol, metaclass=abc.ABCMeta):
    api: Incomplete
    algo_session: Incomplete
    def __init__(self, api: Api, algo_session: AlgoSession) -> None: ...
    def get_broker_symbols(self, broker_title: str, payload: dict[str, Any], base_symbol: BaseSymbol) -> dict[str, Any]: ...
