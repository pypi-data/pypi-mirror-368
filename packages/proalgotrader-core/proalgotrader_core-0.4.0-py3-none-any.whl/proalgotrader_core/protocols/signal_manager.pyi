import abc
from abc import ABC, abstractmethod
from proalgotrader_core.algorithm import Algorithm as Algorithm
from proalgotrader_core.protocols.enums.symbol_type import SymbolType as SymbolType

class SignalManagerProtocol(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def __init__(self, symbol_type: SymbolType, algorithm: Algorithm): ...
    @abstractmethod
    async def initialize(self) -> None: ...
    @abstractmethod
    async def next(self) -> None: ...
