from typing import TYPE_CHECKING

from pbi_core.pydantic.main import BaseValidation

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.column import Column
    from pbi_core.ssas.model_tables.measure import Measure
    from pbi_core.ssas.model_tables.table import Table
    from pbi_core.ssas.server.tabular_model.tabular_model import BaseTabularModel


class ModelColumnReference(BaseValidation):
    column: str
    table: str

    def to_model(self, tabular_model: "BaseTabularModel") -> "Column":
        return tabular_model.columns.find(lambda c: (c.explicit_name == self.column) and (c.table().name == self.table))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ModelColumnReference):
            return False
        return (self.column == other.column) and (self.table == other.table)

    def __hash__(self) -> int:
        return hash((self.column, self.table))


class ModelTableReference(BaseValidation):
    table: str

    def to_model(self, tabular_model: "BaseTabularModel") -> "Table":
        return tabular_model.tables.find(lambda t: (t.name == self.table))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ModelTableReference):
            return False
        return self.table == other.table

    def __hash__(self) -> int:
        return hash(self.table)


class ModelMeasureReference(BaseValidation):
    measure: str
    table: str

    def to_model(self, tabular_model: "BaseTabularModel") -> "Measure":
        return tabular_model.measures.find(lambda m: (m.name == self.measure) and (m.table().name == self.table))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ModelMeasureReference):
            return False
        return (self.measure == other.measure) and (self.table == other.table)

    def __hash__(self) -> int:
        return hash((self.measure, self.table))
