from indicator_library.base import IndicatorBase
from indicator_library.indicators.ema import EMA


class MACD(IndicatorBase):
    """
    Moving Average Convergence Divergence (MACD).
    LEAN-style implementation.
    """

    def __init__(self, fast_period: int, slow_period: int, signal_period: int):
        super().__init__()

        if fast_period <= 0 or slow_period <= 0 or signal_period <= 0:
            raise ValueError("All MACD periods must be > 0")

        if fast_period >= slow_period:
            raise ValueError("fast_period must be < slow_period")

        self.fast_ema = EMA(fast_period)
        self.slow_ema = EMA(slow_period)
        self.signal_ema = EMA(signal_period)

        self.macd = None
        self.signal = None
        self.histogram = None

    def update(self, value: float) -> None:
        self.fast_ema.update(value)
        self.slow_ema.update(value)

        if not (self.fast_ema.is_ready and self.slow_ema.is_ready):
            return

        self.macd = self.fast_ema.current_value - self.slow_ema.current_value
        self.signal_ema.update(self.macd)

        if not self.signal_ema.is_ready:
            return

        self.signal = self.signal_ema.current_value
        self.histogram = self.macd - self.signal

        self._current_value = self.macd
        self._is_ready = True

    def reset(self) -> None:
        self.fast_ema.reset()
        self.slow_ema.reset()
        self.signal_ema.reset()

        self.macd = None
        self.signal = None
        self.histogram = None

        self._is_ready = False
        self._current_value = None

# =========================
# MACD metadata definition
# =========================

MACD_DEF = IndicatorDef(
    id="MACD",
    name="Moving Average Convergence Divergence",
    category="Momentum",
    description="MACD oscillator using EMA (LEAN style)",

    implementation=MACD,

    inputs=[
        {
            "name": "source",
            "type": "scalar",
            "fields": ["close"],
            "required": True
        }
    ],

    outputs=[
        {"name": "macd", "type": "scalar"},
        {"name": "signal", "type": "scalar"},
        {"name": "histogram", "type": "scalar"}
    ],

    params={
        "fast_period": IndicatorParamDef(
            name="fast_period",
            type=int,
            default=12,
            min=1,
            max=200
        ),
        "slow_period": IndicatorParamDef(
            name="slow_period",
            type=int,
            default=26,
            min=1,
            max=500
        ),
        "signal_period": IndicatorParamDef(
            name="signal_period",
            type=int,
            default=9,
            min=1,
            max=200
        )
    },

    warmup_expr="slow_period + signal_period",

    dependencies=[
        {"indicator": "EMA", "role": "fast"},
        {"indicator": "EMA", "role": "slow"},
        {"indicator": "EMA", "role": "signal"}
    ],

    plot={
        "pane": "separate",
        "lines": ["macd", "signal"],
        "histogram": "histogram"
    },

    tags=["classic", "momentum"],
    reference="https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/supported-indicators/moving-average-convergence-divergence"
)