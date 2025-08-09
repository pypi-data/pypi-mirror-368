from abc import abstractmethod, ABC
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from proalgotrader_core.algo_session import AlgoSession
    from proalgotrader_core.api import Api


class BaseOrderBrokerManagerProtocol(ABC):
    @abstractmethod
    def __init__(self, api: "Api", algo_session: "AlgoSession") -> None: ...
