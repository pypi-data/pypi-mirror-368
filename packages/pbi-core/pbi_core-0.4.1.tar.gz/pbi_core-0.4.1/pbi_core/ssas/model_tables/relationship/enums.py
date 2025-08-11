from enum import IntEnum


class RelationshipType(IntEnum):
    SINGLE_COLUMN = 1


class CrossFilteringBehavior(IntEnum):
    ONE_DIRECTION = 1
    BOTH_DIRECTION = 2
    AUTOMATIC = 3


class JoinOnDateBehavior(IntEnum):
    DATE_AND_TIME = 1
    DATE_PART_ONLY = 2


class SecurityFilteringBehavior(IntEnum):
    ONE_DIRECTION = 1
    BOTH_DIRECTIONS = 2
    _NONE = 3
