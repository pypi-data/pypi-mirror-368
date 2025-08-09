import abc
from abc import ABC, abstractmethod
from proalgotrader_core.algorithm import Algorithm as Algorithm

class StrategyProtocol(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def __init__(self, algorithm: Algorithm): ...
    @abstractmethod
    async def initialize(self) -> None: ...
    @abstractmethod
    async def next(self) -> None: ...
