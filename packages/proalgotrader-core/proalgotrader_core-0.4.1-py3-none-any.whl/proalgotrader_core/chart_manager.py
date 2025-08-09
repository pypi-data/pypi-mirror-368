from datetime import timedelta
from typing import Dict, List, Tuple

from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.chart import Chart
from proalgotrader_core.order_broker_managers.base_order_broker_manager import (
    BaseOrderBrokerManager,
)


class ChartManager:
    def __init__(self, order_broker_manager: "BaseOrderBrokerManager") -> None:
        self.order_broker_manager = order_broker_manager
        self.api = self.order_broker_manager.api
        self.algo_session = self.order_broker_manager.algo_session

        self.__charts: Dict[Tuple[str, timedelta], Chart] = {}

    @property
    def charts(self) -> List[Chart]:
        return [chart for chart in self.__charts.values()]

    async def get_chart(
        self, broker_symbol: BrokerSymbol, timeframe: timedelta
    ) -> Chart | None:
        try:
            return self.__charts[(broker_symbol.base_symbol.key, timeframe)]
        except KeyError:
            return None

    async def register_chart(
        self, broker_symbol: BrokerSymbol, timeframe: timedelta
    ) -> Chart:
        try:
            exists = await self.get_chart(broker_symbol, timeframe)

            if exists:
                return exists
            else:
                chart = Chart(broker_symbol, timeframe, self)

                self.__charts[(broker_symbol.base_symbol.key, timeframe)] = chart

                return chart
        except Exception as e:
            raise Exception(e)
