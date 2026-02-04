from dataclasses import dataclass
from typing import Any, Optional, Sequence


@dataclass(frozen=True)
class IndicatorParamDef:

    name: str
    type: type

    # Optional constraints
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None

    # For categorical / enum-like params
    choices: Optional[Sequence[Any]] = None

    # Default value (used if strategy does not override)
    default: Optional[Any] = None

    # Whether this param is mandatory
    required: bool = True

    description: Optional[str] = None

    def validate(self, value: Any) -> None:

        if value is None:
            if self.required:
                raise ValueError(f"Parameter '{self.name}' is required")
            return

        if not isinstance(value, self.type):
            raise TypeError(
                f"Parameter '{self.name}' must be of type {self.type.__name__}"
            )

        if self.choices is not None and value not in self.choices:
            raise ValueError(
                f"Parameter '{self.name}' must be one of {self.choices}"
            )

        if isinstance(value, (int, float)):
            if self.min is not None and value < self.min:
                raise ValueError(
                    f"Parameter '{self.name}' must be >= {self.min}"
                )
            if self.max is not None and value > self.max:
                raise ValueError(
                    f"Parameter '{self.name}' must be <= {self.max}"
                )
