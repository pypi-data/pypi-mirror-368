import requests
import json
import os
import threading
import pandas as pd

from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Dict, List
from websocket._app import WebSocketApp

from SmartApi import SmartConnect
from logzero import logger

from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.bar import Bar
from proalgotrader_core.base_symbol import BaseSymbol
from proalgotrader_core.broker_symbol import BrokerSymbol
from proalgotrader_core.data_broker_managers.base_data_broker_manager import (
    BaseDataBrokerManager,
)
from proalgotrader_core.token_managers.angel_one_token_manager import (
    AngelOneTokenManager,
)


class AngelOneDataBrokerManager(BaseDataBrokerManager, ABC):
    def __init__(self, api: Api, algo_session: AlgoSession) -> None:
        self.api = api
        self.algo_session = algo_session

        broker_config = self.algo_session.project.order_broker_info.broker_config

        print("AngelOneDataBrokerManager: getting token manager")

        self.token_manager = AngelOneTokenManager(
            client_id=broker_config["client_id"],
            totp_key=broker_config["totp_key"],
            mpin=broker_config["pin"],
            api_key=broker_config["api_key"],
            api_secret=broker_config["api_secret"],
            redirect_url=broker_config["redirect_url"],
        )

        self.http_client: SmartConnect = self.token_manager.http_client
        self.data_ws_url = self.algo_session.args_manager.data_ws_url
        self.ws_client = None
        self.connected = False

        self.resolutions = {
            timedelta(minutes=1): "ONE_MINUTE",
            timedelta(minutes=3): "THREE_MINUTE",
            timedelta(minutes=5): "FIVE_MINUTE",
            timedelta(minutes=15): "FIFTEEN_MINUTE",
            timedelta(minutes=30): "THIRTY_MINUTE",
            timedelta(hours=1): "ONE_HOUR",
            timedelta(hours=2): "TWO_HOUR",
            timedelta(hours=3): "THREE_HOUR",
            timedelta(hours=4): "FOUR_HOUR",
            timedelta(days=1): "ONE_DAY",
        }

        self.subscribers: List[BrokerSymbol] = []

        self.url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"

        home_directory = os.path.expanduser("~")

        self.file_path = f"{home_directory}/proalgotrader/data/instruments.json"

        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    @property
    def instrument_df(self) -> pd.DataFrame:
        return self.get_instrument_df()

    def check_and_update_file(self) -> None:
        try:
            with open(self.file_path) as file:
                json_content = json.load(file)
                last_downloaded = datetime.fromisoformat(
                    json_content["last_downloaded"]
                )

            if datetime.now() - last_downloaded > timedelta(hours=1):
                self.download_file()
        except (FileNotFoundError, json.JSONDecodeError):
            self.download_file()

    def download_file(self) -> None:
        print("Fetching data...")
        response = requests.get(self.url)
        response.raise_for_status()  # Raise an error on a failed request
        data = response.json()

        # Save the JSON data along with the current timestamp to the specified file
        with open(self.file_path, "w") as file:
            json.dump(
                {"last_downloaded": datetime.now().isoformat(), "data": data}, file
            )

    def get_instrument_df(self) -> pd.DataFrame:
        self.check_and_update_file()

        with open(self.file_path) as file:
            json_content = json.load(file)
            data = json_content["data"]

        return pd.DataFrame(data)

    def start_connection(self) -> None:
        market_status = self.algo_session.get_market_status()

        if market_status != "market_opened":
            return False

        print(f"🔗 Connecting to Django WebSocket: {self.data_ws_url}")

        self.ws_client = WebSocketApp(
            self.data_ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        thread = threading.Thread(target=self.ws_client.run_forever, daemon=True)

        thread.start()

    def close_connection(self) -> None:
        self.ws_client.close()

    def on_open(self, ws) -> None:
        self.connected = True
        logger.debug("✅ Connected to Django WebSocket")

    def on_close(self, ws, close_status_code, close_msg) -> None:
        logger.debug(f"🔌 WebSocket closed: {close_status_code} - {close_msg}")
        self.connected = False

    def on_error(self, ws, error) -> None:
        logger.debug(f"❌ WebSocket error: {error}")

    def on_message(self, ws, message) -> None:
        try:
            response = json.loads(message)

            data = response.get("data")

            if data["status"] != "success":
                logger.error(data["message"])
                return False

            ltp_data = data.get("data")

            if not ltp_data:
                return False

            # Extract LTP data
            last_traded_price = ltp_data.get("last_traded_price", 0)
            volume_trade_for_the_day = ltp_data.get("volume_trade_for_the_day", 0)
            token = ltp_data.get("token", 0)

            for subscriber in self.subscribers:
                if last_traded_price > 0 and subscriber.exchange_token == int(token):
                    ltp = last_traded_price / 100
                    subscriber.on_tick(ltp, volume_trade_for_the_day)
        except Exception as e:
            logger.debug(e)

    def subscribe(self, broker_symbol: BrokerSymbol) -> None:
        """Subscribe to a new symbol"""
        exchange_type = 1 if broker_symbol.segment_type == "Equity" else 2
        exchange_token = broker_symbol.exchange_token

        if self.connected and self.ws_client:
            subscription_message = {
                "command": "subscribe",
                "exchange_type": exchange_type,
                "exchange_token": exchange_token,
            }

            self.ws_client.send(json.dumps(subscription_message))

            self.subscribers.append(broker_symbol)

            broker_symbol.subscribed = True

            print("subscribed to", broker_symbol.symbol_name)

    def fetch_quotes(self, broker_symbol: BrokerSymbol) -> None:
        try:
            logger.debug(f"fetching quotes {broker_symbol.symbol_name}")

            response = self.http_client.getMarketData(
                mode="FULL",
                exchangeTokens={
                    "NSE" if broker_symbol.segment_type == "Equity" else "NFO": [
                        broker_symbol.exchange_token
                    ]
                },
            )

            if not response["data"]:
                raise Exception("Error fetching quotes", broker_symbol.symbol_name)

            data = response["data"]["fetched"][0]
            ltp = data.get("ltp")
            total_volume = data.get("tradeVolume")

            broker_symbol.on_bar(ltp, total_volume)
        except Exception as e:
            raise Exception(e)

    def fetch_bars(
        self,
        broker_symbol: BrokerSymbol,
        timeframe: timedelta,
        fetch_from: datetime,
        fetch_to: datetime,
    ) -> List[Bar]:
        try:
            historicDataParams = {
                "exchange": broker_symbol.base_symbol.exchange,
                "symboltoken": broker_symbol.exchange_token,
                "interval": self.resolutions[timeframe],
                "fromdate": fetch_from.strftime("%Y-%m-%d %H:%M"),
                "todate": fetch_to.strftime("%Y-%m-%d %H:%M"),
            }

            response = self.http_client.getCandleData(
                historicDataParams=historicDataParams
            )

            if not response["status"]:
                raise Exception("Error fetching candles")

            bars = [
                Bar(
                    broker_symbol=broker_symbol,
                    timestamp=int(datetime.fromisoformat(bar[0]).timestamp()),
                    open=bar[1],
                    high=bar[2],
                    low=bar[3],
                    close=bar[4],
                    volume=bar[5],
                )
                for bar in response["data"]
            ]

            return bars
        except Exception as e:
            raise Exception(e)

    def get_equity_symbol_name(
        self, broker_title: str, payload: Dict[str, Any], base_symbol: BaseSymbol
    ) -> Dict[str, Any]:
        instrumenttype = "AMXIDX" if base_symbol.type == "Index" else ""

        filtered_df = self.instrument_df[
            (self.instrument_df["name"] == base_symbol.value)
            & (self.instrument_df["instrumenttype"] == instrumenttype)
        ]

        return {
            "symbol_name": filtered_df.iloc[0]["symbol"],
            "symbol_token": filtered_df.iloc[0]["name"],
            "exchange_token": filtered_df.iloc[0]["token"],
        }

    def get_future_symbol_name(
        self, broker_title: str, payload: Dict[str, Any], base_symbol: BaseSymbol
    ) -> Dict[str, Any]:
        instrumenttype = "FUTIDX"

        expiry_date = (
            datetime.fromisoformat(payload["expiry_date"]).strftime("%d%b%Y").upper()
        )

        filtered_df = self.instrument_df[
            (self.instrument_df["name"] == base_symbol.value)
            & (self.instrument_df["instrumenttype"] == instrumenttype)
            & (self.instrument_df["expiry"] == expiry_date)
        ]

        return {
            "symbol_name": filtered_df.iloc[0]["symbol"],
            "symbol_token": filtered_df.iloc[0]["name"],
            "exchange_token": filtered_df.iloc[0]["token"],
        }

    def get_option_symbol_name(
        self, broker_title: str, payload: Dict[str, Any], base_symbol: BaseSymbol
    ) -> Dict[str, Any]:
        instrumenttype = "OPTIDX"

        expiry_date = (
            datetime.fromisoformat(payload["expiry_date"]).strftime("%d%b%Y").upper()
        )

        strike_price = format(payload["strike_price"] * 100, ".6f")

        filtered_df = self.instrument_df[
            (self.instrument_df["name"] == base_symbol.value)
            & (self.instrument_df["instrumenttype"] == instrumenttype)
            & (self.instrument_df["expiry"] == expiry_date)
            & (self.instrument_df["strike"] == strike_price)
            & (self.instrument_df["symbol"].str.contains(payload["option_type"]))
        ]

        if not len(filtered_df):
            raise Exception("Invalid symbol config")

        return {
            "symbol_name": filtered_df.iloc[0]["symbol"],
            "symbol_token": filtered_df.iloc[0]["name"],
            "exchange_token": filtered_df.iloc[0]["token"],
        }
