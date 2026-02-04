from user_configs.take_profit_config import TakeProfitConfig, TpMode
from utils.numeric_guard.model import NumericGuardModel


class TakeProfitModel:
    """
    Stateless foundation model.
    Responsible only for TP price computation.
    """

    _guard = NumericGuardModel()

    @classmethod
    def compute_price(
        cls,
        *,
        config: TakeProfitConfig,

        # --- runtime values from engine ---
        entry_price: float,
        side: PositionSide,

        pip_size: float | None = None,
        lot_size: float | None = None,
        pip_value_per_lot: float | None = None,

        sl_price: float | None = None,
    ) -> float:

        g = cls._guard

        entry_price = g.ensure_positive(
            value=entry_price,
            name="entry_price"
        )

        # ====================================================
        # FIXED PIPS
        # ====================================================
        if config.mode == TpMode.FIXED_PIPS:
            pips = g.ensure_positive(config.pips, "pips")
            pip_size = g.ensure_positive(pip_size, "pip_size")

            distance = pips * pip_size

        # ====================================================
        # FIXED CASH
        # ====================================================
        elif config.mode == TpMode.FIXED_CASH:
            cash_profit = g.ensure_positive(config.cash_profit, "cash_profit")
            lot_size = g.ensure_positive(lot_size, "lot_size")
            pip_value = g.ensure_positive(pip_value_per_lot, "pip_value_per_lot")

            pips = g.safe_divide(
                numerator=cash_profit,
                denominator=lot_size * pip_value
            )

            pip_size = g.ensure_positive(pip_size, "pip_size")
            distance = pips * pip_size

        # ====================================================
        # PERCENT PRICE
        # ====================================================
        elif config.mode == TpMode.PERCENT_PRICE:
            percent = g.ensure_positive(config.percent, "percent")
            distance = entry_price * (percent / 100.0)

        # ====================================================
        # RISK REWARD
        # ====================================================
        elif config.mode == TpMode.RISK_REWARD:
            rr_ratio = g.ensure_positive(config.rr_ratio, "rr_ratio")
            sl_price = g.ensure_finite(sl_price, "sl_price")

            risk_distance = abs(entry_price - sl_price)
            g.ensure_non_zero_distance(risk_distance, "risk_distance")

            distance = risk_distance * rr_ratio

        else:
            raise ValueError(f"Unsupported TpMode: {config.mode}")

        # ---- final TP price ----
        if side.is_long:
            tp_price = entry_price + distance
        else:
            tp_price = entry_price - distance

        return g.ensure_finite(tp_price, "tp_price")
