from indicator_library.base import IndicatorBase
from indicator_library.indicator_def import IndicatorDef
from indicator_library.indicator_param_def import IndicatorParamDef


class EMA(IndicatorBase):
    """
    Exponential Moving Average (LEAN-style).

    Formula:
        EMA_t = EMA_{t-1} + k * (value_t - EMA_{t-1})
        k = 2 / (period + 1)
    """

    def __init__(self, period: int):
        super().__init__()

        if period <= 0:
            raise ValueError("period must be > 0")

        self.period = period
        self.k = 2.0 / (period + 1)

        self._ema = None
        self._samples = 0

    def update(self, value: float) -> None:
        self._samples += 1

        # Seed with first value (LEAN behavior)
        if self._ema is None:
            self._ema = value
            self._current_value = value
            return

        self._ema = self._ema + self.k * (value - self._ema)
        self._current_value = self._ema

        if self._samples >= self.period:
            self._is_ready = True

    def reset(self) -> None:
        self._ema = None
        self._samples = 0
        self._is_ready = False
        self._current_value = None

# =========================
# EMA metadata definition
# =========================

EMA_DEF = IndicatorDef(
    # -------- Identity --------
    id="EMA",
    name="Exponential Moving Average",
    category="Trend",
    description="Exponentially weighted moving average (LEAN style)",

    # -------- Runtime --------
    implementation=EMA,

    # -------- Inputs --------
    inputs=[
        {
            "name": "source",
            "type": "scalar",
            "fields": ["close"],
            "required": True,
            "multiple": False
        }
    ],

    # -------- Outputs --------
    outputs=[
        {
            "name": "value",
            "type": "scalar",
            "semantic": "price",
            "range": None
        }
    ],

    # -------- Parameters --------
    params={
        "period": IndicatorParamDef(
            name="period",
            type=int,
            default=14,
            min=1,
            max=5000,
            step=1,
            description="EMA lookback period"
        )
    },

    # -------- Warmup --------
    # LEAN considers EMA ready after period samples
    warmup_expr="period",

    # -------- Dependencies --------
    dependencies=None,

    # -------- Visualization --------
    plot={
        "overlay": True,
        "line_style": "solid"
    },

    # -------- Misc --------
    tags=["classic", "ema", "lean"],
    reference="https://github.com/QuantConnect/Lean/blob/master/Indicators/ExponentialMovingAverage.cs"
)
