from .base import BaseVisual, PropertyDef


class GenericVisual(BaseVisual):
    """A generic visual representation."""

    objects: dict[str, list[PropertyDef]] | None = None
