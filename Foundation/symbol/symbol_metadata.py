from dataclasses import dataclass

@dataclass(frozen=True)
class SymbolMetadata:
    """
    Static instrument metadata definition.
    Immutable and side-effect free.
    """
    symbol: str

    pip_size: float
    pip_precision: int

    lot_size: float
    pip_value_per_lot: float


SYMBOL_METADATA_CATALOG: dict[str, SymbolMetadata] = {
    "EURUSD": SymbolMetadata(
        symbol="EURUSD",
        pip_size=0.0001,
        pip_precision=5,
        lot_size=100_000,
        pip_value_per_lot=10.0,
    ),
    "XAUUSD": SymbolMetadata(
        symbol="XAUUSD",
        pip_size=0.01,
        pip_precision=2,
        lot_size=100,
        pip_value_per_lot=1.0,
    ),
}
