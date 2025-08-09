import pandas as pd
from _typeshed import Incomplete
from datetime import datetime, timedelta
from proalgotrader_core.broker_symbol import BrokerSymbol as BrokerSymbol
from proalgotrader_core.chart_manager import ChartManager as ChartManager
from proalgotrader_core.protocols.enums.segment_type import SegmentType as SegmentType

class Chart:
    broker_symbol: Incomplete
    timeframe: Incomplete
    chart_manager: Incomplete
    algo_session: Incomplete
    order_broker_manager: Incomplete
    def __init__(self, broker_symbol: BrokerSymbol, timeframe: timedelta, chart_manager: ChartManager) -> None: ...
    @property
    def current_candle(self) -> datetime: ...
    @property
    def ltp(self) -> float: ...
    @property
    def data(self) -> pd.DataFrame: ...
    next_candle_datetime: Incomplete
    async def is_new_candle(self) -> bool: ...
    async def next(self) -> None: ...
