import datetime
from typing import TYPE_CHECKING, Literal
from uuid import UUID, uuid4

from bs4 import BeautifulSoup
from pydantic import PrivateAttr

from pbi_core.lineage import LineageNode
from pbi_core.ssas.model_tables.base import RefreshType, SsasRefreshRecord
from pbi_core.ssas.model_tables.column import Column
from pbi_core.ssas.model_tables.enums import DataCategory
from pbi_core.ssas.model_tables.measure import Measure
from pbi_core.ssas.model_tables.partition import Partition
from pbi_core.ssas.server._commands import RefreshCommands
from pbi_core.ssas.server.utils import SsasCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.calculation_group import CalculationGroup
    from pbi_core.ssas.model_tables.detail_row_definition import DetailRowDefinition
    from pbi_core.ssas.model_tables.model import Model
    from pbi_core.ssas.model_tables.refresh_policy import RefreshPolicy


class Table(SsasRefreshRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/6360ac84-0717-4170-bce0-284cbef419ca)
    """

    _refresh_type = RefreshType.DATA_ONLY

    alternate_source_precedence: int
    calculation_group_id: int | None = None
    data_category: DataCategory | None = None
    default_detail_rows_defintion_id: int | None = None
    description: str | None = None
    """A description of the table, which may be used in the hover tooltip in edit mode"""
    exclude_from_automatic_aggregations: bool = False
    exclude_from_model_refresh: bool
    """Controls whether this table is included in the model-wide refresh process"""
    is_hidden: bool
    """Controls whether the table appears in the edit mode of the report"""
    is_private: bool
    model_id: int
    """The ID of the model this table belongs to"""
    name: str
    """The name of the table as it appears in the report"""
    refresh_policy_id: int | None = None
    show_as_variations_only: bool
    system_flags: int
    system_managed: bool | None = None
    table_storage_id: int | None = None

    lineage_tag: UUID = uuid4()
    source_lineage_tag: UUID = uuid4()

    modified_time: datetime.datetime
    structure_modified_time: datetime.datetime

    _commands: RefreshCommands = PrivateAttr(default_factory=lambda: SsasCommands.table)

    def modification_hash(self) -> int:
        return hash((
            self.name,
            self.description,
            self.is_hidden,
        ))

    def calculation_group(self) -> "CalculationGroup | None":
        if self.calculation_group_id is None:
            return None
        return self.tabular_model.calculation_groups.find(self.calculation_group_id)

    def refresh_policy(self) -> "RefreshPolicy | None":
        if self.refresh_policy_id is None:
            return None
        return self.tabular_model.refresh_policies.find(self.refresh_policy_id)

    def is_system_table(self) -> bool:
        return bool(self.system_flags >> 1 % 2)

    def is_from_calculated_table(self) -> bool:
        return bool(self.system_flags % 2)

    def data(self, head: int = 100) -> list[dict[str, int | float | str]]:
        """Extracts records from the table in SSAS.

        Args:
            head (int): The number of records to return from the table.

        Returns:
            list[dict[str, int | float | str]]: A list of SSAS records in dictionary form.
                The keys are the field names and the values are the record values

        """
        return self.tabular_model.server.query_dax(
            f"EVALUATE TOPN({head}, ALL('{self.name}'))",
            db_name=self.tabular_model.db_name,
        )

    def partitions(self) -> set[Partition]:
        """Get associated dependent partitions.

        Returns:
            (set[Partition]): A list of the partitions containing data for this table

        """
        return self.tabular_model.partitions.find_all({"table_id": self.id})

    def columns(self) -> set[Column]:
        """Get associated dependent partitions.

        Returns:
            (set[Column]): A list of the columns in this table

        """
        return self.tabular_model.columns.find_all({"table_id": self.id})

    def default_row_definition(self) -> "DetailRowDefinition | None":
        if self.default_detail_rows_defintion_id is None:
            return None
        return self.tabular_model.detail_row_definitions.find(self.default_detail_rows_defintion_id)

    def table_measures(self) -> set[Measure]:
        """Get measures saved to this table.

        Returns:
            (set[Measure]): A list of measures saved to this table

        Note:
            These measures do not necessarily have calculations that depend on this table.
                For that use `table.measures()`

        """
        return self.tabular_model.measures.find_all({"table_id": self.id})

    def measures(self, *, recursive: bool = False) -> set[Measure]:
        """Get measures that logically depend on this table.

        Examples:
            ```python
            print(measure.expression)
            # sumx(example, [a])

            Table(name=example).measures()
            # [..., Measure(name='measure'), ...]
            ```
        Args:
            recursive (bool): Whether to include measures that depend on other measures.

        Returns:
            (set[Measure]): A list of measures that logically depend this table

        Note:
            These measures are not necessarily saved physically to this table. For that use `table.table_measures()`

        """
        ret = set()
        for col in self.columns():
            ret.update(col.child_measures(recursive=recursive))
        return ret

    def model(self) -> "Model":
        return self.tabular_model.model

    def get_lineage(self, lineage_type: Literal["children", "parents"]) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(
                self,
                lineage_type,
                [col.get_lineage(lineage_type) for col in self.columns()]
                + [partition.get_lineage(lineage_type) for partition in self.partitions()]
                + [measure.get_lineage(lineage_type) for measure in self.measures()],
            )
        return LineageNode(self, lineage_type, [self.model().get_lineage(lineage_type)])

    def refresh(self, *, include_model_refresh: bool = True) -> list[BeautifulSoup]:  # pyright: ignore reportIncompatibleMethodOverride
        """Needs a model refresh to properly propogate the update."""
        if include_model_refresh:
            return [
                super().refresh(),
                self.model().refresh(),
            ]
        return [super().refresh()]
