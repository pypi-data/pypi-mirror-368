from _typeshed import Incomplete
from datetime import timedelta
from proalgotrader_core.broker_symbol import BrokerSymbol as BrokerSymbol
from proalgotrader_core.chart import Chart as Chart
from proalgotrader_core.order_broker_managers.base_order_broker_manager import BaseOrderBrokerManager as BaseOrderBrokerManager

class ChartManager:
    order_broker_manager: Incomplete
    api: Incomplete
    algo_session: Incomplete
    def __init__(self, order_broker_manager: BaseOrderBrokerManager) -> None: ...
    @property
    def charts(self) -> list[Chart]: ...
    async def get_chart(self, broker_symbol: BrokerSymbol, timeframe: timedelta) -> Chart | None: ...
    async def register_chart(self, broker_symbol: BrokerSymbol, timeframe: timedelta) -> Chart: ...
