from abc import ABC
from typing import Dict, Any

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
from proalgotrader_core.token_managers.fyers_token_manager import FyersTokenManager
from asyncio import sleep


class FyersOrderBrokerManager(BaseOrderBrokerManager, ABC):
    def __init__(self, api: Api, algo_session: AlgoSession) -> None:
        super().__init__(api=api, algo_session=algo_session)

        broker_config = self.algo_session.project.order_broker_info.broker_config

        print("FyersBroker: getting token manager")

        self.token_manager = FyersTokenManager(
            username=broker_config["username"],
            totp_key=broker_config["totp_key"],
            pin=broker_config["pin"],
            client_id=broker_config["client_id"],
            secret_key=broker_config["secret_key"],
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
        funds = self.token_manager.http_client.funds()

        if not funds["fund_limit"]:
            self.initial_capital = self.algo_session.initial_capital
        else:
            self.initial_capital = funds["fund_limit"][8]["equityAmount"]

    async def set_current_capital(self) -> None:
        funds = self.token_manager.http_client.funds()

        if not funds["fund_limit"]:
            self.current_capital = self.algo_session.current_capital
        else:
            self.current_capital = funds["fund_limit"][0]["equityAmount"]

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
        assert (
            self.token_manager.http_client is not None
        ), "http_client must not be None"

        order_types = await self.get_order_types()
        position_types = await self.get_position_types()
        product_types = await self.get_product_types()

        data = {
            "symbol": broker_symbol.symbol_name,
            "qty": quantities,
            "type": order_types[order_type],
            "side": position_types[position_type],
            "productType": product_types[product_type],
            "limitPrice": 0,
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": False,
            "orderTag": "tag1",
        }

        response = self.token_manager.http_client.place_order(data=data)

        orders_data = self.token_manager.http_client.orderbook(
            data={"id": response["id"]}
        )

        order_data = orders_data["orderBook"][0]

        payload: Dict[str, Any] = {
            "order_id": order_data["id"],
            "algo_session_id": self.algo_session.id,
            "broker_symbol_id": broker_symbol.id,
            "market_type": market_type,
            "product_type": product_type,
            "order_type": order_type,
            "position_type": position_type,
            "position_id": position_id,
            "quantities": quantities,
            "price": round(order_data["tradedPrice"], 4),
            "status": "completed",
        }

        data = await self.api.create_order(payload=payload)

        order = Order(data, broker_symbol=broker_symbol, algorithm=self.algorithm)

        await order.initialize()

        await self.manage_position(order)

    async def get_enter_position_info(
        self, order: Order, position: Position | None
    ) -> Dict[str, Any]:
        assert (
            self.token_manager.http_client is not None
        ), "http_client must not be None"

        position_types = await self.get_position_types()

        product_types = await self.get_product_types()

        while True:
            await sleep(1)

            positions = self.token_manager.http_client.positions()

            netPositions = [
                netPosition
                for netPosition in positions["netPositions"]
                if netPosition["symbol"] == order.broker_symbol.symbol_name
                and netPosition["side"] == position_types[order.position_type]
                and netPosition["productType"] == product_types[order.product_type]
            ]

            if netPositions:
                break
            else:
                continue

        return {
            "average_price": round(netPositions[0]["netAvg"], 4),
            "position_id": netPositions[0]["id"],
        }

    async def get_exit_position_info(self, order: Order) -> Dict[str, Any]:
        return {
            "average_price": order.price,
            "position_id": order.position_id,
        }
