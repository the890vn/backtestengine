from user_configs.stop_loss_config import StopLossConfig, SlMode
from utils.numeric_guard.model import NumericGuardModel


class StopLossModel:
    """
    Stateless foundation model.
    Pure SL price computation.
    """

    _guard = NumericGuardModel()

    @classmethod
    def compute_price(
        cls,
        *,
        config: StopLossConfig,

        # --- external runtime values ---
        entry_price: float,
        side: PositionSide,
        pip_size: float | None = None,
    ) -> float:

        g = cls._guard

        entry_price = g.ensure_positive(
            value=entry_price,
            name="entry_price"
        )

        # ====================================================
        # FIXED PIPS
        # ====================================================
        if config.mode == SlMode.FIXED_PIPS:
            pips = g.ensure_positive(config.pips, "pips")
            pip_size = g.ensure_positive(pip_size, "pip_size")

            distance = pips * pip_size

        # ====================================================
        # PERCENT PRICE
        # ====================================================
        elif config.mode == SlMode.PERCENT_PRICE:
            percent = g.ensure_positive(config.percent, "percent")
            distance = entry_price * (percent / 100.0)

        else:
            raise ValueError(f"Unsupported SlMode: {config.mode}")

        # ---- final SL price ----
        if side.is_long:
            sl_price = entry_price - distance
        else:
            sl_price = entry_price + distance

        return g.ensure_finite(sl_price, "sl_price")
