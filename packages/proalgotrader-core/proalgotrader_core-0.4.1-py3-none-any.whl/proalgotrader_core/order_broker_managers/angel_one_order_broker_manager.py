from abc import ABC
from typing import Any, Dict

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
from proalgotrader_core.token_managers.angel_one_token_manager import (
    AngelOneTokenManager,
)


class AngelOneOrderBrokerManager(BaseOrderBrokerManager, ABC):
    def __init__(self, api: Api, algo_session: AlgoSession) -> None:
        super().__init__(api=api, algo_session=algo_session)

        broker_config = self.algo_session.project.order_broker_info.broker_config

        self.token_manager = AngelOneTokenManager(
            client_id=broker_config["client_id"],
            totp_key=broker_config["totp_key"],
            mpin=broker_config["mpin"],
            api_key=broker_config["api_key"],
            api_secret=broker_config["api_secret"],
            redirect_url=broker_config["redirect_url"],
        )

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
        self.current_capital = self.algo_session.current_capital

    async def place_order(
        self,
        *,
        broker_symbol: BrokerSymbol,
        quantities: int,
        market_type: str,
        product_type: str,
        order_type: str,
        position_type: str,
        position_id: str | None,
    ) -> None:
        pass

    async def get_enter_position_info(
        self, order: Order, position: Position | None
    ) -> Dict[str, Any]:
        raise NotImplementedError

    async def get_exit_position_info(self, order: Order) -> Dict[str, Any]:
        raise NotImplementedError
