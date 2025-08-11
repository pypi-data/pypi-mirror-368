import datetime
from typing import TYPE_CHECKING, Literal
from uuid import UUID, uuid4

from pbi_parsers import dax
from pydantic import PrivateAttr

from pbi_core.lineage import LineageNode
from pbi_core.ssas.model_tables.base import SsasRenameRecord, SsasTable
from pbi_core.ssas.model_tables.column import Column
from pbi_core.ssas.model_tables.enums import DataState, DataType
from pbi_core.ssas.server._commands import RenameCommands
from pbi_core.ssas.server.utils import SsasCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.calc_dependency import CalcDependency
    from pbi_core.ssas.model_tables.detail_row_definition import DetailRowDefinition
    from pbi_core.ssas.model_tables.format_string_definition import FormatStringDefinition
    from pbi_core.ssas.model_tables.kpi import KPI
    from pbi_core.ssas.model_tables.table import Table
    from pbi_core.ssas.server.tabular_model.tabular_model import BaseTabularModel


class Measure(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/ab331e04-78f7-49f0-861f-3f155b8b4c5b)
    """

    data_category: str | None = None
    data_type: DataType
    description: str | None = None
    """This description will appear in the hover-over for the measure in the edit mode of the report"""

    detail_rows_definition_id: int | None = None
    display_folder: str | None = None
    error_message: str | None = None
    expression: str | int | float | None = None
    format_string: str | int | None = None
    """A static definition for the formatting of the measure"""

    format_string_definition_id: int | None = None
    """A foreign key to a FormatStringDefinition object. Used for dynamic-type measure formatting.

    Note:
        Mutually exclusive with format_string
    """
    is_hidden: bool = False
    """Controls whether the measure appears in the edit mode of the report"""
    is_simple_measure: bool
    kpi_id: int | None = None
    name: str
    """The name of the measure"""
    state: DataState
    table_id: int

    lineage_tag: UUID = uuid4()
    source_lineage_tag: UUID = uuid4()

    modified_time: datetime.datetime
    structure_modified_time: datetime.datetime

    _commands: RenameCommands = PrivateAttr(default_factory=lambda: SsasCommands.measure)

    def modification_hash(self) -> int:
        return hash((
            self.data_category,
            self.data_type,
            self.description,
            self.detail_rows_definition_id,
            self.display_folder,
            self.error_message,
            self.expression,
            self.format_string,
            self.format_string_definition_id,
            self.is_hidden,
            self.is_simple_measure,
            self.kpi_id,
            self.name,
            self.state,
            self.table_id,
            self.lineage_tag,
            self.source_lineage_tag,
            self.modified_time,
            self.structure_modified_time,
        ))

    def expression_ast(self) -> dax.Expression | None:
        if not isinstance(self.expression, str):
            return None
        ret = dax.to_ast(self.expression)
        if ret is None:
            msg = "Failed to parse DAX expression from measure"
            raise ValueError(msg)
        return ret

    def detail_rows_definition(self) -> "DetailRowDefinition | None":
        if self.detail_rows_definition_id is None:
            return None
        return self.tabular_model.detail_row_definitions.find(self.detail_rows_definition_id)

    def format_string_definition(self) -> "FormatStringDefinition | None":
        if self.format_string_definition_id is None:
            return None
        return self.tabular_model.format_string_definitions.find(self.format_string_definition_id)

    def KPI(self) -> "KPI | None":  # noqa: N802
        if self.kpi_id is not None:
            return self.tabular_model.kpis.find({"id": self.kpi_id})
        return None

    def table(self) -> "Table":
        """The Table object the measure is saved under."""
        return self.tabular_model.tables.find({"id": self.table_id})

    def full_name(self) -> str:
        """Returns the fully qualified name for DAX queries."""
        table_name = self.table().name
        return f"'{table_name}'[{self.name}]"

    def data(self, columns: Column | list[Column], head: int = 100) -> list[dict[str, int | float | str]]:
        if isinstance(columns, Column):
            columns = [columns]
        column_str = "\n".join(
            col.full_name() + "," for col in columns
        )  # this should eventually be converted to jinja imo
        command = f"""
        EVALUATE TOPN({head}, SUMMARIZECOLUMNS(
            {column_str}
            {columns[0].table().name},
            "measure", {self.full_name()}
        ))
        """
        return self.tabular_model.server.query_dax(command)

    def __repr__(self) -> str:
        return f"Measure({self.table().name}.{self.name})"

    def child_measures(self, *, recursive: bool = False) -> set["Measure"]:
        dependent_measures = self.tabular_model.calc_dependencies.find_all({
            "referenced_object_type": "MEASURE",
            "referenced_table": self.table().name,
            "referenced_object": self.name,
            "object_type": "MEASURE",
        })
        child_keys: list[tuple[str | None, str]] = [(m.table, m.object) for m in dependent_measures]
        full_dependencies = [m for m in self.tabular_model.measures if (m.table().name, m.name) in child_keys]

        if recursive:
            recursive_dependencies: set[Measure] = set()
            for dep in full_dependencies:
                if f"[{self.name}]" in str(dep.expression):
                    recursive_dependencies.add(dep)
                    recursive_dependencies.update(dep.child_measures(recursive=True))
            return recursive_dependencies

        return {x for x in full_dependencies if f"[{self.name}]" in str(x.expression)}

    def parent_measures(self, *, recursive: bool = False) -> set["Measure"]:
        """Calculated columns can use Measures too :(."""
        dependent_measures: set[CalcDependency] = self.tabular_model.calc_dependencies.find_all({
            "object_type": "MEASURE",
            "table": self.table().name,
            "object": self.name,
            "referenced_object_type": "MEASURE",
        })
        parent_keys = [(m.referenced_table, m.referenced_object) for m in dependent_measures]
        full_dependencies = [m for m in self.tabular_model.measures if (m.table().name, m.name) in parent_keys]

        if recursive:
            recursive_dependencies: set[Measure] = set()
            for dep in full_dependencies:
                if f"[{dep.name}]" in str(self.expression):
                    recursive_dependencies.add(dep)
                    recursive_dependencies.update(dep.parent_measures(recursive=True))
            return recursive_dependencies

        return {x for x in full_dependencies if f"[{x.name}]" in str(self.expression)}

    def child_columns(self, *, recursive: bool = False) -> set["Column"]:
        """Only occurs when the dependent column is calculated (expression is not None)."""
        dependent_measures = self.tabular_model.calc_dependencies.find_all({
            "referenced_object_type": "MEASURE",
            "referenced_table": self.table().name,
            "referenced_object": self.name,
        })
        child_keys = [(m.table, m.object) for m in dependent_measures if m.object_type in {"CALC_COLUMN", "COLUMN"}]
        full_dependencies = [m for m in self.tabular_model.columns if (m.table().name, m.explicit_name) in child_keys]

        if recursive:
            recursive_dependencies: set[Column] = set()
            for dep in full_dependencies:
                if f"[{self.name}]" in str(dep.expression):
                    recursive_dependencies.add(dep)
                    recursive_dependencies.update(dep.child_columns(recursive=True))
            return recursive_dependencies

        return {x for x in full_dependencies if f"[{self.name}]" in str(x.expression)}

    def parent_columns(self, *, recursive: bool = False) -> set["Column"]:
        """Only occurs when column is calculated."""
        dependent_measures = self.tabular_model.calc_dependencies.find_all({
            "object_type": "MEASURE",
            "table": self.table().name,
            "object": self.name,
        })
        parent_keys = {
            (m.referenced_table, m.referenced_object)
            for m in dependent_measures
            if m.referenced_object_type in {"CALC_COLUMN", "COLUMN"}
        }
        full_dependencies = [c for c in self.tabular_model.columns if (c.table().name, c.explicit_name) in parent_keys]

        if recursive:
            recursive_dependencies: set[Column] = set()
            for dep in full_dependencies:
                if f"[{dep.explicit_name}]" in str(self.expression):
                    recursive_dependencies.add(dep)
                    recursive_dependencies.update(dep.parent_columns(recursive=True))
            return recursive_dependencies

        return {x for x in full_dependencies if f"[{x.explicit_name}]" in str(self.expression)}

    def parents(self, *, recursive: bool = False) -> "set[Column | Measure]":
        """Returns all columns and measures this Measure is dependent on."""
        full_dependencies = self.parent_columns() | self.parent_measures()
        if recursive:
            recursive_dependencies: set[Column | Measure] = set()
            for dep in full_dependencies:
                recursive_dependencies.add(dep)
                recursive_dependencies.update(dep.parents(recursive=True))
            return recursive_dependencies

        return full_dependencies

    def children(self, *, recursive: bool = False) -> "set[Column | Measure]":
        """Returns all columns and measures dependent on this Measure."""
        full_dependencies = self.child_columns() | self.child_measures()
        if recursive:
            recursive_dependencies: set[Column | Measure] = set()
            for dep in full_dependencies:
                recursive_dependencies.add(dep)
                recursive_dependencies.update(dep.children(recursive=True))
            return recursive_dependencies

        return full_dependencies

    def get_lineage(self, lineage_type: Literal["children", "parents"]) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(
                self,
                lineage_type,
                [c.get_lineage(lineage_type) for c in self.child_measures() | self.child_columns()],
            )
        parent_nodes: list[SsasTable | None] = [
            self.KPI(),
            self.table(),
            *self.parent_measures(),
            *self.parent_columns(),
        ]
        parent_lineage = [c.get_lineage(lineage_type) for c in parent_nodes if c is not None]
        return LineageNode(self, lineage_type, parent_lineage)

    @staticmethod
    def new(
        name: str,
        expression: str,
        table: "int | Table",
        ssas: "BaseTabularModel",
    ) -> "Measure":
        table_id = table if isinstance(table, int) else table.id

        return Measure(
            name=name,
            data_type=DataType.UNKNOWN,
            is_simple_measure=True,
            state=DataState.READY,
            modified_time=datetime.datetime.now(tz=datetime.UTC),
            structure_modified_time=datetime.datetime.now(tz=datetime.UTC),
            expression=expression,
            table_id=table_id,
            tabular_model=ssas,
            id=-1,
        )
