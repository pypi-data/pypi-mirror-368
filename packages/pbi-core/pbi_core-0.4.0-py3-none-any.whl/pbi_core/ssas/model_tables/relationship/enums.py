from enum import IntEnum


class RelationshipType(IntEnum):
    SingleColumn = 1


class CrossFilteringBehavior(IntEnum):
    OneDirection = 1
    BothDirection = 2
    Automatic = 3


class JoinOnDateBehavior(IntEnum):
    DateAndTime = 1
    DatePartOnly = 2


class SecurityFilteringBehavior(IntEnum):
    OneDirection = 1
    BothDirections = 2
    _None = 3
