from typing import Dict, Type, Iterable

from .base import Indicator
from .indicator_def import IndicatorDef


class IndicatorRegistry:
    """
    Central registry for all system indicators.

    Responsibilities:
    - Store indicator metadata (IndicatorDef)
    - Map indicator slug -> runtime Indicator class
    - Provide discovery for UI & strategy builder
    """

    _defs: Dict[str, IndicatorDef] = {}
    _classes: Dict[str, Type[Indicator]] = {}

    # -------------------------
    # Registration
    # -------------------------

    @classmethod
    def register(
        cls,
        indicator_def: IndicatorDef,
        indicator_cls: Type[Indicator],
    ) -> None:
        slug = indicator_def.slug

        if not slug:
            raise ValueError("Indicator slug must not be empty")

        if slug in cls._defs:
            raise ValueError(f"Indicator '{slug}' already registered")

        cls._defs[slug] = indicator_def
        cls._classes[slug] = indicator_cls

    # -------------------------
    # Accessors
    # -------------------------

    @classmethod
    def get_def(cls, slug: str) -> IndicatorDef:
        try:
            return cls._defs[slug]
        except KeyError:
            raise KeyError(f"Indicator definition '{slug}' not found")

    @classmethod
    def get_class(cls, slug: str) -> Type[Indicator]:
        try:
            return cls._classes[slug]
        except KeyError:
            raise KeyError(f"Indicator class '{slug}' not found")

    @classmethod
    def has(cls, slug: str) -> bool:
        return slug in cls._defs

    # -------------------------
    # Discovery (UI / Builder)
    # -------------------------

    @classmethod
    def list_defs(cls) -> Iterable[IndicatorDef]:
        """
        Used by UI to show available indicators
        """
        return cls._defs.values()

    @classmethod
    def clear(cls) -> None:
        """
        Only for testing
        """
        cls._defs.clear()
        cls._classes.clear()
