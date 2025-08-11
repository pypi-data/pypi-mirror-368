from enum import IntEnum


class PartitionMode(IntEnum):
    """Source: [Microsoft](https://learn.microsoft.com/en-us/analysis-services/tmsl/partitions-object-tmsl?view=asallproducts-allversions)."""

    Import = 0
    DirectQuery = 1  # not verified
    Default = 2  # not verified
    Push = 3


class PartitionType(IntEnum):
    """Source: [Microsoft](https://learn.microsoft.com/en-us/analysis-services/tmsl/partitions-object-tmsl?view=asallproducts-allversions)."""

    Query = 1
    Calculated = 2
    _None = 3
    M = 4
    Entity = 5
    CalculationGroup = 7


class DataView(IntEnum):
    Full = 0
    Sample = 1
    Default = 3
