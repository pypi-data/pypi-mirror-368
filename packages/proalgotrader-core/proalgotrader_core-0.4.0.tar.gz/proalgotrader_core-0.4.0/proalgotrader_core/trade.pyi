from datetime import datetime
from proalgotrader_core.algorithm import Algorithm as Algorithm
from proalgotrader_core.broker_symbol import BrokerSymbol as BrokerSymbol
from proalgotrader_core.protocols.enums.position_type import PositionType as PositionType
from typing import Any, Literal

class Trade:
    id: int
    position_id: str
    position_type: str
    order_type: str
    product_type: str
    quantities: int
    enter_price: float
    exit_price: float
    status: Literal['open', 'closed']
    created_at: datetime
    updated_at: datetime
    algorithm: Algorithm
    broker_symbol: BrokerSymbol
    def __init__(self, position_info: dict[str, Any], broker_symbol: BrokerSymbol, algorithm: Algorithm) -> None: ...
    @property
    def is_buy(self) -> bool: ...
    @property
    def is_sell(self) -> bool: ...
    @property
    def pnl(self) -> float: ...
    @property
    def pnl_percent(self) -> float: ...
    async def initialize(self) -> None: ...
