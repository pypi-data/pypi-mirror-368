from abc import ABC
from typing import Dict, Any
from uuid import uuid4

from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.order_broker_managers.base_order_broker_manager import (
    BaseOrderBrokerManager,
)
from proalgotrader_core.order import Order
from proalgotrader_core.position import Position
from proalgotrader_core.protocols.enums.order_type import OrderType
from proalgotrader_core.protocols.enums.position_type import PositionType
from proalgotrader_core.protocols.enums.product_type import ProductType


class PaperOrderBrokerManager(BaseOrderBrokerManager, ABC):
    def __init__(self, api: Api, algo_session: AlgoSession) -> None:
        super().__init__(api=api, algo_session=algo_session)

    async def get_order_types(self) -> Dict[Any, Any]:
        return {
            OrderType.LIMIT_ORDER.value: 1,
            1: OrderType.LIMIT_ORDER.value,
            OrderType.MARKET_ORDER.value: 2,
            2: OrderType.MARKET_ORDER.value,
            OrderType.STOP_ORDER.value: 3,
            3: OrderType.STOP_ORDER.value,
            OrderType.STOP_LIMIT_ORDER.value: 4,
            4: OrderType.STOP_LIMIT_ORDER.value,
        }

    async def get_position_types(self) -> Dict[Any, Any]:
        return {
            PositionType.BUY.value: 1,
            1: PositionType.BUY.value,
            PositionType.SELL.value: -1,
            -1: PositionType.SELL.value,
        }

    async def get_product_types(self) -> Dict[Any, Any]:
        return {
            ProductType.MIS.value: "INTRADAY",
            "INTRADAY": ProductType.MIS.value,
            ProductType.NRML.value: "MARGIN",
            "MARGIN": ProductType.NRML.value,
            ProductType.CNC.value: "CNC",
            "CNC": ProductType.CNC.value,
        }

    async def set_initial_capital(self) -> None:
        self.initial_capital = self.algo_session.initial_capital

    async def set_current_capital(self) -> None:
        self.current_capital = await self.get_current_capital()

    async def get_current_capital(self) -> float:
        initial_capital = self.algo_session.initial_capital
        position_pnl = self.algorithm.position_pnl["pnl"]
        used_margin = sum(
            [
                position.enter_price * position.quantities
                for position in self.algorithm.positions
            ]
        )

        return (initial_capital + position_pnl) - used_margin

    async def place_order(
        self,
        *,
        broker_symbol: BrokerSymbol,
        quantities: int,
        product_type: str,
        order_type: str,
        position_type: str,
        position_id: str | None,
    ) -> None:
        payload: Dict[str, Any] = {
            "order_id": str(uuid4()),
            "algo_session_id": self.algo_session.id,
            "broker_symbol_id": broker_symbol.id,
            "product_type": product_type,
            "order_type": order_type,
            "position_type": position_type,
            "position_id": position_id,
            "quantities": quantities,
            "price": broker_symbol.ltp,
            "status": "completed",
        }

        data = await self.api.create_order(payload=payload)

        order = Order(data, broker_symbol=broker_symbol, algorithm=self.algorithm)

        await order.initialize()

        await self.manage_position(order)

    async def get_enter_position_info(
        self, order: Order, position: Position | None
    ) -> Dict[str, Any]:
        if not position:
            return {
                "average_price": order.price,
                "position_id": str(uuid4()),
            }

        last_volume = position.enter_price * position.quantities

        current_volume = order.price * order.quantities

        total_volume = last_volume + current_volume

        total_quantities = position.quantities + order.quantities

        average_price = round(total_volume / total_quantities, 2)

        return {
            "average_price": average_price,
            "position_id": position.position_id,
        }

    async def get_exit_position_info(self, order: Order) -> Dict[str, Any]:
        return {
            "average_price": order.price,
            "position_id": order.position_id,
        }
