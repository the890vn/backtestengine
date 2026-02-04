from indicator_library.base import IndicatorBase


class ADX(IndicatorBase):
    """
    Average Directional Index (Wilder).
    LEAN-style implementation.
    """

    def __init__(self, period: int):
        super().__init__()

        if period <= 0:
            raise ValueError("period must be > 0")

        self.period = period

        self._prev_high = None
        self._prev_low = None
        self._prev_close = None

        self._tr = 0.0
        self._plus_dm = 0.0
        self._minus_dm = 0.0

        self._atr = 0.0
        self._plus_di = 0.0
        self._minus_di = 0.0

        self._adx = 0.0
        self._counter = 0

    def update(self, high: float, low: float, close: float) -> None:
        if self._prev_close is None:
            self._prev_high = high
            self._prev_low = low
            self._prev_close = close
            return

        up_move = high - self._prev_high
        down_move = self._prev_low - low

        plus_dm = up_move if up_move > down_move and up_move > 0 else 0.0
        minus_dm = down_move if down_move > up_move and down_move > 0 else 0.0

        tr = max(
            high - low,
            abs(high - self._prev_close),
            abs(low - self._prev_close)
        )

        self._counter += 1

        if self._counter <= self.period:
            self._tr += tr
            self._plus_dm += plus_dm
            self._minus_dm += minus_dm

            if self._counter == self.period:
                self._atr = self._tr
        else:
            self._atr = self._atr - (self._atr / self.period) + tr
            self._plus_dm = self._plus_dm - (self._plus_dm / self.period) + plus_dm
            self._minus_dm = self._minus_dm - (self._minus_dm / self.period) + minus_dm

        if self._counter >= self.period:
            self._plus_di = 100 * (self._plus_dm / self._atr) if self._atr != 0 else 0
            self._minus_di = 100 * (self._minus_dm / self._atr) if self._atr != 0 else 0

            dx = (
                abs(self._plus_di - self._minus_di) /
                (self._plus_di + self._minus_di)
            ) * 100 if (self._plus_di + self._minus_di) != 0 else 0

            if self._counter == self.period * 2:
                self._adx = dx
            elif self._counter > self.period * 2:
                self._adx = (self._adx * (self.period - 1) + dx) / self.period

            if self._counter >= self.period * 2:
                self._current_value = self._adx
                self._is_ready = True

        self._prev_high = high
        self._prev_low = low
        self._prev_close = close

    def reset(self) -> None:
        self._prev_high = None
        self._prev_low = None
        self._prev_close = None

        self._tr = 0.0
        self._plus_dm = 0.0
        self._minus_dm = 0.0

        self._atr = 0.0
        self._plus_di = 0.0
        self._minus_di = 0.0

        self._adx = 0.0
        self._counter = 0

        self._is_ready = False
        self._current_value = None

# =========================
# ADX metadata definition
# =========================

ADX_DEF = IndicatorDef(
    id="ADX",
    name="Average Directional Index",
    category="Trend Strength",
    description="Wilder ADX measuring trend strength",

    implementation=ADX,

    inputs=[
        {
            "name": "ohlc",
            "type": "ohlc",
            "fields": ["high", "low", "close"],
            "required": True
        }
    ],

    outputs=[
        {"name": "adx", "type": "scalar", "range": [0, 100]},
        {"name": "plus_di", "type": "scalar"},
        {"name": "minus_di", "type": "scalar"}
    ],

    params={
        "period": IndicatorParamDef(
            name="period",
            type=int,
            default=14,
            min=1,
            max=100
        )
    },

    warmup_expr="period * 2",

    dependencies=None,

    plot={
        "pane": "separate",
        "lines": ["adx", "plus_di", "minus_di"]
    },

    tags=["classic", "wilder"],
    reference="https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/supported-indicators/average-directional-index"
)