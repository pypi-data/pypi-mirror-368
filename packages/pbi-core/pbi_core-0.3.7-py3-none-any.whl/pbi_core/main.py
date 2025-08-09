from typing import TYPE_CHECKING

from .logging import get_logger
from .ssas.model_tables.column import Column
from .ssas.model_tables.measure import Measure
from .ssas.server import BaseTabularModel, LocalTabularModel, get_or_create_local_server
from .static_files import StaticFiles
from .static_files.model_references import ModelColumnReference, ModelMeasureReference

logger = get_logger()

if TYPE_CHECKING:
    from _typeshed import StrPath
    from pbi_core.ssas.model_tables.table import Table


class BaseReport:
    pass


class WorkspaceReport(BaseReport):
    ssas: BaseTabularModel


class LocalReport(BaseReport):
    """An instance of a PowerBI report from a local PBIX file.

    Args:
        static_files (StaticElements): An instance of all the static files (except DataModel) in the PBIX file

    Examples:
        ```python
        from pbi_core import LocalReport

        report = LocalReport.load_pbix("example.pbix")
        report.save_pbix("example_out.pbix")
        ```

    """

    ssas: LocalTabularModel
    """An instance of a local SSAS Server"""

    static_files: StaticFiles
    """Classes representing the static design portions of the PBIX report"""

    def __init__(self, ssas: LocalTabularModel, static_files: StaticFiles) -> None:
        self.ssas = ssas
        self.static_files = static_files

    @staticmethod
    def load_pbix(path: "StrPath", *, kill_ssas_on_exit: bool = True) -> "LocalReport":
        """Creates a ``LocalReport`` instance from a PBIX file.

        Args:
                path (StrPath): The absolute or local path to the PBIX report
                kill_ssas_on_exit (bool, optional): The LocalReport object depends on a ``msmdsrv.exe`` process that is
                    independent of the Python session process. If this function creates a new ``msmdsrv.exe`` instance
                    and kill_ssas_on_exit is true, the process will be killed on exit.

        Examples:
            ```python

               from pbi_core import LocalReport

               report = LocalReport.load_pbix("example.pbix")
            ```

        Returns:
                LocalReport: the local PBIX class

        """
        logger.info("Loading PBIX", path=path)
        server = get_or_create_local_server(kill_on_exit=kill_ssas_on_exit)
        ssas = server.load_pbix(path)
        static_files = StaticFiles.load_pbix(path)
        return LocalReport(ssas=ssas, static_files=static_files)

    def save_pbix(self, path: "StrPath") -> None:
        """Creates a new PBIX with the information in this class to the given path.

        Examples:
            ```python

               from pbi_core import LocalReport

               report = LocalReport.load_pbix("example.pbix")
            ```
               report.save_pbix("example_out.pbix")

        Args:
                path (StrPath): the path (relative or absolute) to save the PBIX to

        """
        self.ssas.save_pbix(path)
        self.static_files.save_pbix(path)

    def cleanse_ssas_model(self) -> None:
        """Removes all unused tables, columns, and measures in an SSAS model.

        1. Uses the layout to identify all Measures and Columns being used by the report visuals and filters.
        2. Uses SSAS relationships to identify additional columns and tables used for cross-table filtering.
        3. Traces calculation dependencies (on measures and calculated columns) to identify measures and columns used
             to create report fields
        4. Removes any measure/column that is:
            1. Not in results of 1-3
            2. Not part of a system table
        5. Removes any table that has no column/measure used in the report and no active relationship with a reporting
            table
        """
        report_references = self.static_files.layout.get_ssas_elements()
        model_values = (
            [x.to_model(self.ssas) for x in report_references]
            + [relationship.to_column() for relationship in self.ssas.relationships]
            + [relationship.from_column() for relationship in self.ssas.relationships]
        )
        ret: list[Measure | Column] = []
        for val in model_values:
            ret.append(val)
            ret.extend(val.parents(recursive=True))

        used_tables = {x.table() for x in ret}
        used_measures = {
            x
            for x in ret
            if isinstance(
                x,
                Measure,
            )
        }
        used_columns = {x for x in ret if isinstance(x, Column)}

        # In the examples I've seen, there's a table named "DateTableTemplate_<UUID>" that doesn't seem used,
        # but breaks the system when removed
        tables_to_drop = {t for t in self.ssas.tables if t not in used_tables and not t.is_private}
        columns_to_drop = {
            c
            for c in self.ssas.columns
            if c not in used_columns
            and not c.table().name.startswith("DateTableTemplate")
            and c.table() not in tables_to_drop
        }
        affected_tables: dict[Table, list[Column]] = {}
        for c in columns_to_drop:
            t = c.table()
            if t not in tables_to_drop:
                affected_tables.setdefault(t, []).append(c)

        measures_to_drop = {m for m in self.ssas.measures if m not in used_measures}
        # TODO: convert to batch deletion
        for t in tables_to_drop:
            t.delete()
        for c in columns_to_drop:
            c.delete()
        for m in measures_to_drop:
            m.delete()
        for affected_table, table_columns_to_drop in affected_tables.items():
            for partition in affected_table.partitions():
                partition.remove_columns(table_columns_to_drop)


def column_finder(c: Column, reference: ModelColumnReference) -> bool:
    return c.explicit_name == reference.column and c.table().name == reference.table


def measure_finder(m: Measure, reference: ModelMeasureReference) -> bool:
    return m.name == reference.measure and m.table().name == reference.table
