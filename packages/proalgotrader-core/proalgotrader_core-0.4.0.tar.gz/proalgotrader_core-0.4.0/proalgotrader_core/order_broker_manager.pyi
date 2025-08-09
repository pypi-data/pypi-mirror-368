from proalgotrader_core.algo_session import AlgoSession as AlgoSession
from proalgotrader_core.api import Api as Api
from proalgotrader_core.order_broker_managers.angel_one_order_broker_manager import AngelOneOrderBrokerManager as AngelOneOrderBrokerManager
from proalgotrader_core.order_broker_managers.base_order_broker_manager import BaseOrderBrokerManager as BaseOrderBrokerManager
from proalgotrader_core.order_broker_managers.fyers_order_broker_manager import FyersOrderBrokerManager as FyersOrderBrokerManager
from proalgotrader_core.order_broker_managers.paper_order_broker_manager import PaperOrderBrokerManager as PaperOrderBrokerManager
from proalgotrader_core.order_broker_managers.shoonya_order_broker_manager import ShoonyaOrderBrokerManager as ShoonyaOrderBrokerManager
from typing import Any

order_broker_managers: dict[str, Any]

class OrderBrokerManager:
    @staticmethod
    def get_instance(api: Api, algo_session: AlgoSession) -> BaseOrderBrokerManager: ...
