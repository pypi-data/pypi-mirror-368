from _typeshed import Incomplete
from proalgotrader_core.broker_symbol import BrokerSymbol as BrokerSymbol
from typing import Any

class Bar:
    current_candle: Incomplete
    timestamp: Incomplete
    datetime: Incomplete
    broker_symbol: Incomplete
    open: Incomplete
    high: Incomplete
    low: Incomplete
    close: Incomplete
    volume: Incomplete
    def __init__(self, *, broker_symbol: BrokerSymbol, timestamp: int, open: float, high: float, low: float, close: float, volume: int = 0) -> None: ...
    def get_item(self) -> list[Any]: ...
