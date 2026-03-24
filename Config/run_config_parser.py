from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import ValidationError

from Core.Config.config_schema import (
    ConditionDef,
    ConstantNodeDef,
    IndicatorNodeDef,
    LeafNodeDef,
    PositionNodeDef,
    PriceNodeDef,
    RunConfigSchema,
    StrategyConditionsDef,
)
from Core.Config.resolved_configs import (
    BacktestRunConfig,
    IndicatorBuildPlan,
    ResolvedDataConfig,
    ResolvedIndicatorConfig,
    ResolvedStrategyConfig,
)
from Core.Data.timeframe_utils import (
    canonicalize_timeframes,
    compute_load_from_time,
    eval_warmup_expr,
    parse_timeframe,
    parse_utc_timestamp,
)
from Core.Strategy.conditions import GroupCondition
from Core.Strategy.nodes import (
    ComparisonNode,
    ConstantNode,
    EntryCondition,
    ExitCondition,
    ExitConditionOptional,
    IndicatorNode,
    PositionNode,
    PriceNode,
)
from Core.Strategy.operators import OPERATOR_REGISTRY
from Infrastructure.indicator_library.indicator_name_builder import build_indicator_name
from Infrastructure.indicator_library.indicator_registry import IndicatorRegistry

logger = logging.getLogger(__name__)

_RUNTIME_TIMEFRAME        = "M1"
_STRATEGY_SECTION_NAMES   = ("entry_condition", "exit_condition", "exit_condition_optional")


class RunConfigParser:
    """
    Parse toàn bộ run_config.json thành BacktestRunConfig một lần duy nhất.

    Thứ tự xử lý bắt buộc:
        1. Pydantic validate toàn bộ JSON          → RunConfigSchema
        2. _parse_indicator_config()               → ResolvedIndicatorConfig + warmup_bars
        3. _parse_data_config(warmup_bars)         → ResolvedDataConfig
        4. _parse_strategy_config()                → ResolvedStrategyConfig

    Orchestrator nhận BacktestRunConfig và distribute từng ResolvedConfig
    xuống đúng engine. Các engine không biết gì về run_config.json gốc.
    """

    @classmethod
    def parse(
        cls,
        run_config_json:    str | dict[str, Any],
        indicator_registry: IndicatorRegistry,
    ) -> BacktestRunConfig:
        raw_config = cls._load_raw_config(run_config_json)

        try:
            validated_config = RunConfigSchema.model_validate(raw_config)
        except ValidationError as e:
            raise ValueError(f"run_config không hợp lệ:\n{e}") from e

        resolved_indicator = cls._parse_indicator_config(validated_config, indicator_registry)
        resolved_data      = cls._parse_data_config(validated_config, resolved_indicator.warmup_bars)
        resolved_strategy  = cls._parse_strategy_config(validated_config.strategy)

        logger.info(
            "[RunConfigParser] Parse hoàn tất — symbol=%s | window=[%d, %d] | "
            "load_from=%d | timeframes=%s | warmup=%s",
            resolved_data.symbol,
            resolved_data.from_time,
            resolved_data.to_time,
            resolved_data.load_from_time,
            list(resolved_data.data_timeframes),
            resolved_data.warmup_bars,
        )

        return BacktestRunConfig(
            resolved_data      = resolved_data,
            resolved_indicator = resolved_indicator,
            resolved_strategy  = resolved_strategy,
        )

    # ── Sub-parsers ───────────────────────────────────────────────────────────

    @classmethod
    def _parse_indicator_config(
        cls,
        validated_config:   RunConfigSchema,
        indicator_registry: IndicatorRegistry,
    ) -> ResolvedIndicatorConfig:
        """
        Đọc indicators[], merge params với default từ registry,
        tính warmup_bars per timeframe, generate instance names.
        Deduplication: cùng cấu hình chỉ tạo một build plan.
        """
        warmup_bars:         dict[str, int]         = {}
        build_plans:         list[IndicatorBuildPlan] = []
        seen_instance_names: set[str]               = set()

        for indicator_config in validated_config.indicators:
            indicator_id = indicator_config.id
            input_sources = indicator_config.input
            timeframe    = indicator_config.timeframe
            raw_params   = indicator_config.params

            indicator_def = indicator_registry.get_def(indicator_id)

            # Merge params: user value → default từ registry
            validated_params: dict[str, Any] = {}
            for param_name, param_def in indicator_def.params.items():
                value = raw_params.get(param_name, param_def.default)
                param_def.validate(value)
                validated_params[param_name] = value

            # Tính warmup per timeframe — lấy max nếu nhiều indicator cùng timeframe
            warmup_value = eval_warmup_expr(indicator_def.warmup_expr, validated_params)
            warmup_bars[timeframe] = max(warmup_bars.get(timeframe, 0), warmup_value)

            # Generate tên deterministic — phải khớp với tên frontend đã tạo
            indicator_instance_name = build_indicator_name(
                indicator_def = indicator_def,
                input_sources = input_sources,
                params        = validated_params,
                timeframe     = timeframe,
            )

            # Bỏ qua nếu cùng cấu hình đã được đăng ký
            if indicator_instance_name in seen_instance_names:
                continue
            seen_instance_names.add(indicator_instance_name)

            build_plans.append(IndicatorBuildPlan(
                indicator_instance_name = indicator_instance_name,
                indicator_id            = indicator_id,
                input_sources           = tuple(input_sources),
                validated_params        = validated_params,
                timeframe               = timeframe,
            ))

        return ResolvedIndicatorConfig(
            build_plans = tuple(build_plans),
            warmup_bars = warmup_bars,
        )

    @classmethod
    def _parse_data_config(
        cls,
        validated_config: RunConfigSchema,
        warmup_bars:      dict[str, int],
    ) -> ResolvedDataConfig:
        """
        Thu thập timeframes, nhận warmup_bars từ _parse_indicator_config,
        tính load_from_time. Không tự đọc lại indicators[].
        """
        from_time = parse_utc_timestamp(validated_config.date_range.from_time)
        to_time   = parse_utc_timestamp(validated_config.date_range.to_time)

        if from_time >= to_time:
            raise ValueError(
                f"date_range.from_time ({from_time}) phải nhỏ hơn to_time ({to_time})"
            )

        data_timeframes = cls._collect_data_timeframes(validated_config)

        # Đảm bảo warmup_bars có đủ key cho tất cả timeframes đã thu thập
        # Timeframe không có indicator nào thì warmup = 0
        full_warmup_bars: dict[str, int] = {
            tf: warmup_bars.get(tf, 0) for tf in data_timeframes
        }

        load_from_time = compute_load_from_time(from_time, full_warmup_bars)

        return ResolvedDataConfig(
            symbol            = validated_config.symbol,
            from_time         = from_time,
            to_time           = to_time,
            load_from_time    = load_from_time,
            runtime_timeframe = _RUNTIME_TIMEFRAME,
            data_timeframes   = data_timeframes,
            warmup_bars       = full_warmup_bars,
        )

    @classmethod
    def _parse_strategy_config(
        cls,
        strategy_def: StrategyConditionsDef,
    ) -> ResolvedStrategyConfig:
        return ResolvedStrategyConfig(
            entry_condition = EntryCondition(
                groups=cls._parse_condition_groups(strategy_def.entry_condition)
            ),
            exit_condition = ExitCondition(
                groups=cls._parse_condition_groups(strategy_def.exit_condition)
            ),
            exit_condition_optional = ExitConditionOptional(
                groups=cls._parse_condition_groups(strategy_def.exit_condition_optional)
            ),
        )

    # ── Helpers: data timeframes ──────────────────────────────────────────────

    @classmethod
    def _collect_data_timeframes(cls, validated_config: RunConfigSchema) -> tuple[str, ...]:
        """
        Thu thập tất cả timeframes cần load:
        - indicators[*].timeframe
        - strategy.*_condition keys (timeframe block keys)
        - Inject M1 bắt buộc làm runtime_timeframe
        """
        timeframes: set[str] = {_RUNTIME_TIMEFRAME}

        for indicator_config in validated_config.indicators:
            timeframes.add(indicator_config.timeframe)

        strategy = validated_config.strategy
        for section_name in _STRATEGY_SECTION_NAMES:
            section: dict = getattr(strategy, section_name, {})
            for tf_key in section.keys():
                timeframes.add(tf_key)

        return canonicalize_timeframes(timeframes)

    # ── Helpers: strategy nodes ───────────────────────────────────────────────

    @classmethod
    def _parse_condition_groups(
        cls,
        section_conditions: dict[str, list[ConditionDef]],
    ) -> list[GroupCondition]:
        return [
            GroupCondition(
                timeframe = timeframe,
                nodes     = cls._parse_comparison_nodes(timeframe, condition_defs),
            )
            for timeframe, condition_defs in section_conditions.items()
        ]

    @classmethod
    def _parse_comparison_nodes(
        cls,
        timeframe:      str,
        condition_defs: list[ConditionDef],
    ) -> list[ComparisonNode]:
        return [
            ComparisonNode(
                left          = cls._build_leaf_node(cond_def.subject, timeframe),
                operator_spec = OPERATOR_REGISTRY[cond_def.operator],
                right         = cls._build_leaf_node(cond_def.reference, timeframe),
                timeframe     = timeframe,
            )
            for cond_def in condition_defs
        ]

    @classmethod
    def _build_leaf_node(cls, node_def: LeafNodeDef, timeframe: str):
        """
        Map từ Pydantic NodeDef sang Engine Node.
        Dùng isinstance thay vì string comparison để type checker có thể kiểm tra.
        """
        if isinstance(node_def, IndicatorNodeDef):
            return IndicatorNode(
                indicator_instance_name = node_def.indicator_instance_name,
                output                  = node_def.output,
                timeframe               = timeframe,
            )
        if isinstance(node_def, ConstantNodeDef):
            return ConstantNode(value=node_def.value, timeframe=timeframe)

        if isinstance(node_def, PriceNodeDef):
            return PriceNode(field=node_def.field, timeframe=timeframe)

        if isinstance(node_def, PositionNodeDef):
            return PositionNode(field=node_def.field)

        raise ValueError(f"Loại node không được hỗ trợ: {type(node_def)}")

    # ── Utility ───────────────────────────────────────────────────────────────

    @staticmethod
    def _load_raw_config(run_config_json: str | dict[str, Any]) -> dict[str, Any]:
        if isinstance(run_config_json, dict):
            return run_config_json
        if isinstance(run_config_json, str):
            try:
                return json.loads(run_config_json)
            except json.JSONDecodeError as e:
                raise ValueError(f"run_config không phải JSON hợp lệ: {e}") from e
        raise TypeError(
            f"run_config phải là str hoặc dict, nhận được: {type(run_config_json)}"
        )