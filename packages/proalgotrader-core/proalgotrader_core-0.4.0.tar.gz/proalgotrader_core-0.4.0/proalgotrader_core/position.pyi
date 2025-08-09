from datetime import datetime
from proalgotrader_core.algorithm import Algorithm as Algorithm
from proalgotrader_core.broker_symbol import BrokerSymbol as BrokerSymbol
from proalgotrader_core.protocols.enums.position_type import PositionType as PositionType
from proalgotrader_core.protocols.enums.product_type import ProductType as ProductType
from proalgotrader_core.risk_reward import RiskReward as RiskReward
from typing import Any, Callable, Literal

class Position:
    id: int
    position_id: str
    position_type: str
    order_type: str
    product_type: str
    quantities: int
    enter_price: float
    exit_price: float | None
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
    @property
    def should_square_off(self) -> bool: ...
    async def on_after_market_closed(self) -> None: ...
    async def exit(self) -> None: ...
    async def get_risk_reward(self, *, broker_symbol: BrokerSymbol, sl: float, tgt: float | None = None, tsl: float | None = None, on_exit: Callable[[Any], Any]) -> RiskReward: ...
