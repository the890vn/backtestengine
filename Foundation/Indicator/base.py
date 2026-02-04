from abc import ABC, abstractmethod

class IndicatorBase(ABC):
    """
    IndicatorBase is a stateful mathematical reducer.
    It does NOT define input source or output wiring.
    """

    def __init__(self) -> None:
        self._is_ready = False
        self._current_value = None

    @abstractmethod
    def update(self, value: float) -> None:
        pass

    @property
    def is_ready(self) -> bool:
        return self._is_ready

    @property
    def current_value(self) -> float:
        if not self._is_ready:
            raise RuntimeError("Indicator not ready")
        return self._current_value

    @abstractmethod
    def reset(self) -> None:
        pass
