from enum import IntEnum


class ImpersonationMode(IntEnum):
    Default = 1
    ImpersonateAccount = 2
    ImpersonateAnonymous = 3
    ImpersonateCurrentUser = 4
    ImpersonateServiceAccount = 5
    ImpersonateUnattendedAccount = 6


class DataSourceType(IntEnum):
    Provider = 1
    Structured = 2


class Isolation(IntEnum):
    ReadCommitted = 1
    Snapshot = 2
