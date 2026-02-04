
from __future__ import annotations

from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass(frozen=True)
class SlippageContext:
    pass

class SlippageModel(ABC):

    @abstractmethod
    def compute(
        self,
        *,
        side: OrderSide,
        context: SlippageContext,
    ) -> float:
        """
        Returns signed slippage in PRICE units.
        """
        raise NotImplementedError

class ConstantSlippageModel(SlippageModel):

    def __init__(
        self,
        *,
        slippage_pips: float,
        symbol: SymbolMetadata,
    ):
        if slippage_pips < 0:
            raise ValueError("slippage_pips must be >= 0")

        self._slippage_price = slippage_pips * symbol.pip_size

    def compute(
        self,
        *,
        side: OrderSide,
        context: SlippageContext,
    ) -> float:

        if side == OrderSide.BUY:
            return +self._slippage_price

        if side == OrderSide.SELL:
            return -self._slippage_price

        raise ValueError(f"Unsupported side: {side}")
