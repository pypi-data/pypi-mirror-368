from abc import abstractmethod, ABC

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Dict, List

from proalgotrader_core.bar import Bar
from proalgotrader_core.base_symbol import BaseSymbol
from proalgotrader_core.broker_symbol import BrokerSymbol

if TYPE_CHECKING:
    from proalgotrader_core.algo_session import AlgoSession
    from proalgotrader_core.api import Api


class BaseDataBrokerManagerProtocol(ABC):
    @abstractmethod
    def __init__(self, api: "Api", algo_session: "AlgoSession") -> None: ...

    @abstractmethod
    def start_connection(self) -> None: ...

    @abstractmethod
    def close_connection(self) -> None: ...

    @abstractmethod
    def subscribe(self, broker_symbol: BrokerSymbol) -> None: ...

    @abstractmethod
    def fetch_quotes(self, broker_symbol: BrokerSymbol) -> None: ...

    @abstractmethod
    def fetch_bars(
        self,
        broker_symbol: BrokerSymbol,
        timeframe: timedelta,
        fetch_from: datetime,
        fetch_to: datetime,
    ) -> List[Bar]: ...

    @abstractmethod
    def get_broker_symbols(
        self, broker_title: str, payload: Dict[str, Any], base_symbol: BaseSymbol
    ) -> Dict[str, Any]: ...
