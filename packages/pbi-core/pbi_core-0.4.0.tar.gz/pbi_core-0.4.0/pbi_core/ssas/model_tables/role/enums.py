from enum import IntEnum


class ModelPermission(IntEnum):
    _None = 1
    Read = 2
    ReadRefresh = 3
    Refresh = 4
    Administrator = 5
