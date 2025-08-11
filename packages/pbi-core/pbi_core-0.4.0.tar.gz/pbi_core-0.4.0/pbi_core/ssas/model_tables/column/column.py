import datetime
from typing import ClassVar
from uuid import UUID, uuid4

from pydantic import PrivateAttr
from structlog import BoundLogger

from pbi_core.logging import get_logger
from pbi_core.ssas.model_tables.base import SsasRenameRecord
from pbi_core.ssas.model_tables.enums import DataState, DataType
from pbi_core.ssas.server._commands import RenameCommands
from pbi_core.ssas.server.utils import SsasCommands

from .commands import CommandMixin
from .enums import Alignment, ColumnType, EncodingHint, SummarizedBy

logger: BoundLogger = get_logger()


class Column(SsasRenameRecord, CommandMixin):  # pyright: ignore[reportIncompatibleMethodOverride]
    """A column of an SSAS table.

    PowerBI spec: [Power BI](https://learn.microsoft.com/en-us/analysis-services/tabular-models/column-properties-ssas-tabular?view=asallproducts-allversions)

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/00a9ec7a-5f4d-4517-8091-b370fe2dc18b)
    """

    _field_mapping: ClassVar[dict[str, str]] = {
        "description": "Description",
    }
    _db_name_field: str = "ExplicitName"
    _read_only_fields = ("table_id",)

    alignment: Alignment
    attribute_hierarchy_id: int
    column_origin_id: int | None = None
    column_storage_id: int
    data_category: str | None = None
    description: str | None = None
    display_folder: str | None = None
    display_ordinal: int
    encoding_hint: EncodingHint
    error_message: str | None = None
    explicit_data_type: DataType  # enum
    explicit_name: str | None = None
    expression: str | int | None = None
    format_string: int | str | None = None
    inferred_data_type: int  # enum
    inferred_name: str | None = None
    is_available_in_mdx: bool
    is_default_image: bool
    is_default_label: bool
    is_hidden: bool
    is_key: bool
    is_nullable: bool
    is_unique: bool
    keep_unique_rows: bool
    lineage_tag: UUID = uuid4()
    sort_by_column_id: int | None = None
    source_column: str | None = None
    state: DataState
    summarize_by: SummarizedBy
    system_flags: int
    table_id: int
    table_detail_position: int
    type: ColumnType

    modified_time: datetime.datetime
    refreshed_time: datetime.datetime
    structure_modified_time: datetime.datetime

    _commands: RenameCommands = PrivateAttr(default_factory=lambda: SsasCommands.column)

    def __repr__(self) -> str:
        return f"Column({self.table().name}.{self.pbi_core_name()})"
