# foundation/utils/numeric_guard/model.py
import math
from utils.numeric_guard.contract import NumericGuardContract


class NumericGuardModel(NumericGuardContract):
    """
    Stateless numeric invariant guard.
    Engine-safety only. No business logic.
    """

    def ensure_finite(self, *, value: float, name: str) -> float:
        if not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number")
        return value

    def ensure_positive(self, *, value: float, name: str) -> float:
        self.ensure_finite(value=value, name=name)

        if value <= 0:
            raise ValueError(f"{name} must be > 0")

        return value

    def ensure_non_negative(self, *, value: float, name: str) -> float:
        self.ensure_finite(value=value, name=name)

        if value < 0:
            raise ValueError(f"{name} must be >= 0")

        return value

    def safe_divide(
        self,
        *,
        numerator: float,
        denominator: float,
        default: float | None = None
    ) -> float:
        self.ensure_finite(value=numerator, name="numerator")
        self.ensure_finite(value=denominator, name="denominator")

        if denominator == 0:
            if default is not None:
                return default
            raise ValueError("Division by zero")

        return numerator / denominator

    def ensure_non_zero_distance(self, *, value: float, name: str) -> float:
        self.ensure_finite(value=value, name=name)

        if value == 0:
            raise ValueError(f"{name} must not be zero")

        return value
