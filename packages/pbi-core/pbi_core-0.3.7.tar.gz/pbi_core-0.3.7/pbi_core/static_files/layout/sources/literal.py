from datetime import UTC, datetime

from pbi_core.static_files.layout._base_node import LayoutNode

PrimitiveValue = int | str | datetime | bool | None
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def parse_literal(literal_val: str) -> PrimitiveValue:
    if literal_val == "null":
        return None
    if literal_val in {"true", "false"}:
        return literal_val == "true"
    if literal_val.endswith("L"):
        return int(literal_val[:-1])
    if literal_val.startswith("datetime"):
        return datetime.strptime(literal_val[9:-1], DATETIME_FORMAT).replace(tzinfo=UTC)
    return literal_val[1:-1]


class _LiteralSourceHelper(LayoutNode):
    Value: str


class LiteralSource(LayoutNode):
    Literal: _LiteralSourceHelper

    def value(self) -> PrimitiveValue:
        return parse_literal(self.Literal.Value)

    def __repr__(self) -> str:
        return f"LiteralSource({self.Literal.Value})"
