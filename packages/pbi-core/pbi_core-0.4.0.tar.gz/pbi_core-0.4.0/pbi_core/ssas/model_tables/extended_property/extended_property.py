import datetime

from git import TYPE_CHECKING
from pydantic import Json, PrivateAttr

from pbi_core.pydantic import BaseValidation
from pbi_core.ssas.model_tables.base import SsasRenameRecord, SsasTable
from pbi_core.ssas.model_tables.enums import ObjectType
from pbi_core.ssas.server._commands import RenameCommands
from pbi_core.ssas.server.utils import SsasCommands
from pbi_core.static_files.layout.sources.column import ColumnSource

if TYPE_CHECKING:
    from collections.abc import Callable


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

    _commands: RenameCommands = PrivateAttr(default_factory=lambda: SsasCommands.extended_property)

    def object(self) -> "SsasTable":
        """Returns the object the property is describing."""
        mapper: dict[ObjectType, Callable[[int], SsasTable]] = {
            ObjectType.MODEL: lambda _x: self.tabular_model.model,
            ObjectType.DATASOURCE: self.tabular_model.data_sources.find,
            ObjectType.TABLE: self.tabular_model.tables.find,
            ObjectType.COLUMN: self.tabular_model.columns.find,
            ObjectType.ATTRIBUTE_HIERARCHY: self.tabular_model.attribute_hierarchies.find,
            ObjectType.PARTITION: self.tabular_model.partitions.find,
            ObjectType.RELATIONSHIP: self.tabular_model.relationships.find,
            ObjectType.MEASURE: self.tabular_model.measures.find,
            ObjectType.HIERARCHY: self.tabular_model.hierarchies.find,
            ObjectType.LEVEL: self.tabular_model.levels.find,
            ObjectType.KPI: self.tabular_model.kpis.find,
            ObjectType.CULTURE: self.tabular_model.cultures.find,
            ObjectType.LINGUISTIC_METADATA: self.tabular_model.linguistic_metadata.find,
            ObjectType.PERSPECTIVE: self.tabular_model.perspectives.find,
            ObjectType.PERSPECTIVE_TABLE: self.tabular_model.perspective_tables.find,
            ObjectType.PERSPECTIVE_HIERARCHY: self.tabular_model.perspective_hierarchies.find,
            ObjectType.PERSPECTIVE_MEASURE: self.tabular_model.perspective_measures.find,
            ObjectType.ROLE: self.tabular_model.roles.find,
            ObjectType.ROLE_MEMBERSHIP: self.tabular_model.role_memberships.find,
            ObjectType.TABLE_PERMISSION: self.tabular_model.table_permissions.find,
            ObjectType.VARIATION: self.tabular_model.variations.find,
            ObjectType.EXPRESSION: self.tabular_model.expressions.find,
            ObjectType.COLUMN_PERMISSION: self.tabular_model.column_permissions.find,
            ObjectType.CALCULATION_GROUP: self.tabular_model.calculation_groups.find,
            ObjectType.QUERY_GROUP: self.tabular_model.query_groups.find,
        }
        return mapper[self.object_type](self.object_id)

    @classmethod
    def _db_command_obj_name(cls) -> str:
        return "ExtendedProperties"
