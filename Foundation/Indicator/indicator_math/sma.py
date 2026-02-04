from collections import deque

from indicator_library.base import IndicatorBase
from indicator_library.indicator_def import IndicatorDef
from indicator_library.indicator_param_def import IndicatorParamDef


class SMA(IndicatorBase):
    """
    Simple Moving Average (SMA).

    LEAN-engine equivalent:
    - Rolling window
    - Sum / period
    - IsReady after period samples
    """

    def __init__(self, period: int):
        super().__init__()

        if period <= 0:
            raise ValueError("period must be > 0")

        self.period = period

        self._window = deque(maxlen=period)
        self._sum: float = 0.0

    def update(self, value: float) -> None:
        """
        Update SMA with a new scalar value (e.g. close price).
        """

        # Remove oldest value if window is full
        if len(self._window) == self.period:
            self._sum -= self._window[0]

        self._window.append(value)
        self._sum += value

        if len(self._window) == self.period:
            self._current_value = self._sum / self.period
            self._is_ready = True

    def reset(self) -> None:
        self._window.clear()
        self._sum = 0.0
        self._is_ready = False
        self._current_value = None


# =========================
# SMA metadata definition
# =========================

SMA_DEF = IndicatorDef(
    # -------- Identity --------
    id="SMA",
    name="Simple Moving Average",
    category="Trend",
    description="Arithmetic mean of the last N values",

    # -------- Runtime --------
    implementation=SMA,

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
            "range": None,
            "semantic": "price"
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
            description="Number of samples used to compute the average"
        )
    },

    # -------- Warmup --------
    warmup_expr="period",

    # -------- Dependencies --------
    dependencies=None,

    # -------- Visualization --------
    plot={
        "pane": "overlay",
        "style": "line"
    },

    # -------- Misc --------
    tags=["classic", "trend"],
    reference="https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/supported-indicators/simple-moving-average-sma"
)
