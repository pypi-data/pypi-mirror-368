# ruff: noqa: N815
from enum import IntEnum
from typing import TYPE_CHECKING

from ._base_node import LayoutNode

if TYPE_CHECKING:
    from .layout import Layout


class ResourcePackageItemType(IntEnum):
    JS = 0
    CSS = 1
    PNG = 3
    PBIVIZ = 5
    NA = 100
    TOPO = 200
    JSON2 = 201
    JSON = 202


class ResourcePackageItem(LayoutNode):
    _parent: "ResourcePackageDetails"  # pyright: ignore reportIncompatibleVariableOverride=false
    name: str | None = None
    path: str
    type: ResourcePackageItemType
    resourcePackageId: int | None = None
    resourcePackageItemBlobInfoId: int | None = None
    id: int | None = None


class ResourcePackageDetailsType(IntEnum):
    JS = 0
    CUSTOM_THEME = 1
    BASE_THEME = 2


class ResourcePackageDetails(LayoutNode):
    _parent: "ResourcePackage"  # pyright: ignore reportIncompatibleVariableOverride=false
    disabled: bool = False
    items: list[ResourcePackageItem] = []
    type: ResourcePackageDetailsType
    name: str
    id: int | None = None
    reportId: int | None = None


class ResourcePackage(LayoutNode):
    _parent: "Layout"  # pyright: ignore reportIncompatibleVariableOverride=false
    resourcePackage: ResourcePackageDetails
