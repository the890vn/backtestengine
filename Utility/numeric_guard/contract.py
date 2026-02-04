from abc import ABC, abstractmethod


class NumericGuardContract(ABC):

    @abstractmethod
    def ensure_finite(self, *, value: float, name: str) -> float:
        pass

    @abstractmethod
    def ensure_positive(self, *, value: float, name: str) -> float:
        pass

    @abstractmethod
    def ensure_non_negative(self, *, value: float, name: str) -> float:
        pass

    @abstractmethod
    def safe_divide(
        self,
        *,
        numerator: float,
        denominator: float,
        default: float | None = None
    ) -> float:
        pass

    @abstractmethod
    def ensure_non_zero_distance(self, *, value: float, name: str) -> float:
        pass
