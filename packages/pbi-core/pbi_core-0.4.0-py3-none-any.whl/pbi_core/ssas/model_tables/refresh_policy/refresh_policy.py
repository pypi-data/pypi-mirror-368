from pydantic import PrivateAttr

from pbi_core.ssas.model_tables.base import SsasEditableRecord
from pbi_core.ssas.server._commands import BaseCommands
from pbi_core.ssas.server.utils import SsasCommands

from .enums import Granularity, PolicyType, RefreshMode


class RefreshPolicy(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/e11ae511-5064-470b-8abc-e2a4dd3999e6)
    This class represents the refresh policy for a partition in a Tabular model.
    """

    incremental_granularity: Granularity
    incremental_periods: int
    incremental_periods_offset: int
    mode: RefreshMode
    policy_type: PolicyType
    polling_expression: str
    rolling_window_granularity: Granularity
    rolling_window_periods: int
    source_expression: str
    table_id: int

    _commands: BaseCommands = PrivateAttr(default_factory=lambda: SsasCommands.refresh_policy)
