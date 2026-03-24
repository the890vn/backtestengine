from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from Core.Strategy.nodes import EntryCondition, ExitCondition, ExitConditionOptional


@dataclass(frozen=True)
class IndicatorBuildPlan:
    """
    Kế hoạch khởi tạo một indicator instance.
    IndicatorEngine dùng object này để build, không cần đọc run_config.

    validated_params đã được merge với default và validate bởi indicator registry.
    indicator_instance_name là tên deterministic, khớp với tên frontend đã generate.
    """
    indicator_instance_name: str
    indicator_id:            str
    input_sources:           tuple[str, ...]
    validated_params:        dict[str, Any]
    timeframe:               str


@dataclass(frozen=True)
class ResolvedDataConfig:
    """
    Kết quả parse phần data của run_config.
    DataEngine chỉ nhận object này, không biết gì về run_config gốc.

    Timestamp convention:
        - Đơn vị: epoch seconds UTC
        - timestamp = close_time của bar (end time)
        - Bar đã đóng hoàn toàn tại thời điểm timestamp của nó
    """
    symbol:            str
    from_time:         int             # epoch seconds — bar đầu tiên trong official window
    to_time:           int             # epoch seconds — bar cuối trong official window
    load_from_time:    int             # epoch seconds — lùi thêm để đủ warmup
    runtime_timeframe: str             # luôn là M1
    data_timeframes:   tuple[str, ...] # sorted tăng dần theo seconds, luôn include M1
    warmup_bars:       dict[str, int]  # số bar warmup yêu cầu per timeframe


@dataclass(frozen=True)
class ResolvedIndicatorConfig:
    """
    Kết quả parse phần indicators của run_config.
    IndicatorEngine chỉ nhận object này để build instances và precompute.

    warmup_bars được expose ra ngoài để RunConfigParser truyền cho _parse_data_config.
    IndicatorEngine không cần dùng warmup_bars — đó là trách nhiệm của DataEngine.
    """
    build_plans: tuple[IndicatorBuildPlan, ...]
    warmup_bars: dict[str, int]  # per timeframe — RunConfigParser dùng để tính load_from_time


@dataclass(frozen=True)
class ResolvedStrategyConfig:
    """
    Kết quả parse phần strategy của run_config.
    StrategyEngine chỉ nhận object này để evaluate conditions.
    """
    entry_condition:         EntryCondition
    exit_condition:          ExitCondition
    exit_condition_optional: ExitConditionOptional


@dataclass(frozen=True)
class BacktestRunConfig:
    """
    Object tổng được RunConfigParser.parse() trả ra.
    Orchestrator dùng để distribute config xuống từng engine.

    Đây là hợp đồng bất biến duy nhất giữa tầng config và tầng engine.
    Sau khi parse() trả về object này, run_config.json không còn được dùng nữa.
    """
    resolved_data:      ResolvedDataConfig
    resolved_indicator: ResolvedIndicatorConfig
    resolved_strategy:  ResolvedStrategyConfig