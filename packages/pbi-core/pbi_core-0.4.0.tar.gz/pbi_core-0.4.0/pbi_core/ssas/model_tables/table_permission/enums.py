from enum import IntEnum


class MetadataPermission(IntEnum):
    """Source: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/ac2ceeb3-a54e-4bf5-85b0-a770d4b1716e)."""

    Default = 0
    _None = 1
    Read = 2
