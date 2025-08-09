from datetime import datetime
from typing import Literal, Any, Dict, TYPE_CHECKING, Callable

from logzero import logger

if TYPE_CHECKING:
    from proalgotrader_core.algorithm import Algorithm

from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.protocols.enums.position_type import PositionType
from proalgotrader_core.protocols.enums.product_type import ProductType
from proalgotrader_core.risk_reward import RiskReward


class Position:
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
        self.exit_price: float | None = position_info["exit_price"]
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
            self.broker_symbol.ltp - self.enter_price
            if self.position_type == PositionType.BUY.value
            else self.enter_price - self.broker_symbol.ltp
        )

        return round((pnl * self.quantities), 2)

    @property
    def pnl_percent(self) -> float:
        total_volume = self.enter_price * self.quantities

        return round((self.pnl * 100) / total_volume, 2)

    @property
    def should_square_off(self) -> bool:
        if self.product_type == ProductType.NRML.value:
            expiry_date = self.algorithm.current_datetime.strftime("%Y-%m-%d")

            return self.broker_symbol.expiry_date == expiry_date
        else:
            return self.product_type == ProductType.MIS.value

    async def on_after_market_closed(self) -> None:
        if self.should_square_off:
            print(f"closing {self.broker_symbol.symbol_name}")

            await self.exit()

    async def exit(self) -> None:
        try:
            logger.debug("exiting position")

            exit_position_type: PositionType = (
                PositionType.SELL if self.is_buy else PositionType.BUY
            )

            await self.algorithm.order_broker_manager.place_order(
                broker_symbol=self.broker_symbol,
                quantities=self.quantities,
                product_type=self.product_type,
                order_type=self.order_type,
                position_type=str(exit_position_type.value),
                position_id=self.position_id,
            )
        except Exception as e:
            raise Exception(e)

    async def get_risk_reward(
        self,
        *,
        broker_symbol: BrokerSymbol,
        sl: float,
        tgt: float | None = None,
        tsl: float | None = None,
        on_exit: Callable[[Any], Any],
    ) -> RiskReward:
        risk_reward_info = self.algorithm.api.get_risk_reward(self.position_id)

        if risk_reward_info:
            if broker_symbol.symbol_name != risk_reward_info["symbol_name"]:
                logger.error("Invalid Risk reward symbol")

        if not risk_reward_info:
            payload = {
                "symbol_name": broker_symbol.symbol_name,
                "symbol_price": broker_symbol.ltp,
                "sl": round(sl, 2),
                "tgt": round(tgt, 2) if tgt else None,
                "tsl": round(tsl, 2) if tsl else None,
            }

            risk_reward_info = self.algorithm.api.create_risk_reward(
                self.position_id, payload
            )

        risk_reward = RiskReward(
            position=self,
            broker_symbol=broker_symbol,
            symbol_name=risk_reward_info["symbol_name"],
            symbol_price=risk_reward_info["symbol_price"],
            sl=risk_reward_info["sl"],
            tgt=risk_reward_info["tgt"],
            tsl=risk_reward_info["tsl"],
            on_exit=on_exit,
        )

        return risk_reward
