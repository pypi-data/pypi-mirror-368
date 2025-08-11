import datetime
from typing import TYPE_CHECKING

from pbi_parsers import dax
from pydantic import PrivateAttr

from pbi_core.ssas.model_tables.base import SsasEditableRecord, SsasTable
from pbi_core.ssas.model_tables.enums import DataState, ObjectType
from pbi_core.ssas.server._commands import BaseCommands
from pbi_core.ssas.server.utils import SsasCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables._group import Group


class FormatStringDefinition(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/b756b0c1-c912-4218-80dc-7ff09d0968ff)
    """

    object_type: ObjectType
    object_id: int
    error_message: str | None = None
    """When no issue exists, this field is blank"""
    expression: str
    """The DAX expression defining the """
    state: DataState

    modified_time: datetime.datetime

    _commands: BaseCommands = PrivateAttr(default_factory=lambda: SsasCommands.format_string_definition)

    def pbi_core_name(self) -> str:
        return str(self.object_id)

    def object(self) -> SsasTable:
        """Returns the object the annotation is describing.

        Raises:
            TypeError: When the Object Type doesn't map to a know SSAS entity type

        """
        if self.object_type == ObjectType.MODEL:
            return self.tabular_model.model

        type_mapper: dict[ObjectType, Group] = {
            ObjectType.DATASOURCE: self.tabular_model.data_sources,
            ObjectType.TABLE: self.tabular_model.tables,
            ObjectType.COLUMN: self.tabular_model.columns,
            ObjectType.ATTRIBUTE_HIERARCHY: self.tabular_model.attribute_hierarchies,
            ObjectType.PARTITION: self.tabular_model.partitions,
            ObjectType.RELATIONSHIP: self.tabular_model.relationships,
            ObjectType.MEASURE: self.tabular_model.measures,
            ObjectType.HIERARCHY: self.tabular_model.hierarchies,
            ObjectType.LEVEL: self.tabular_model.levels,
            ObjectType.KPI: self.tabular_model.kpis,
            ObjectType.CULTURE: self.tabular_model.cultures,
            ObjectType.LINGUISTIC_METADATA: self.tabular_model.linguistic_metadata,
            ObjectType.PERSPECTIVE: self.tabular_model.perspectives,
            ObjectType.PERSPECTIVE_TABLE: self.tabular_model.perspective_tables,
            ObjectType.PERSPECTIVE_HIERARCHY: self.tabular_model.perspective_hierarchies,
            ObjectType.PERSPECTIVE_MEASURE: self.tabular_model.perspective_measures,
            ObjectType.ROLE: self.tabular_model.roles,
            ObjectType.ROLE_MEMBERSHIP: self.tabular_model.role_memberships,
            ObjectType.TABLE_PERMISSION: self.tabular_model.table_permissions,
            ObjectType.VARIATION: self.tabular_model.variations,
            ObjectType.EXPRESSION: self.tabular_model.expressions,
            ObjectType.COLUMN_PERMISSION: self.tabular_model.column_permissions,
            ObjectType.CALCULATION_GROUP: self.tabular_model.calculation_groups,
            ObjectType.QUERY_GROUP: self.tabular_model.query_groups,
        }
        if self.object_type not in type_mapper:
            msg = f"Object Type {self.object_type} does not map to a known SSAS entity type."
            raise TypeError(msg)

        return type_mapper[self.object_type].find(self.object_id)

    def expression_ast(self) -> dax.Expression | None:
        if not isinstance(self.expression, str):
            return None
        ret = dax.to_ast(self.expression)
        if ret is None:
            msg = "Failed to parse DAX expression from format string definition"
            raise ValueError(msg)
        return ret

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.id}, on: {self.object()!r})"
