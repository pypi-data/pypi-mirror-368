from typing import Literal

from pbi_parsers import dax

from .enums import Alignment, ColumnType
from .relationships import RelationshipMixin


class HelpersMixin(RelationshipMixin):
    alignment: Alignment
    expression: str | int | None
    system_flags: int
    explicit_name: str | None
    id: int
    inferred_name: str | None
    type: ColumnType

    def expression_ast(self) -> dax.Expression | None:
        if not isinstance(self.expression, str):
            return None
        return dax.to_ast(self.expression)

    def is_system_table(self) -> bool:
        return bool(self.system_flags >> 1 % 2)

    def is_from_calculated_table(self) -> bool:
        return bool(self.system_flags % 2)

    def is_calculated_column(self) -> bool:
        return self.type == ColumnType.CALCULATED

    def is_normal(self) -> bool:
        return self.type != ColumnType.ROW_NUMBER

    def pbi_core_name(self) -> str:
        """Returns the name displayed in the PBIX report."""
        if self.explicit_name is not None:
            return self.explicit_name
        if self.inferred_name is not None:
            return self.inferred_name
        return str(self.id)

    def _column_type(self) -> Literal["COLUMN", "CALC_COLUMN"]:
        if self.type == ColumnType.DATA:
            return "COLUMN"
        return "CALC_COLUMN"

    def modification_hash(self) -> int:
        return hash((
            self.alignment,
            self.explicit_name,
            self.sort_by_column_id,
            self.table_id,
        ))

    def full_name(self) -> str:
        """Returns the fully qualified name for DAX queries."""
        table_name = self.table().name
        return f"'{table_name}'[{self.explicit_name}]"

    def data(self, head: int = 100) -> list[int | float | str]:
        table_name = self.table().name
        ret = self.tabular_model.server.query_dax(
            f"EVALUATE TOPN({head}, SELECTCOLUMNS(ALL('{table_name}'), {self.full_name()}))",
            db_name=self.tabular_model.db_name,
        )
        return [next(iter(row.values())) for row in ret]
