import datetime
from typing import Literal

from pydantic import PrivateAttr

from pbi_core.lineage import LineageNode
from pbi_core.ssas.model_tables.base import SsasRenameRecord, SsasTable
from pbi_core.ssas.model_tables.enums import ObjectType
from pbi_core.ssas.server._commands import RenameCommands
from pbi_core.ssas.server.utils import SsasCommands


class Annotation(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/7a16a837-cb88-4cb2-a766-a97c4d0e1f43)
    """

    object_id: int
    object_type: ObjectType
    name: str
    value: str | None = None

    modified_time: datetime.datetime
    _commands: RenameCommands = PrivateAttr(default_factory=lambda: SsasCommands.annotation)

    def object(self) -> SsasTable:
        """Returns the object the annotation is describing.

        Raises:
            TypeError: When the Object Type doesn't map to a know SSAS entity type

        """
        mapper = {
            ObjectType.ATTRIBUTE_HIERARCHY: self.tabular_model.attribute_hierarchies.find,
            ObjectType.CALCULATION_GROUP: self.tabular_model.calculation_groups.find,
            ObjectType.COLUMN: self.tabular_model.columns.find,
            ObjectType.COLUMN_PERMISSION: self.tabular_model.column_permissions.find,
            ObjectType.CULTURE: self.tabular_model.cultures.find,
            ObjectType.DATASOURCE: self.tabular_model.data_sources.find,
            ObjectType.EXPRESSION: self.tabular_model.expressions.find,
            ObjectType.HIERARCHY: self.tabular_model.hierarchies.find,
            ObjectType.KPI: self.tabular_model.kpis.find,
            ObjectType.LEVEL: self.tabular_model.levels.find,
            ObjectType.LINGUISTIC_METADATA: self.tabular_model.linguistic_metadata.find,
            ObjectType.MEASURE: self.tabular_model.measures.find,
            ObjectType.MODEL: lambda _x: self.tabular_model.model,
            ObjectType.PARTITION: self.tabular_model.partitions.find,
            ObjectType.PERSPECTIVE: self.tabular_model.perspectives.find,
            ObjectType.PERSPECTIVE_HIERARCHY: self.tabular_model.perspective_hierarchies.find,
            ObjectType.PERSPECTIVE_MEASURE: self.tabular_model.perspective_measures.find,
            ObjectType.PERSPECTIVE_TABLE: self.tabular_model.perspective_tables.find,
            ObjectType.QUERY_GROUP: self.tabular_model.query_groups.find,
            ObjectType.RELATIONSHIP: self.tabular_model.relationships.find,
            ObjectType.ROLE: self.tabular_model.roles.find,
            ObjectType.ROLE_MEMBERSHIP: self.tabular_model.role_memberships.find,
            ObjectType.TABLE: self.tabular_model.tables.find,
            ObjectType.TABLE_PERMISSION: self.tabular_model.table_permissions.find,
            ObjectType.VARIATION: self.tabular_model.variations.find,
        }
        if self.object_type not in mapper:
            msg = f"Object Type {self.object_type} does not map to a known SSAS entity type."
            raise TypeError(msg)
        return mapper[self.object_type](self.object_id)

    def get_lineage(self, lineage_type: Literal["children", "parents"]) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(self, lineage_type)
        return LineageNode(self, lineage_type, [self.object().get_lineage(lineage_type)])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.id}, on: {self.object()!r}, name: {self.name}, value: {self.value})"
