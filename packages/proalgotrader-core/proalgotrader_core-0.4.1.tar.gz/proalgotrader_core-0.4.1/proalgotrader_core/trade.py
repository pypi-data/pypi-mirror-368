from datetime import datetime
from typing import List, Literal, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from proalgotrader_core.algorithm import Algorithm

from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.protocols.enums.position_type import PositionType


class Trade:
    def __init__(
        self,
        position_info: Dict[str, Any],
        broker_symbol: BrokerSymbol,
        algorithm: "Algorithm",
    ) -> None:
        self.id: int = position_info["id"]
        self.position_id: str = position_info["position_id"]
        self.position_type: str = position_info["position_type"]
        self.order_type: str = position_info["order_type"]
        self.product_type: str = position_info["product_type"]
        self.quantities: int = position_info["quantities"]
        self.enter_price: float = position_info["enter_price"]
        self.exit_price: float = position_info["exit_price"]
        self.status: Literal["open", "closed"] = position_info["status"]
        self.created_at: datetime = position_info["created_at"]
        self.updated_at: datetime = position_info["updated_at"]

        self.algorithm: "Algorithm" = algorithm

        self.broker_symbol: BrokerSymbol = broker_symbol

    @property
    def is_buy(self) -> bool:
        return self.position_type == PositionType.BUY.value

    @property
    def is_sell(self) -> bool:
        return self.position_type == PositionType.SELL.value

    @property
    def pnl(self) -> float:
        pnl: float = (
            self.exit_price - self.enter_price
            if self.position_type == PositionType.BUY.value
            else self.enter_price - self.exit_price
        )

        return round((pnl * self.quantities), 2)

    @property
    def pnl_percent(self) -> float:
        total_volume = self.enter_price * self.quantities

        return round((self.pnl * 100) / total_volume, 2)

    async def initialize(self) -> None:
        pass
