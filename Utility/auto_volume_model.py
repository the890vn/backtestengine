from user_configs.auto_volume_config import AutoVolumeConfig, AutoVolumeMode
from utils.numeric_guard.model import NumericGuardModel


class AutoVolumeModel:
    """
    Stateless foundation model.
    Computes position size (lot size) from risk constraints.
    """

    _guard = NumericGuardModel()

    @classmethod
    def compute_lot_size(
        cls,
        *,
        config: AutoVolumeConfig,

        # --- runtime inputs from engine ---
        entry_price: float,
        sl_price: float,

        account_equity: float,
        pip_size: float,
        pip_value_per_lot: float,
    ) -> float:
        """
        Compute position size (lot size).
        """

        g = cls._guard

        # ---- numeric safety ----
        entry_price = g.ensure_positive(entry_price, "entry_price")
        sl_price = g.ensure_finite(sl_price, "sl_price")

        equity = g.ensure_positive(account_equity, "account_equity")
        pip_size = g.ensure_positive(pip_size, "pip_size")
        pip_value = g.ensure_positive(pip_value_per_lot, "pip_value_per_lot")

        # ---- risk distance (price) ----
        risk_distance_price = abs(entry_price - sl_price)
        g.ensure_non_zero_distance(risk_distance_price, "risk_distance_price")

        # ---- convert price → pips ----
        risk_pips = g.safe_divide(
            numerator=risk_distance_price,
            denominator=pip_size
        )

        # ====================================================
        # RISK % EQUITY
        # ====================================================
        if config.mode == AutoVolumeMode.RISK_PERCENT_EQUITY:
            risk_percent = g.ensure_positive(
                config.risk_percent,
                "risk_percent"
            )
            cash_risk = equity * (risk_percent / 100.0)

        # ====================================================
        # FIXED CASH RISK
        # ====================================================
        elif config.mode == AutoVolumeMode.FIXED_CASH_RISK:
            cash_risk = g.ensure_positive(
                config.cash_risk,
                "cash_risk"
            )

        else:
            raise ValueError(f"Unsupported AutoVolumeMode: {config.mode}")

        # ---- lot size ----
        lot_size = g.safe_divide(
            numerator=cash_risk,
            denominator=risk_pips * pip_value
        )

        return g.ensure_finite(lot_size, "lot_size")
