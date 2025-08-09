from typing import Any, Literal

class BaseSymbol:
    id: int
    exchange: str
    key: str
    value: str
    type: str
    lot_size: int
    strike_size: int
    weekly_expiry_day: str | None
    monthly_expiry_day: str | None
    def __init__(self, base_symbol_info: dict[str, Any]) -> None: ...
    def get_expiry_day(self, expiry_period: Literal['Weekly', 'Monthly']) -> str: ...
