from enum import Enum, IntEnum


class DataState(IntEnum):
    """Source: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/93d1844f-a6c7-4dda-879b-2e26ed5cd297)."""

    Ready = 1
    NoData = 3
    CalculationNeeded = 4
    SemanticError = 5
    EvaluationError = 6
    DependencyError = 7
    Incomplete = 8
    SyntaxError = 9


class ObjectType(IntEnum):
    """Source: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/7a16a837-cb88-4cb2-a766-a97c4d0e1f43)."""

    MODEL = 1
    DATASOURCE = 2
    TABLE = 3
    COLUMN = 4
    ATTRIBUTE_HIERARCHY = 5
    PARTITION = 6
    RELATIONSHIP = 7
    MEASURE = 8
    HIERARCHY = 9
    LEVEL = 10
    KPI = 12
    CULTURE = 13
    LINGUISTIC_METADATA = 15
    PERSPECTIVE = 29
    PERSPECTIVE_TABLE = 30
    PERSPECTIVE_COLUMN = 31
    PERSPECTIVE_HIERARCHY = 32
    PERSPECTIVE_MEASURE = 33
    ROLE = 34
    ROLE_MEMBERSHIP = 35
    TABLE_PERMISSION = 36
    VARIATION = 37
    EXPRESSION = 41
    COLUMN_PERMISSION = 42
    CALCULATION_GROUP = 46
    CALCULATION_ITEM = 47
    QUERY_GROUP = 51


class DataType(IntEnum):
    """Source: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/00a9ec7a-5f4d-4517-8091-b370fe2dc18b)."""

    Automatic = 1
    String = 2
    Int64 = 6
    Double = 8
    DateTime = 9
    Decimal = 10
    Boolean = 11
    Binary = 17
    Unknown = 19
    Unknowner = 20


class DataCategory(Enum):
    """Source: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/6360ac84-0717-4170-bce0-284cbef419ca).

    Note:
        Only used for table, the Column and Measure DataCategories are just strings

    """

    Unknown = 0
    Regular = 1
    Time = 2
    Geography = 3
    Organization = 4
    BillOfMaterials = 5
    Accounts = 6
    Customers = 7
    Products = 8
    Scenario = 9
    Quantitative = 10
    Utility = 11
    Currency = 12
    Rates = 13
    Channel = 14
    Promotion = 15
    TimeStr = "Time"  # TODO: I think we're accidentally merging two enums. sometimes it's a string in the pbix??
