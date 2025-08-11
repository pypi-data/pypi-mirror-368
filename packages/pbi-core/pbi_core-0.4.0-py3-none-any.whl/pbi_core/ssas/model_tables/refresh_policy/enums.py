from enum import IntEnum


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
