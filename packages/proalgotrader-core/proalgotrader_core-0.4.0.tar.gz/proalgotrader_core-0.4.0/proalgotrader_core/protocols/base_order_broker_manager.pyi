import abc
from abc import ABC, abstractmethod
from proalgotrader_core.algo_session import AlgoSession as AlgoSession
from proalgotrader_core.api import Api as Api

class BaseOrderBrokerManagerProtocol(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def __init__(self, api: Api, algo_session: AlgoSession): ...
