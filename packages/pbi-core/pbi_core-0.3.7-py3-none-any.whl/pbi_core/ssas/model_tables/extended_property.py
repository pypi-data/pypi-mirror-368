import datetime

from pbi_core.pydantic import BaseValidation
from pbi_core.static_files.layout.sources.column import ColumnSource
from pydantic import Json

from .base import SsasRenameRecord, SsasTable
from .enums import ObjectType


class BinSize(BaseValidation):
    value: float
    unit: int


class BinningMetadata(BaseValidation):
    binSize: BinSize


class ExtendedPropertyValue(BaseValidation):
    version: int
    daxTemplateName: str | None = None
    groupedColumns: list[ColumnSource] | None = None
    binningMetadata: BinningMetadata | None = None


class ExtendedProperty(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/5c1521e5-defe-4ba2-9558-b67457e94569)
    """

    object_id: int
    object_type: ObjectType
    name: str
    type: ObjectType
    value: Json[ExtendedPropertyValue]

    modified_time: datetime.datetime

    def object(self) -> "SsasTable":
        """Returns the object the property is describing."""
        mapper: dict[ObjectType, SsasTable] = {
            ObjectType.MODEL: self.tabular_model.model,
            ObjectType.DATASOURCE: self.tabular_model.data_sources.find(self.object_id),
            ObjectType.TABLE: self.tabular_model.tables.find(self.object_id),
            ObjectType.COLUMN: self.tabular_model.columns.find(self.object_id),
            ObjectType.ATTRIBUTE_HIERARCHY: self.tabular_model.attribute_hierarchies.find(self.object_id),
            ObjectType.PARTITION: self.tabular_model.partitions.find(self.object_id),
            ObjectType.RELATIONSHIP: self.tabular_model.relationships.find(self.object_id),
            ObjectType.MEASURE: self.tabular_model.measures.find(self.object_id),
            ObjectType.HIERARCHY: self.tabular_model.hierarchies.find(self.object_id),
            ObjectType.LEVEL: self.tabular_model.levels.find(self.object_id),
            ObjectType.KPI: self.tabular_model.kpis.find(self.object_id),
            ObjectType.CULTURE: self.tabular_model.cultures.find(self.object_id),
            ObjectType.LINGUISTIC_METADATA: self.tabular_model.linguistic_metadata.find(self.object_id),
            ObjectType.PERSPECTIVE: self.tabular_model.perspectives.find(self.object_id),
            ObjectType.PERSPECTIVE_TABLE: self.tabular_model.perspective_tables.find(self.object_id),
            ObjectType.PERSPECTIVE_HIERARCHY: self.tabular_model.perspective_hierarchies.find(self.object_id),
            ObjectType.PERSPECTIVE_MEASURE: self.tabular_model.perspective_measures.find(self.object_id),
            ObjectType.ROLE: self.tabular_model.roles.find(self.object_id),
            ObjectType.ROLE_MEMBERSHIP: self.tabular_model.role_memberships.find(self.object_id),
            ObjectType.TABLE_PERMISSION: self.tabular_model.table_permissions.find(self.object_id),
            ObjectType.VARIATION: self.tabular_model.variations.find(self.object_id),
            ObjectType.EXPRESSION: self.tabular_model.expressions.find(self.object_id),
            ObjectType.COLUMN_PERMISSION: self.tabular_model.column_permissions.find(self.object_id),
            ObjectType.CALCULATION_GROUP: self.tabular_model.calculation_groups.find(self.object_id),
            ObjectType.QUERY_GROUP: self.tabular_model.query_groups.find(self.object_id),
        }
        return mapper[self.object_type]

    @classmethod
    def _db_command_obj_name(cls) -> str:
        return "ExtendedProperties"
