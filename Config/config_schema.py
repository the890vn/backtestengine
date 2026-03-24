from __future__ import annotations

from typing import Any, Dict, List, Literal, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from Core.Data.timeframe_utils import parse_timeframe
from Core.Strategy.operators import OPERATOR_REGISTRY, STRATEGY_METADATA


# ── Date Range ────────────────────────────────────────────────────────────────

class DateRangeDef(BaseModel):
    from_time: str
    to_time: str


# ── Indicator Config ──────────────────────────────────────────────────────────

class IndicatorConfigDef(BaseModel):
    id:        str
    input:     str | list[str]
    params:    Dict[str, Any] = Field(default_factory=dict)
    timeframe: str

    @field_validator("id")
    @classmethod
    def validate_indicator_id(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("indicator 'id' không được rỗng")
        return stripped

    @field_validator("input")
    @classmethod
    def validate_input_sources(cls, v: str | list[str]) -> list[str]:
        """Normalize về list, validate từng source."""
        allowed = {"open", "high", "low", "close", "volume", "timestamp"}
        sources = [v] if isinstance(v, str) else v

        if not sources:
            raise ValueError("'input' không được rỗng")

        for source in sources:
            if source not in allowed:
                raise ValueError(
                    f"input source '{source}' không hợp lệ. Chỉ chấp nhận: {allowed}"
                )
        return sources

    @field_validator("timeframe")
    @classmethod
    def validate_timeframe_format(cls, v: str) -> str:
        return parse_timeframe(v)


# ── Strategy Leaf Nodes ───────────────────────────────────────────────────────

class IndicatorNodeDef(BaseModel):
    type:                   Literal["indicator"]
    indicator_instance_name: str
    output:                 str


class ConstantNodeDef(BaseModel):
    type:  Literal["constant"]
    value: float


class PriceNodeDef(BaseModel):
    type:  Literal["price"]
    field: str

    @field_validator("field")
    @classmethod
    def validate_price_field(cls, v: str) -> str:
        allowed = STRATEGY_METADATA["price"]["fields"]
        if v not in allowed:
            raise ValueError(
                f"price 'field' là '{v}' không hợp lệ. Chỉ chấp nhận: {allowed}"
            )
        return v


class PositionNodeDef(BaseModel):
    type:  Literal["position"]
    field: str

    @field_validator("field")
    @classmethod
    def validate_position_field(cls, v: str) -> str:
        allowed = STRATEGY_METADATA["position"]["fields"]
        if v not in allowed:
            raise ValueError(
                f"position 'field' là '{v}' không hợp lệ. Chỉ chấp nhận: {allowed}"
            )
        return v


# Pydantic tự nhận diện loại node qua trường 'type'
LeafNodeDef = Union[IndicatorNodeDef, ConstantNodeDef, PriceNodeDef, PositionNodeDef]


# ── Strategy Condition ────────────────────────────────────────────────────────

class ConditionDef(BaseModel):
    subject:   LeafNodeDef
    operator:  str
    reference: LeafNodeDef

    @model_validator(mode="after")
    def validate_operator_compatibility(self) -> "ConditionDef":
        operator_spec = OPERATOR_REGISTRY.get(self.operator)
        if operator_spec is None:
            raise ValueError(f"Operator không hợp lệ: '{self.operator}'")

        for node in (self.subject, self.reference):
            node_meta = STRATEGY_METADATA.get(node.type)
            if node_meta is None:
                continue

            if operator_spec.requires_previous and not node_meta.get("supports_previous", False):
                raise ValueError(
                    f"Operator '{self.operator}' yêu cầu previous value "
                    f"nhưng loại node '{node.type}' không hỗ trợ."
                )

            allowed_operators = node_meta.get("compatible_operators", [])
            if self.operator not in allowed_operators:
                raise ValueError(
                    f"Operator '{self.operator}' không được hỗ trợ cho loại node '{node.type}'. "
                    f"Chỉ chấp nhận: {allowed_operators}"
                )
        return self


# ── Strategy Conditions ───────────────────────────────────────────────────────

class StrategyConditionsDef(BaseModel):
    entry_condition:          Dict[str, List[ConditionDef]] = Field(default_factory=dict)
    exit_condition:           Dict[str, List[ConditionDef]] = Field(default_factory=dict)
    exit_condition_optional:  Dict[str, List[ConditionDef]] = Field(default_factory=dict)

    @field_validator(
        "entry_condition",
        "exit_condition",
        "exit_condition_optional",
        mode="before",
    )
    @classmethod
    def validate_and_normalize_timeframe_keys(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate format của timeframe keys (M5, H1, ...) và normalize về uppercase.
        parse_timeframe sẽ raise nếu format sai.
        """
        return {parse_timeframe(tf_key): conditions for tf_key, conditions in v.items()}


# ── Root Schema ───────────────────────────────────────────────────────────────

class RunConfigSchema(BaseModel):
    symbol:     str
    date_range: DateRangeDef
    indicators: List[IndicatorConfigDef] = Field(default_factory=list)
    strategy:   StrategyConditionsDef

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        symbol = v.strip().upper()
        if not symbol:
            raise ValueError("'symbol' không được rỗng")
        return symbol