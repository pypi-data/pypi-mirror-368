from enum import IntEnum


class PolicyType(IntEnum):
    BASIC = 0


class Granularity(IntEnum):
    INVALID = -1
    DAY = 0
    MONTH = 1
    QUARTER = 2
    YEAR = 3


class RefreshMode(IntEnum):
    IMPORT = 0
    HYBRID = 1
