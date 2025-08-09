from abc import abstractmethod
from typing import Any, Dict, List

from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.base_symbol import BaseSymbol
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.data_broker_managers.angel_one_data_broker_manager import (
    AngelOneDataBrokerManager,
)
from proalgotrader_core.data_broker_managers.base_data_broker_manager import (
    BaseDataBrokerManager,
)
from proalgotrader_core.data_broker_managers.fyers_data_broker_manager import (
    FyersDataBrokerManager,
)
from proalgotrader_core.order import Order
from proalgotrader_core.position import Position
from proalgotrader_core.protocols.base_order_broker_manager import (
    BaseOrderBrokerManagerProtocol,
)


data_broker_managers: Dict[str, Any] = {
    "fyers": FyersDataBrokerManager,
    "angel-one": AngelOneDataBrokerManager,
}


class BaseOrderBrokerManager(BaseOrderBrokerManagerProtocol):
    def __init__(self, api: Api, algo_session: AlgoSession) -> None:
        self.api = api
        self.algo_session = algo_session
        self.algorithm = algo_session.algorithm
        self.algo_session_broker = algo_session.project.order_broker_info

        self.id = self.algo_session_broker.id
        self.broker_uid = self.algo_session_broker.broker_uid
        self.broker_title = self.algo_session_broker.broker_title
        self.broker_name = self.algo_session_broker.broker_name
        self.broker_config = self.algo_session_broker.broker_config

        self.base_symbols: Dict[str, BaseSymbol] = {}
        self.broker_symbols: Dict[Any, BrokerSymbol] = {}

        self.initial_capital: float = 0
        self.current_capital: float = 0

        self.__orders: List[Order] = []
        self.__positions: List[Position] = []

        self.data_manager: BaseDataBrokerManager = AngelOneDataBrokerManager(
            api=self.api,
            algo_session=self.algo_session,
        )

    @property
    def orders(self) -> List[Order]:
        return self.__orders

    @property
    def positions(self) -> List[Position]:
        return self.__positions

    @property
    def open_positions(self) -> List[Position]:
        return [position for position in self.__positions if position.status == "open"]

    def initialize(self) -> None:
        base_symbols = self.api.get_base_symbols()

        self.base_symbols = {
            base_symbol["key"]: BaseSymbol(base_symbol) for base_symbol in base_symbols
        }

    async def get_order_info(self, data: Dict[str, Any]) -> Order:
        broker_symbol = self.get_symbol(data["broker_symbol"])

        order = Order(data, broker_symbol=broker_symbol, algorithm=self.algorithm)

        await order.initialize()

        return order

    async def get_position_info(self, data: Dict[str, Any]) -> Position:
        broker_symbol = self.get_symbol(data["broker_symbol"])

        position = Position(data, broker_symbol=broker_symbol, algorithm=self.algorithm)

        if self.algorithm.position_manager and position.status == "open":
            position_manager = self.algorithm.position_manager(
                algorithm=self.algorithm, position=position
            )

            await position_manager.initialize()

            self.algorithm.position_managers.append(position_manager)

        return position

    async def set_orders(self) -> None:
        orders = self.api.get_orders()

        self.__orders = [await self.get_order_info(order) for order in orders]

    async def set_positions(self) -> None:
        try:
            positions = self.api.get_positions()

            self.__positions = [
                await self.get_position_info(position) for position in positions
            ]
        except Exception as e:
            print(e, "error happened")

    async def on_after_market_closed(self) -> None:
        for position in self.positions:
            await position.on_after_market_closed()

        self.data_manager.close_connection()

    def add_equity(
        self,
        *,
        base_symbol: BaseSymbol,
        market_type: str,
        segment_type: str,
    ) -> BrokerSymbol:
        try:
            data = {
                "base_symbol_id": base_symbol.id,
                "exchange": base_symbol.exchange,
                "market_type": market_type,
                "segment_type": segment_type,
                "expiry_period": None,
                "expiry_date": None,
                "strike_price": None,
                "option_type": None,
            }

            broker_symbol = self.get_symbol(data)

            return broker_symbol
        except Exception as e:
            raise Exception(e)

    def add_future(
        self,
        *,
        base_symbol: BaseSymbol,
        market_type: str,
        segment_type: str,
        expiry_period: str,
        expiry_date: str,
    ) -> BrokerSymbol:
        try:
            data = {
                "base_symbol_id": base_symbol.id,
                "exchange": base_symbol.exchange,
                "market_type": market_type,
                "segment_type": segment_type,
                "expiry_period": expiry_period,
                "expiry_date": expiry_date,
                "strike_price": None,
                "option_type": None,
            }

            broker_symbol = self.get_symbol(data)

            return broker_symbol
        except Exception as e:
            raise Exception(e)

    def add_option(
        self,
        *,
        base_symbol: BaseSymbol,
        market_type: str,
        segment_type: str,
        expiry_period: str,
        expiry_date: str,
        strike_price: int,
        option_type: str,
    ) -> BrokerSymbol:
        try:
            data = {
                "base_symbol_id": base_symbol.id,
                "exchange": base_symbol.exchange,
                "market_type": market_type,
                "segment_type": segment_type,
                "expiry_period": expiry_period,
                "expiry_date": expiry_date,
                "strike_price": strike_price,
                "option_type": option_type,
            }

            broker_symbol = self.get_symbol(data)

            return broker_symbol
        except Exception as e:
            raise Exception(e)

    def get_symbol(
        self,
        broker_symbol_info: Dict[str, Any],
    ) -> BrokerSymbol:
        base_symbol_id = broker_symbol_info["base_symbol_id"]
        exchange = broker_symbol_info["exchange"]
        market_type = broker_symbol_info["market_type"]
        segment_type = broker_symbol_info["segment_type"]
        expiry_period = broker_symbol_info["expiry_period"]
        expiry_date = broker_symbol_info["expiry_date"]
        strike_price = broker_symbol_info["strike_price"]
        option_type = broker_symbol_info["option_type"]

        key = (
            base_symbol_id,
            exchange,
            market_type,
            segment_type,
            expiry_period,
            expiry_date,
            strike_price,
            option_type,
        )

        try:
            return self.broker_symbols[key]
        except KeyError:
            payload = {
                "base_symbol_id": base_symbol_id,
                "exchange": exchange,
                "market_type": market_type,
                "segment_type": segment_type,
                "expiry_period": expiry_period,
                "expiry_date": expiry_date,
                "strike_price": strike_price,
                "option_type": option_type,
            }

            if "id" not in broker_symbol_info:
                filtered_base_symbols = [
                    value
                    for value in self.base_symbols.values()
                    if value.id == base_symbol_id
                ]

                if not filtered_base_symbols:
                    raise Exception("Invalid Base Symbol")

                broker_symbol_info = self.data_manager.get_broker_symbols(
                    broker_title=self.broker_title,
                    payload=payload,
                    base_symbol=filtered_base_symbols[0],
                )

            broker_symbol = BrokerSymbol(broker_symbol_info, algorithm=self.algorithm)

            self.broker_symbols[key] = broker_symbol

            return broker_symbol

    def get_positions(
        self,
        symbol_name: str,
        market_type: str,
        order_type: str,
        product_type: str,
        position_type: str,
    ) -> List[Position]:
        return [
            position
            for position in self.positions
            if (
                position.broker_symbol.symbol_name == symbol_name
                and position.broker_symbol.market_type == market_type
                and position.order_type == order_type
                and position.product_type == product_type
                and position.position_type == position_type
            )
        ]

    async def manage_position(self, order: Order) -> None:
        try:
            self.__orders.append(order)

            if not order.position_id:
                await self.enter_position(order)
            else:
                await self.exit_position(order)
        except Exception as e:
            raise Exception(e)

    async def enter_position(self, order: Order) -> None:
        positions = self.get_positions(
            order.broker_symbol.symbol_name,
            order.broker_symbol.market_type,
            order.order_type,
            order.product_type,
            order.position_type,
        )

        enter_position_info = await self.get_enter_position_info(
            order, positions[-1] if positions else None
        )

        average_price: float = enter_position_info["average_price"]

        position_id: str = enter_position_info["position_id"]

        payload: Dict[str, Any] = {
            "position_id": position_id,
            "algo_session_id": self.algo_session.id,
            "broker_symbol_id": order.broker_symbol.id,
            "product_type": order.product_type,
            "order_type": order.order_type,
            "position_type": order.position_type,
            "quantities": order.quantities,
            "enter_price": average_price,
            "exit_price": None,
            "status": "open",
        }

        data = await self.api.enter_position(payload)

        position = Position(
            data, broker_symbol=order.broker_symbol, algorithm=self.algorithm
        )

        if self.algorithm.position_manager and position.status == "open":
            position_manager = self.algorithm.position_manager(
                algorithm=self.algorithm, position=position
            )

            await position_manager.initialize()

            self.algorithm.position_managers.append(position_manager)

        self.__positions.append(position)

    async def exit_position(self, order: Order) -> None:
        exit_position_info = await self.get_exit_position_info(order)

        average_price: float = exit_position_info["average_price"]
        position_id: str = exit_position_info["position_id"]

        position = [
            position
            for position in self.positions
            if position.position_id == position_id
        ][0]

        position.enter_price = position.enter_price
        position.exit_price = average_price
        position.status = "closed"

        self.__positions = [
            position for position in self.__positions if position.id != position_id
        ]

        payload: Dict[str, Any] = {
            "position_id": position_id,
            "algo_session_id": self.algo_session.id,
            "broker_symbol_id": position.broker_symbol.id,
            "product_type": position.product_type,
            "order_type": position.order_type,
            "position_type": position.position_type,
            "quantities": position.quantities,
            "enter_price": position.enter_price,
            "exit_price": average_price,
            "status": "closed",
        }

        await self.api.exit_position(payload)

        self.algorithm.position_managers = [
            pm
            for pm in self.algorithm.position_managers
            if pm.position.id != position_id
        ]

        self.__positions.append(position)

    async def next(self) -> None:
        for position in self.positions:
            await position.next()

    @abstractmethod
    async def get_product_types(self) -> Dict[Any, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_order_types(self) -> Dict[Any, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_position_types(self) -> Dict[Any, Any]:
        raise NotImplementedError

    @abstractmethod
    async def set_initial_capital(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def set_current_capital(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_enter_position_info(
        self, order: Order, position: Position | None
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_exit_position_info(self, order: Order) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError
