from enum import IntEnum


class RefreshType(IntEnum):
    """From `[`Microsoft doc pages <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.refreshtype?view=analysisservices-dotnet>_."""

    """
    For all partitions in the specified partition, table, or database, refresh data and recalculate all dependents.
    For a calculation partition, recalculate the partition and all its dependents.
    """
    Full = 1
    """
    Clear values in this object and all its dependents.
    """
    ClearValues = 2
    """
    Recalculate this object and all its dependents, but only if needed.
    This value does not force recalculation, except for volatile formulas.
    """
    Calculate = 3
    """
    Refresh data in this object and clear all dependents.
    """
    DataOnly = 4
    """
    If the object needs to be refreshed and recalculated, refresh and recalculate the object and all its dependents.
    Applies if the partition is in a state other than Ready.
    """
    Automatic = 5
    """
    Append data to this partition and recalculate all dependents.
    This command is valid only for regular partitions and not for calculation partitions.
    """
    Add = 7
    """
    Defragment the data in the specified table. As data is added to or removed from a table, the dictionaries of each
    column can become polluted with values that no longer exist in the actual column values.
    The defragment option will clean up the values in the dictionaries that are no longer used.
    """
    Defragment = 8
