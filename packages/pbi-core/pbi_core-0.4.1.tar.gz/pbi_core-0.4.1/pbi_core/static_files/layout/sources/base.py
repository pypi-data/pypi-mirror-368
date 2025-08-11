from enum import IntEnum
from typing import Annotated, Any

from pydantic import Discriminator, Tag

from pbi_core.static_files.layout._base_node import LayoutNode


class EntityType(IntEnum):
    NA = 1
    NA2 = 0
    NA3 = 2


class Entity(LayoutNode):
    Entity: str
    Name: str | None = None
    Type: EntityType | None = EntityType.NA2

    def table(self) -> str:
        return self.Entity

    def table_mapping(self) -> dict[str, str]:
        if self.Name is None:
            return {}
        return {self.Name: self.Entity}

    @staticmethod
    def create(entity: str) -> "Entity":
        return Entity.model_validate({"Entity": entity})

    def __repr__(self) -> str:
        return f"Entity({self.Name}: {self.Entity})"


class Source(LayoutNode):
    Source: str

    def table(self) -> str:
        return self.Source


def get_type(v: object | dict[str, Any]) -> str:
    if isinstance(v, dict):
        if "Source" in v:
            return "Source"
        if "Entity" in v:
            return "Entity"
        raise TypeError(v)
    return v.__class__.__name__


SourceRefSource = Annotated[
    Annotated[Entity, Tag("Entity")] | Annotated[Source, Tag("Source")],
    Discriminator(get_type),
]


class TransformTableRef(LayoutNode):
    TransformTableRef: SourceRefSource

    def table(self) -> str:
        return self.TransformTableRef.table()


class SourceRef(LayoutNode):
    SourceRef: SourceRefSource

    def table(self) -> str:
        return self.SourceRef.table()


def get_source_expression_type(v: object | dict[str, Any]) -> str:
    if isinstance(v, dict):
        if "SourceRef" in v:
            return "SourceRef"
        if "TransformTableRef" in v:
            return "TransformTableRef"
        raise TypeError(v)
    return v.__class__.__name__


SourceExpressionUnion = Annotated[
    Annotated[TransformTableRef, Tag("TransformTableRef")] | Annotated[SourceRef, Tag("SourceRef")],
    Discriminator(get_source_expression_type),
]


class SourceExpression(LayoutNode):
    Expression: SourceExpressionUnion
    Property: str

    def table(self) -> str:
        return self.Expression.table()

    def column(self) -> str:
        return self.Property

    @staticmethod
    def create(table: str, column: str) -> "SourceExpression":
        entity = Entity.create(entity=table)
        ret: SourceExpression = SourceExpression.model_validate({
            "Expression": {
                "SourceRef": entity.model_dump_json(),
                "Property": column,
            },
        })
        return ret
