from .base import SsasReadonlyRecord


class CalcDependency(SsasReadonlyRecord):
    """TBD.

    SSAS spec:
    """

    database_name: str
    object_type: str
    table: str | None = None
    object: str
    expression: str | None = None
    referenced_object_type: str
    referenced_table: str | None = None
    referenced_object: str
    referenced_expression: str | None = None

    def pbi_core_name(self) -> str:
        """Returns the name displayed in the PBIX report."""
        return f"{self.object_type}[{self.object}] -> {self.referenced_object_type}[{self.referenced_object}]"
