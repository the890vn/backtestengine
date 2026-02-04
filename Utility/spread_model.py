
from __future__ import annotations

from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class Bar:
    open: float
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class BidAskBar:
    bid: Bar
    ask: Bar


@dataclass(frozen=True)
class SpreadContext:
    """
    Context passed to SpreadModel.

    Currently unused, but intentionally exists to support:
    - dynamic spread
    - ATR-based spread
    - session-based spread
    - volatility regime
    """
    pass


class SpreadModel(ABC):
    @abstractmethod
    def apply(
        self,
        *,
        mid_bar: Bar,
        context: SpreadContext,
    ) -> BidAskBar:
        raise NotImplementedError


class ConstantSpreadModel(SpreadModel):
    def __init__(self, spread: float):
        if spread < 0:
            raise ValueError("Spread must be non-negative")

        self._half_spread = spread / 2.0

    def apply(
        self,
        *,
        mid_bar: Bar,
        context: SpreadContext,
    ) -> BidAskBar:

        hs = self._half_spread

        bid = Bar(
            open=mid_bar.open - hs,
            high=mid_bar.high - hs,
            low=mid_bar.low - hs,
            close=mid_bar.close - hs,
        )

        ask = Bar(
            open=mid_bar.open + hs,
            high=mid_bar.high + hs,
            low=mid_bar.low + hs,
            close=mid_bar.close + hs,
        )

        return BidAskBar(bid=bid, ask=ask)

