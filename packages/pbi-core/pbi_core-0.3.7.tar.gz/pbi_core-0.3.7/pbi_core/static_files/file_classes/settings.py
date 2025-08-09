from ._base import BaseFileModel

base_val = bool | int | str


class Settings(BaseFileModel):
    Version: int
    ReportSettings: dict[str, base_val]
    QueriesSettings: dict[str, base_val]
