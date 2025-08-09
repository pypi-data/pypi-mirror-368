import datetime
from typing import TYPE_CHECKING

from pbi_core.ssas.model_tables.enums import DataState

from .base import SsasRenameRecord

if TYPE_CHECKING:
    from .calculation_group import CalculationGroup
    from .format_string_definition import FormatStringDefinition


class CalculationItem(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/f5a398a7-ff65-45f0-a865-b561416f1cb4)
    """

    calculation_group_id: int
    description: str
    error_message: str
    expression: str
    format_string_definition_id: int
    name: str
    ordinal: int
    state: DataState

    modified_time: datetime.datetime

    def format_string_definition(self) -> "FormatStringDefinition":
        return self.tabular_model.format_string_definitions.find(self.format_string_definition_id)

    def calculation_group(self) -> "CalculationGroup":
        return self.tabular_model.calculation_groups.find(self.calculation_group_id)
