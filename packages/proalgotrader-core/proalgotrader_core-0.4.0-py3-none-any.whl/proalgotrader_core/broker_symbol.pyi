from proalgotrader_core.algorithm import Algorithm as Algorithm
from proalgotrader_core.base_symbol import BaseSymbol as BaseSymbol
from proalgotrader_core.protocols.enums.segment_type import SegmentType as SegmentType
from typing import Any

class BrokerSymbol:
    id: int
    market_type: str
    segment_type: str
    expiry_period: str
    expiry_date: str
    strike_price: int
    option_type: str
    symbol_name: str
    symbol_token: str
    exchange_token: int
    base_symbol: BaseSymbol
    algorithm: Algorithm
    ltp: float
    total_volume: int
    subscribed: bool
    def __init__(self, broker_symbol_info: dict[str, Any], algorithm: Algorithm) -> None: ...
    @property
    def can_trade(self) -> bool: ...
    def on_bar(self, ltp: float, total_volume: int) -> None: ...
    def on_tick(self, ltp: float, total_volume: int) -> None: ...
