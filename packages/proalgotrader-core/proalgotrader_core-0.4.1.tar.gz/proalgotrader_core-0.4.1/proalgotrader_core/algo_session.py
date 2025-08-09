import json
import pandas as pd
import pytz

from pathlib import Path
from time import sleep
from datetime import date, datetime, time, timedelta
from typing import List, Literal, Tuple, Dict, Any, TYPE_CHECKING
from logzero import logger

from proalgotrader_core._helpers.get_data_path import get_data_path
from proalgotrader_core.args_manager import ArgsManager
from proalgotrader_core.project import Project

if TYPE_CHECKING:
    from proalgotrader_core.algorithm import Algorithm


class AlgoSession:
    def __init__(
        self,
        args_manager: ArgsManager,
        algo_session_info: Dict[str, Any],
        algorithm: "Algorithm",
    ):
        self.args_manager = args_manager
        self.id: int = algo_session_info["id"]
        self.key: str = algo_session_info["key"]
        self.secret: str = algo_session_info["secret"]
        self.mode: Literal["Paper", "Live"] = algo_session_info["mode"]
        self.tz: str = algo_session_info["tz"]

        self.project: Project = Project(algo_session_info["project"])

        self.algorithm = algorithm

        self.initial_capital: float = 10_00_000
        self.current_capital: float = 10_00_000

        self.tz_info = pytz.timezone(self.tz)

        self.market_start_time = time(9, 15)

        self.market_end_time = time(15, 30)

        self.market_start_datetime = datetime.now(tz=self.tz_info).replace(
            hour=self.market_start_time.hour,
            minute=self.market_start_time.minute,
            second=0,
            microsecond=0,
            tzinfo=None,
        )

        self.market_end_datetime = datetime.now(tz=self.tz_info).replace(
            hour=self.market_end_time.hour,
            minute=self.market_end_time.minute,
            second=0,
            microsecond=0,
            tzinfo=None,
        )

        self.resample_days = {
            "Monday": "W-MON",
            "Tuesday": "W-TUE",
            "Wednesday": "W-WED",
            "Thursday": "W-THU",
            "Friday": "W-FRI",
        }

        self.warmup_days = {
            timedelta(minutes=1): 2,
            timedelta(minutes=3): 4,
            timedelta(minutes=5): 6,
            timedelta(minutes=15): 16,
            timedelta(minutes=30): 32,
            timedelta(hours=1): 60,
            timedelta(hours=2): 100,
            timedelta(hours=3): 150,
            timedelta(hours=4): 200,
            timedelta(days=1): 400,
        }

        self.data_path = get_data_path(self.current_datetime)

        self.trading_days = self.__get_trading_days(self.data_path)

    @property
    def current_datetime(self) -> datetime:
        return datetime.now(tz=self.tz_info).replace(
            microsecond=0,
            tzinfo=None,
        )

    @property
    def current_timestamp(self) -> int:
        return int(self.current_datetime.timestamp())

    @property
    def current_date(self) -> date:
        return self.current_datetime.date()

    @property
    def current_time(self) -> time:
        return self.current_datetime.time()

    def get_market_status(self) -> str:
        try:
            if (
                self.current_datetime.strftime("%Y-%m-%d")
                not in self.trading_days.index
            ):
                return "trading_closed"

            if self.current_datetime <= self.market_start_datetime:
                return "before_market_opened"

            if self.current_datetime > self.market_end_datetime:
                return "after_market_closed"

            return "market_opened"
        except Exception as e:
            raise Exception(e)

    def validate_market_status(self) -> None:
        try:
            while True:
                market_status = self.get_market_status()

                if market_status == "trading_closed":
                    raise Exception("trading is closed")
                elif market_status == "after_market_closed":
                    raise Exception("market is closed")
                elif market_status == "before_market_opened":
                    logger.debug("market is not opened yet")
                    sleep(1)
                else:
                    break
        except Exception as e:
            raise Exception(e)

    def get_expires(
        self, expiry_period: Literal["Weekly", "Monthly"], expiry_day: str
    ) -> pd.DataFrame:
        if expiry_period == "Weekly":
            return self.__get_weekly_expiries(expiry_day)
        else:
            return self.__get_monthly_expiries(expiry_day)

    def __get_weekly_expiries(self, expiry_day: str) -> pd.DataFrame:
        file = f"{self.data_path}/Weekly_{expiry_day}.csv"

        try:
            return pd.read_csv(file, index_col="index", parse_dates=True)
        except FileNotFoundError:
            trading_days = self.trading_days.copy()

            weekends = trading_days.resample(self.resample_days[expiry_day]).last()

            weekends.index = weekends["date"]

            weekends.to_csv(file, index_label="index")

        return pd.read_csv(file, index_col="index", parse_dates=True)

    def __get_monthly_expiries(self, expiry_day: str) -> pd.DataFrame:
        file = f"{self.data_path}/Monthly_{expiry_day}.csv"

        try:
            return pd.read_csv(file, index_col="index", parse_dates=True)
        except FileNotFoundError:
            weekends: pd.DataFrame = self.__get_weekly_expiries(expiry_day)

            datetime_index: pd.DatetimeIndex = pd.DatetimeIndex(weekends.index)

            df_grouped = weekends.groupby(
                by=[datetime_index.year, datetime_index.month],
                as_index=True,
                dropna=True,
            ).last()

            json_data = json.loads(df_grouped.to_json())

            def get_data(date: str) -> List[Any]:
                datetime_obj = datetime.fromisoformat(date)

                return [date, datetime_obj.strftime("%A"), datetime_obj.year]

            data = [get_data(date) for date in json_data["date"].values()]

            new_df = pd.DataFrame(data, columns=["date", "day", "year"])

            new_df["index"] = pd.to_datetime(new_df["date"])

            new_df.set_index("index", inplace=True)

            new_df.to_csv(file, index_label="index")

            return pd.read_csv(file, index_col="index", parse_dates=True)

    def get_warmups_days(self, timeframe: timedelta) -> int:
        try:
            return self.warmup_days[timeframe]
        except KeyError:
            raise Exception("Invalid timeframe")

    def fetch_ranges(self, timeframe: timedelta) -> Tuple[datetime, datetime]:
        warmups_days = self.get_warmups_days(timeframe)

        warmups_from: str = str(
            (
                self.trading_days[
                    self.trading_days.index < self.current_datetime.strftime("%Y-%m-%d")
                ]
                .tail(warmups_days)
                .head(1)
                .index[0]
            )
        )

        fetch_from_epoch = datetime.fromisoformat(warmups_from).replace(
            hour=self.market_start_time.hour,
            minute=self.market_start_time.minute,
            second=self.market_start_time.second,
            microsecond=0,
        )

        return fetch_from_epoch, self.current_datetime

    def get_current_candle(self, timeframe: timedelta) -> datetime:
        try:
            if timeframe == timedelta(days=1):
                return datetime.now(tz=self.tz_info).replace(
                    hour=5,
                    minute=30,
                    second=0,
                    microsecond=0,
                    tzinfo=None,
                )

            current_candle_timedelta: timedelta = (
                self.current_datetime - self.market_start_datetime
            )

            seconds, _ = divmod(
                int(current_candle_timedelta.seconds), int(timeframe.total_seconds())
            )

            return self.market_start_datetime + timedelta(
                seconds=seconds * timeframe.total_seconds()
            )
        except Exception as e:
            raise Exception(e)

    def __get_trading_days(self, data_path: Path) -> pd.DataFrame:
        file = f"{data_path}/trading_days.csv"

        try:
            return pd.read_csv(file, index_col="index", parse_dates=["index", "date"])
        except FileNotFoundError:
            trading_days = self.algorithm.api.get_trading_days()

            def get_json(date: str) -> Dict[str, Any]:
                dt = datetime.strptime(date, "%Y-%m-%d")

                return {
                    "date": dt.strftime("%Y-%m-%d"),
                    "day": dt.strftime("%A"),
                    "year": dt.year,
                }

            df = pd.DataFrame(
                data=[get_json(trading_day["date"]) for trading_day in trading_days],
                columns=["date", "day", "year"],
            )

            df["index"] = pd.to_datetime(df["date"])

            df.set_index(["index"], inplace=True)

            df.to_csv(file, index_label="index")

        return pd.read_csv(file, index_col="index", parse_dates=["index", "date"])
