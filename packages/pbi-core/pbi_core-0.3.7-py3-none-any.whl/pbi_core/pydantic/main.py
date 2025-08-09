from pydantic import BaseModel, ConfigDict


class BaseValidation(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        use_enum_values=False,
        json_schema_mode_override="serialization",
        validate_assignment=True,
        protected_namespaces=(),
    )

    def __format__(self, format_spec: str) -> str:
        return f"{self!s:{format_spec}}"
