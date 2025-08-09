from datetime import datetime
from proalgotrader_core.algorithm import Algorithm as Algorithm
from proalgotrader_core.broker_symbol import BrokerSymbol as BrokerSymbol
from typing import Any, Literal

class Order:
    id: int
    order_id: str
    position_id: str | None
    position_type: str
    order_type: str
    product_type: str
    quantities: int
    price: float
    status: Literal['pending', 'completed', 'rejected', 'failed']
    created_at: datetime
    updated_at: datetime
    algorithm: Algorithm
    broker_symbol: BrokerSymbol
    def __init__(self, order_info: dict[str, Any], broker_symbol: BrokerSymbol, algorithm: Algorithm) -> None: ...
    async def initialize(self) -> None: ...
    @property
    def is_completed(self) -> bool: ...
    @property
    def is_pending(self) -> bool: ...
