from dataclasses import dataclass
from typing import List, Optional

from .indicator_param_def import IndicatorParamDef


@dataclass(frozen=True)
class IndicatorDef:

    # -------- Identity --------
    id: str                     # "SMA", "RSI", "MACD"
    name: str                   # Human readable
    category: str               # Trend, Momentum, Volatility, ...
    description: str

    # -------- Runtime --------
    implementation: type        # IndicatorBase subclass

    # -------- Inputs --------
    inputs: list[dict] | None   # Engine phải coi inputs là schema, không phải runtime data

    # -------- Outputs --------
    outputs: list[dict] | None  # Engine phải coi outputs là schema, không phải runtime data

    # -------- Parameters --------
    params: dict[str, IndicatorParamDef]

    # -------- Warmup --------
    warmup_expr: str | None

    # -------- Dependencies --------
    dependencies: list[dict] | None

    # -------- Visualization (UI only) --------
    plot: dict | None

    # -------- Misc --------
    tags: list[str] | None       # ["classic", "wilder"]
    reference: str | None        # Link to formula / source

