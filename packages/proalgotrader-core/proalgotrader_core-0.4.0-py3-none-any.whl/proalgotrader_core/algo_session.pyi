import pandas as pd
from _typeshed import Incomplete
from datetime import date, datetime, time, timedelta
from proalgotrader_core._helpers.get_data_path import get_data_path as get_data_path
from proalgotrader_core.algorithm import Algorithm as Algorithm
from proalgotrader_core.args_manager import ArgsManager as ArgsManager
from proalgotrader_core.project import Project as Project
from typing import Any, Literal

class AlgoSession:
    args_manager: Incomplete
    id: int
    key: str
    secret: str
    mode: Literal['Paper', 'Live']
    tz: str
    project: Project
    algorithm: Incomplete
    initial_capital: float
    current_capital: float
    tz_info: Incomplete
    market_start_time: Incomplete
    market_end_time: Incomplete
    market_start_datetime: Incomplete
    market_end_datetime: Incomplete
    resample_days: Incomplete
    warmup_days: Incomplete
    data_path: Incomplete
    trading_days: Incomplete
    def __init__(self, args_manager: ArgsManager, algo_session_info: dict[str, Any], algorithm: Algorithm) -> None: ...
    @property
    def current_datetime(self) -> datetime: ...
    @property
    def current_timestamp(self) -> int: ...
    @property
    def current_date(self) -> date: ...
    @property
    def current_time(self) -> time: ...
    def get_market_status(self) -> str: ...
    def validate_market_status(self) -> None: ...
    def get_expires(self, expiry_period: Literal['Weekly', 'Monthly'], expiry_day: str) -> pd.DataFrame: ...
    def get_warmups_days(self, timeframe: timedelta) -> int: ...
    def fetch_ranges(self, timeframe: timedelta) -> tuple[datetime, datetime]: ...
    def get_current_candle(self, timeframe: timedelta) -> datetime: ...
