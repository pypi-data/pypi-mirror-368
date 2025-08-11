from pbi_core.ssas.model_tables.base import SsasReadonlyRecord


class CalcDependency(SsasReadonlyRecord):
    """Calculation Dependency.

    Represents a dependency between two DAX calculations in the model.
    This is recursive, so it connects non-direct dependencies.
    For instance, if we have three measures (A -> B -> C) there will be a dependency record between A and C.
    This entity is calculated, rather than being "real" like the other entities.


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
