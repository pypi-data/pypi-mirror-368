from collections.abc import Callable
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal, Self, TypeVar

from pbi_core.lineage import LineageNode
from pbi_core.pydantic.main import BaseValidation

if TYPE_CHECKING:
    from pbi_core.ssas.server import BaseTabularModel

LAYOUT_ENCODING = "utf-16-le"


T = TypeVar("T", bound="LayoutNode")


class LayoutNode(BaseValidation):
    _name_field: str | None = None  # name of the field used to populate __repr__
    _parent: "LayoutNode"
    _xpath: list[str | int]

    @staticmethod
    def serialize_helper(value: Any) -> Any:
        """Helper function to serialize a value.

        We need to separate from the main function to handle cases where there is a list of
        dictionaries such as the visual container properties.
        """
        if hasattr(value, "serialize"):
            return value.serialize()
        if isinstance(value, list):
            return [LayoutNode.serialize_helper(val) for val in value]
        if isinstance(value, dict):
            return {key: LayoutNode.serialize_helper(val) for key, val in value.items()}
        if isinstance(value, Enum):
            return value.name
        return value

    def serialize(self) -> dict[str, Any]:
        """Serialize the node to a dictionary.

        Differs from the model_dump_json method in that it does not convert the JSON models back to strings.
        """
        ret = {}
        for field in self.model_fields:
            ret[field] = self.serialize_helper(getattr(self, field))
        return ret

    def pbi_core_name(self) -> str:
        raise NotImplementedError

    def find_all(
        self,
        cls_type: type[T],
        attributes: dict[str, Any] | Callable[[T], bool] | None = None,
    ) -> list["T"]:
        ret: list[T] = []
        if attributes is None:
            attribute_lambda: Callable[[T], bool] = lambda _: True  # noqa: E731
        elif isinstance(attributes, dict):
            attribute_lambda = lambda x: all(  # noqa: E731
                getattr(x, field_name) == field_value for field_name, field_value in attributes.items()
            )
        else:
            attribute_lambda = attributes
        if isinstance(self, cls_type) and attribute_lambda(self):
            ret.append(self)
        for child in self._children():
            ret.extend(child.find_all(cls_type, attributes))
        return ret

    def find(self, cls_type: type[T], attributes: dict[str, Any] | Callable[[T], bool] | None = None) -> "T":
        if attributes is None:
            attribute_lambda: Callable[[T], bool] = lambda _: True  # noqa: E731
        elif isinstance(attributes, dict):
            attribute_lambda = lambda x: all(  # noqa: E731
                getattr(x, field_name) == field_value for field_name, field_value in attributes.items()
            )
        else:
            attribute_lambda = attributes
        if isinstance(self, cls_type) and attribute_lambda(self):
            return self
        for child in self._children():
            try:
                return child.find(cls_type, attributes)
            except ValueError:
                pass
        msg = f"Object not found: {cls_type}"
        raise ValueError(msg)

    def model_dump_json(self, **kwargs: Any) -> str:
        return super().model_dump_json(round_trip=True, exclude_unset=True, **kwargs)

    def next_sibling(self) -> Self:
        raise NotImplementedError

    def prev_sibling(self) -> Self:
        raise NotImplementedError

    def _children(self) -> list["LayoutNode"]:
        ret: list[LayoutNode] = []
        for attr in dir(self):
            if attr.startswith("_"):
                continue
            child_candidate: list[Any] | dict[str, Any] | LayoutNode | int | str = getattr(self, attr)
            if isinstance(child_candidate, list):
                ret.extend(val for val in child_candidate if isinstance(val, LayoutNode))
            elif isinstance(child_candidate, dict):
                ret.extend(val for val in child_candidate.values() if isinstance(val, LayoutNode))
            elif isinstance(child_candidate, LayoutNode):
                ret.append(child_candidate)
        return ret

    def __str__(self) -> str:
        if self._name_field is not None:
            name = getattr(self, self._name_field)
            if callable(name):
                name = name()
            return f"{self.__class__.__name__}({name})"
        return super().__str__()

    def get_lineage(
        self,
        lineage_type: Literal["children", "parents"],
        tabular_model: "BaseTabularModel",
    ) -> LineageNode:
        raise NotImplementedError

    def find_xpath(self, xpath: list[str | int]) -> "LayoutNode":
        return _find_xpath(self, xpath)

    def pprint(self, indent: int = 4) -> None:
        ret = self.model_dump_json(indent=indent)
        ret = ret.replace('"', "").replace(":", "=").replace("{", "(").replace("}", ")")
        ret = self.__class__.__name__ + ret
        print(ret)


def _find_xpath(val: LayoutNode | list[LayoutNode] | dict[str, LayoutNode] | str, xpath: list[str | int]) -> LayoutNode:
    if len(xpath) == 0:
        assert isinstance(val, LayoutNode)
        return val
    if isinstance(val, list):
        next_pos = xpath.pop(0)
        assert isinstance(next_pos, int)
        return _find_xpath(val[next_pos], xpath)
    if isinstance(val, dict):
        breakpoint()
    elif isinstance(val, LayoutNode):
        next_pos = xpath.pop(0)
        assert isinstance(next_pos, str)
        return _find_xpath(getattr(val, next_pos), xpath)
    msg = f"What? xpath={xpath}, val={val}"
    raise ValueError(msg)


def _set_parents(
    base: list[LayoutNode] | dict[str, LayoutNode] | LayoutNode | int | str,
    last_parent: "LayoutNode",
    curr_xpath: list[str | int],
) -> None:
    if isinstance(base, list):
        for i, val in enumerate(base):
            _set_parents(val, last_parent, [*curr_xpath, i])
    elif isinstance(base, dict):
        for key, val in base.items():
            _set_parents(val, last_parent, [*curr_xpath, key])
    elif isinstance(base, LayoutNode):
        base._parent = last_parent
        base._xpath = curr_xpath

        for field_name in base.model_fields:
            if field_name.startswith("_"):
                continue
            field_value = getattr(base, field_name)
            if isinstance(field_value, list | dict | LayoutNode):
                _set_parents(field_value, base, [*curr_xpath, field_name])
