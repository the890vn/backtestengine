from indicator_library.base import IndicatorBase
from indicator_library.indicator_def import IndicatorDef
from indicator_library.indicator_param_def import IndicatorParamDef


class RSI(IndicatorBase):
    """
    Relative Strength Index (RSI) – Wilder smoothing.
    Implementation matches LEAN engine logic.
    """

    def __init__(self, period: int):
        super().__init__()

        if period <= 0:
            raise ValueError("period must be > 0")

        self.period = period

        self._prev_price: float | None = None

        # Wilder averages
        self._avg_gain: float = 0.0
        self._avg_loss: float = 0.0

        # Number of deltas processed
        self._count: int = 0

    def update(self, value: float) -> None:

        # First tick: only seed prev_price
        if self._prev_price is None:
            self._prev_price = value
            return

        delta = value - self._prev_price
        gain = max(delta, 0.0)
        loss = max(-delta, 0.0)

        self._prev_price = value

        if self._count < self.period:
            self._avg_gain += gain
            self._avg_loss += loss
            self._count += 1

            if self._count == self.period:
                self._avg_gain /= self.period
                self._avg_loss /= self.period
                self._compute_rsi()
                self._is_ready = True

            return

        self._avg_gain = (
            (self._avg_gain * (self.period - 1)) + gain
        ) / self.period

        self._avg_loss = (
            (self._avg_loss * (self.period - 1)) + loss
        ) / self.period

        self._compute_rsi()
        self._is_ready = True

    def _compute_rsi(self) -> None:
        if self._avg_loss == 0.0:
            self._current_value = 100.0
        else:
            rs = self._avg_gain / self._avg_loss
            self._current_value = 100.0 - (100.0 / (1.0 + rs))

    def reset(self) -> None:
        self._prev_price = None
        self._avg_gain = 0.0
        self._avg_loss = 0.0
        self._count = 0
        self._is_ready = False
        self._current_value = None


# =========================
# RSI metadata definition
# =========================

RSI_DEF = IndicatorDef(
    # -------- Identity --------
    id="RSI",
    name="Relative Strength Index",
    category="Momentum",
    description="Wilder RSI oscillator measuring momentum on a 0–100 scale",

    # -------- Runtime --------
    implementation=RSI,

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
            "range": [0, 100],
            "semantic": "oscillator"
        }
    ],

    # -------- Parameters --------
    params={
        "period": IndicatorParamDef(
            name="period",
            type=int,
            default=14,
            min=1,
            max=1000,
            step=1,
            description="RSI lookback period (Wilder smoothing)"
        )
    },

    # -------- Warmup --------
    # 1 tick to get prev_price + period deltas to seed averages
    warmup_expr="period + 1",

    # -------- Dependencies --------
    dependencies=None,

    # -------- Visualization --------
    plot={
        "pane": "separate",
        "levels": [30, 50, 70],
        "style": "line"
    },

    # -------- Misc --------
    tags=["classic", "wilder", "momentum"],
    reference="https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/supported-indicators/relative-strength-index-rsi"
)
