from enum import IntEnum

from .base import SsasEditableRecord


class PolicyType(IntEnum):
    Basic = 0


class Granularity(IntEnum):
    Invalid = -1
    Day = 0
    Month = 1
    Quarter = 2
    Year = 3


class RefreshMode(IntEnum):
    Import = 0
    Hybrid = 1


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
