from foundation.symbol.symbol_metadata import (
    SymbolMetadata,
    SYMBOL_METADATA_CATALOG,
)

class SymbolContext:
    """
    Immutable symbol snapshot for a single backtest run.

    - Created once at backtest initialization
    - Never mutated
    - Shared read-only across engine and foundation models
    """

    def __init__(self, *, symbol: str):
        self._metadata: SymbolMetadata = self._load_metadata(symbol)

    @staticmethod
    def _load_metadata(symbol: str) -> SymbolMetadata:
        try:
            return SYMBOL_METADATA_CATALOG[symbol]
        except KeyError:
            raise ValueError(f"Unsupported symbol: {symbol}")

    # ---- direct accessors ----

    @property
    def symbol(self) -> str:
        return self._metadata.symbol

    @property
    def pip_size(self) -> float:
        return self._metadata.pip_size

    @property
    def pip_precision(self) -> int:
        return self._metadata.pip_precision

    @property
    def lot_size(self) -> float:
        return self._metadata.lot_size

    @property
    def pip_value_per_lot(self) -> float:
        return self._metadata.pip_value_per_lot

    # ---- optional: expose raw metadata if needed ----

    @property
    def metadata(self) -> SymbolMetadata:
        return self._metadata
