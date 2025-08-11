import datetime

from pydantic import PrivateAttr

from pbi_core.ssas.model_tables.base import SsasEditableRecord, SsasTable
from pbi_core.ssas.model_tables.enums import ObjectType
from pbi_core.ssas.server._commands import BaseCommands
from pbi_core.ssas.server.utils import SsasCommands

from .enums import Property


class ObjectTranslation(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/1eade819-5599-4ddd-9bf5-7d365806069d)
    """

    altered: bool
    culture_id: int
    object_id: int
    object_type: ObjectType
    property: Property
    value: str

    modified_time: datetime.datetime

    _commands: BaseCommands = PrivateAttr(default_factory=lambda: SsasCommands.object_translation)

    def object(self) -> SsasTable:
        """Returns the object the annotation is describing.

        Raises:
            TypeError: When the Object Type doesn't map to a know SSAS entity type

        """
        if self.object_type == ObjectType.MODEL:
            return self.tabular_model.model
        mapper = {
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
        if self.object_type in mapper:
            return mapper[self.object_type]
        msg = f"No logic implemented for type {self.object_type}"
        raise TypeError(msg)
