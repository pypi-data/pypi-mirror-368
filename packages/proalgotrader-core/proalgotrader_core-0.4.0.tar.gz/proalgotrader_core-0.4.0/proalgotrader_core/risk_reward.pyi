from _typeshed import Incomplete
from proalgotrader_core.broker_symbol import BrokerSymbol as BrokerSymbol
from proalgotrader_core.position import Position as Position
from proalgotrader_core.protocols.enums.position_type import PositionType as PositionType
from proalgotrader_core.protocols.enums.segment_type import SegmentType as SegmentType
from typing import Any, Callable

class RiskReward:
    position: Incomplete
    broker_symbol: Incomplete
    symbol_name: Incomplete
    symbol_price: Incomplete
    sl: Incomplete
    tgt: Incomplete
    tsl: Incomplete
    on_exit: Incomplete
    direction: Incomplete
    stoploss: Incomplete
    target: Incomplete
    trailed_stoplosses: list[float]
    def __init__(self, *, position: Position, broker_symbol: BrokerSymbol, symbol_name: str, symbol_price: float, sl: float, tgt: float | None = None, tsl: float | None = None, on_exit: Callable[[Any], Any]) -> None: ...
    @property
    def ltp(self) -> float: ...
    @property
    def trailed_stoploss(self) -> float: ...
    async def next(self) -> None: ...
