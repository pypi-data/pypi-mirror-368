from typing import Any, Dict
from proalgotrader_core.algo_session import AlgoSession
from proalgotrader_core.api import Api
from proalgotrader_core.base_symbol import BaseSymbol
from proalgotrader_core.protocols.base_data_broker_manager import (
    BaseDataBrokerManagerProtocol,
)


class BaseDataBrokerManager(BaseDataBrokerManagerProtocol):
    def __init__(self, api: Api, algo_session: AlgoSession) -> None:
        self.api = api
        self.algo_session = algo_session

    def get_broker_symbols(
        self, broker_title: str, payload: Dict[str, Any], base_symbol: BaseSymbol
    ) -> Dict[str, Any]:
        broker_symbol_exist: Dict[str, Any] = self.api.get_broker_symbols(
            broker_title=broker_title, payload=payload
        )

        if broker_symbol_exist:
            return broker_symbol_exist

        segment_type: str = payload["segment_type"]

        action_name = f"get_{segment_type.lower()}_symbol_name"

        action = getattr(self, action_name)

        data = action(broker_title, payload, base_symbol)

        add_broker_symbol: Dict[str, Any] = self.api.add_broker_symbols(
            broker_title=broker_title, payload={**payload, **data}
        )

        return add_broker_symbol
