from enum import Enum


class ModelAmendOrderRequestAction(str, Enum):
    BUY = "buy"
    SELL = "sell"

    def __str__(self) -> str:
        return str(self.value)
