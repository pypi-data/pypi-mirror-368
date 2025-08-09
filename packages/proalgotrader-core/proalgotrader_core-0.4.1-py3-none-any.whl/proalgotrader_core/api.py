from typing import Any, Dict

import requests
from logzero import logger
from requests import Response

from proalgotrader_core.args_manager import ArgsManager


class Api:
    def __init__(self, args_manager: ArgsManager) -> None:
        self.args_manager = args_manager

        self.algo_session_key = args_manager.algo_session_key
        self.algo_session_secret = args_manager.algo_session_secret
        self.environment = args_manager.environment
        self.api_url = args_manager.api_url

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        self.token = None

    def __make_request(
        self,
        method: str,
        url: str,
        *,
        data: Dict[str, Any] | None = None,
        json: Dict[str, Any] | None = None,
        source: str | None = None,
    ) -> Response:
        try:
            logger.debug(f"making api request to {url} from source: {source}")

            return requests.request(
                method=method,
                url=url,
                data=data,
                json=json,
                headers=self.headers,
            )
        except Exception as e:
            raise Exception(e)

    def get_algo_session_info(self) -> Any:
        try:
            info_url = f"{self.api_url}/api/algo-sessions/info"

            response = self.__make_request(
                method="post",
                url=info_url,
                json={
                    "algo_session_key": self.algo_session_key,
                    "algo_session_secret": self.algo_session_secret,
                },
            )

            json = response.json()

            if not response.ok:
                raise Exception(json)

            self.token = json["token"]

            self.headers["Authorization"] = f"Bearer {self.token}"

            return json
        except Exception as e:
            raise Exception(e)

    def get_github_access_token(self, github_account_id: int) -> Any:
        try:
            algo_session_info_url = (
                f"{self.api_url}/api/github/accounts/{github_account_id}/access-token"
            )

            response = self.__make_request(method="get", url=algo_session_info_url)

            json = response.json()

            if not response.ok:
                raise Exception(json)

            return json["access_token"]
        except Exception as e:
            raise Exception(e)

    def get_trading_days(self) -> Any:
        try:
            trading_days_url = f"{self.api_url}/api/trading-days/list"

            response = self.__make_request(method="get", url=trading_days_url)

            json = response.json()

            if not response.ok:
                raise Exception(json)

            return json["trading_days"]
        except Exception as e:
            raise Exception(e)

    def get_base_symbols(self) -> Any:
        try:
            base_symbols_url = f"{self.api_url}/api/base-symbols/list"

            response = self.__make_request(method="get", url=base_symbols_url)

            json = response.json()

            if not response.ok:
                raise Exception(json)

            return json["base_symbols"]
        except Exception as e:
            raise Exception(e)

    def get_broker_symbols(self, broker_title: str, payload: Dict[str, Any]) -> Any:
        try:
            broker_symbols_url = (
                f"{self.api_url}/api/broker-symbols/{broker_title}/info"
            )

            response = self.__make_request(
                method="get",
                url=broker_symbols_url,
                json=payload,
                source="get_broker_symbols",
            )

            json = response.json()

            if not response.ok:
                raise Exception(json)

            return json["broker_symbol"]
        except Exception as e:
            raise Exception(e)

    def add_broker_symbols(self, broker_title: str, payload: Dict[str, Any]) -> Any:
        try:
            broker_symbols_url = (
                f"{self.api_url}/api/broker-symbols/{broker_title}/info"
            )

            response = self.__make_request(
                method="post",
                url=broker_symbols_url,
                json=payload,
                source="add_broker_symbols",
            )

            json = response.json()

            if not response.ok:
                raise Exception(json)

            return json["broker_symbol"]
        except Exception as e:
            raise Exception(e)

    def get_orders(self) -> Any:
        try:
            get_orders_url = (
                f"{self.api_url}/api/algo-sessions/{self.algo_session_key}/orders/list"
            )

            response = self.__make_request(method="get", url=get_orders_url)

            json = response.json()

            if not response.ok:
                raise Exception(json)

            return json["orders"]
        except Exception as e:
            raise Exception(e)

    def get_positions(self) -> Any:
        try:
            get_positions_url = f"{self.api_url}/api/algo-sessions/{self.algo_session_key}/positions/list"

            response = self.__make_request(method="get", url=get_positions_url)

            json = response.json()

            if not response.ok:
                raise Exception(json)

            return json["positions"]
        except Exception as e:
            raise Exception(e)

    async def create_order(self, payload: Dict[str, Any]) -> Any:
        try:
            create_order_url = f"{self.api_url}/api/algo-sessions/{self.algo_session_key}/orders/create"

            response = self.__make_request(
                method="post", url=create_order_url, json=payload
            )

            json = response.json()

            if not response.ok:
                raise Exception(json)

            return json["order"]
        except Exception as e:
            raise Exception(e)

    async def enter_position(self, payload: Dict[str, Any]) -> Any:
        try:
            manage_position_url = f"{self.api_url}/api/algo-sessions/{self.algo_session_key}/positions/enter"

            response = self.__make_request(
                method="post", url=manage_position_url, json=payload
            )

            json = response.json()

            if not response.ok:
                raise Exception(json)

            return json["position"]
        except Exception as e:
            raise Exception(e)

    async def exit_position(self, payload: Dict[str, Any]) -> Any:
        try:
            manage_position_url = f"{self.api_url}/api/algo-sessions/{self.algo_session_key}/positions/exit"

            response = self.__make_request(
                method="post", url=manage_position_url, json=payload
            )

            json = response.json()

            if not response.ok:
                raise Exception(json)

            return json["position"]
        except Exception as e:
            raise Exception(e)

    def get_risk_reward(self, position_id: str, payload: Dict[str, Any]) -> Any:
        try:
            if not position_id:
                raise Exception("Position Id is required to get risk reward")

            url = f"{self.api_url}/api/algo-sessions/{self.algo_session_key}/risk-rewards/{position_id}/info"

            response = self.__make_request(
                method="get",
                url=url,
                json=payload,
            )

            json = response.json()

            if not response.ok:
                raise Exception(json)

            return json["risk_reward"]
        except Exception as e:
            raise Exception(e)

    def create_risk_reward(self, position_id: str, payload: Dict[str, Any]) -> Any:
        try:
            if not position_id:
                raise Exception("Position Id is required to create risk reward")

            url = f"{self.api_url}/api/algo-sessions/{self.algo_session_key}/risk-rewards/{position_id}/create"

            response = self.__make_request(
                method="post",
                url=url,
                json=payload,
            )

            json = response.json()

            if not response.ok:
                raise Exception(json)

            return json["risk_reward"]
        except Exception as e:
            raise Exception(e)
