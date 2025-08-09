# ruff: noqa: N815


from .base import BaseVisual


class ColumnProperty(BaseVisual):
    displayName: str | None = None
