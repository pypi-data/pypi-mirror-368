from typing import TYPE_CHECKING, Any

import pydantic
from bs4 import BeautifulSoup
from pbi_core.ssas.server._commands import BaseCommands, ModelCommands, NoCommands, RefreshCommands, RenameCommands
from pbi_core.ssas.server.utils import OBJECT_COMMAND_TEMPLATES
from structlog import get_logger

from .base_ssas_table import SsasTable
from .enums import RefreshType

if TYPE_CHECKING:
    from pbi_core.ssas.server.tabular_model import BaseTabularModel

logger = get_logger()


SsasConfig = pydantic.ConfigDict(
    arbitrary_types_allowed=True,
    extra="forbid",
    use_enum_values=False,
    json_schema_mode_override="serialization",
    validate_assignment=True,
    protected_namespaces=(),
)


logger = get_logger()


class SsasAlter(SsasTable):
    """Class for SSAS records that implement alter functionality.

    The `alter <https://learn.microsoft.com/en-us/analysis-services/tmsl/alter-command-tmsl?view=asallproducts-allversions>`_ spec
    """  # noqa: E501

    _commands: BaseCommands  # pyright: ignore reportIncompatibleVariableOverride

    def alter(self) -> BeautifulSoup:
        """Updates a non-name field of an object."""
        data = {
            self._db_field_names.get(k, k): v for k, v in self.model_dump().items() if k not in self._read_only_fields
        }
        xml_command = self.render_xml_command(
            data,
            self._commands.alter,
            self.tabular_model.db_name,
        )
        logger.info("Syncing Alter Changes to SSAS", obj=self._db_type_name())
        return self.query_xml(xml_command, db_name=self.tabular_model.db_name)


class SsasRename(SsasTable):
    """Class for SSAS records that implement rename functionality.

    The `rename <https://learn.microsoft.com/en-us/analysis-services/tmsl/rename-command-tmsl?view=asallproducts-allversions>`_ spec
    """  # noqa: E501

    _db_name_field: str = "not_defined"
    _commands: RenameCommands  # pyright: ignore reportIncompatibleVariableOverride

    def rename(self) -> BeautifulSoup:
        """Updates a name field of an object."""
        data = {
            self._db_field_names.get(k, k): v for k, v in self.model_dump().items() if k not in self._read_only_fields
        }
        xml_command = self.render_xml_command(
            data,
            self._commands.rename,
            self.tabular_model.db_name,
        )
        logger.info("Syncing Rename Changes to SSAS", obj=self._db_type_name())
        return self.query_xml(xml_command, db_name=self.tabular_model.db_name)


class SsasCreate(SsasTable):
    """Class for SSAS records that implement create functionality.

    The `create <https://learn.microsoft.com/en-us/analysis-services/tmsl/create-command-tmsl?view=asallproducts-allversions>`_ spec
    """  # noqa: E501

    @classmethod
    def create(cls: type["SsasCreate"], tabular_model: "BaseTabularModel", **kwargs: dict[str, Any]) -> BeautifulSoup:
        # data = {
        #     cls._db_field_names.get(k, k): v for k, v in kwargs.items() if k not in cls._read_only_fields
        # }
        # xml_command = cls.render_xml_command(
        #     data,
        #     cls._commands.rename,
        #     tabular_model.db_name,
        # )
        # logger.info("Syncing Rename Changes to SSAS", obj=cls._db_type_name())
        # tabular_model.server.query_xml(xml_command, db_name=tabular_model.db_name)
        raise NotImplementedError


class SsasDelete(SsasTable):
    """Class for SSAS records that implement delete functionality.

    The `delete <https://learn.microsoft.com/en-us/analysis-services/tmsl/delete-command-tmsl?view=asallproducts-allversions>`_ spec
    """  # noqa: E501

    _db_id_field: str = "id"  # we're comparing the name before the translation back to SSAS casing
    _commands: BaseCommands  # pyright: ignore reportIncompatibleVariableOverride

    def delete(self) -> BeautifulSoup:
        data = {self._db_field_names.get(k, k): v for k, v in self.model_dump().items() if k == self._db_id_field}
        xml_command = self.render_xml_command(
            data,
            self._commands.delete,
            self.tabular_model.db_name,
        )
        logger.info("Syncing Delete Changes to SSAS", obj=self._db_type_name())
        return self.query_xml(xml_command, db_name=self.tabular_model.db_name)


class SsasRefresh(SsasTable):
    """Class for SSAS records that implement refresh functionality.

    The `refresh <https://learn.microsoft.com/en-us/analysis-services/tmsl/refresh-command-tmsl?view=asallproducts-allversions>`_ spec
    """  # noqa: E501

    _db_id_field: str = "id"  # we're comparing the name before the translation back to SSAS casing
    _default_refresh_type: RefreshType
    _commands: RefreshCommands  # pyright: ignore reportIncompatibleVariableOverride

    def refresh(self, refresh_type: RefreshType | None = None) -> BeautifulSoup:
        data = {self._db_field_names.get(k, k): v for k, v in self.model_dump().items() if k == self._db_id_field}
        data["RefreshType"] = refresh_type or self._default_refresh_type
        xml_command = self.render_xml_command(
            data,
            self._commands.refresh,
            self.tabular_model.db_name,
        )
        logger.info("Syncing Refresh Changes to SSAS", obj=self)
        return self.query_xml(xml_command, db_name=self.tabular_model.db_name)


class SsasReadonlyRecord(SsasTable):
    """Class for SSAS records that implement no command."""

    _commands: NoCommands  # pyright: ignore reportIncompatibleVariableOverride


class SsasEditableRecord(SsasCreate, SsasAlter, SsasDelete):
    _commands: BaseCommands

    def model_post_init(self, __context: Any, /) -> None:
        templates = OBJECT_COMMAND_TEMPLATES.get(self._db_command_obj_name(), {})
        self._commands = BaseCommands(  # pyright: ignore reportIncompatibleVariableOverride
            alter=templates["alter.xml"],
            create=templates["create.xml"],
            delete=templates["delete.xml"],
        )


class SsasRenameRecord(SsasCreate, SsasAlter, SsasDelete, SsasRename):
    _commands: RenameCommands

    def model_post_init(self, __context: Any, /) -> None:
        templates = OBJECT_COMMAND_TEMPLATES.get(self._db_command_obj_name(), {})
        if self._db_command_obj_name() == "ExtendedPropertys":
            breakpoint()
        self._commands = RenameCommands(  # pyright: ignore reportIncompatibleVariableOverride
            alter=templates["alter.xml"],
            create=templates["create.xml"],
            delete=templates["delete.xml"],
            rename=templates["rename.xml"],
        )


class SsasRefreshRecord(SsasCreate, SsasAlter, SsasDelete, SsasRename, SsasRefresh):
    _commands: RefreshCommands

    def model_post_init(self, __context: Any, /) -> None:
        templates = OBJECT_COMMAND_TEMPLATES.get(self._db_command_obj_name(), {})

        self._commands = RefreshCommands(  # pyright: ignore reportIncompatibleVariableOverride
            alter=templates["alter.xml"],
            create=templates["create.xml"],
            delete=templates["delete.xml"],
            rename=templates["rename.xml"],
            refresh=templates["refresh.xml"],
        )


class SsasModelRecord(SsasAlter, SsasRefresh, SsasRename):
    """Solely used for the single Model record."""

    _commands: ModelCommands  # type: ignore[assignment]

    def model_post_init(self, __context: Any, /) -> None:
        templates = OBJECT_COMMAND_TEMPLATES.get(self._db_command_obj_name(), {})

        self._commands = ModelCommands(  # pyright: ignore reportIncompatibleVariableOverride
            alter=templates["alter.xml"],
            refresh=templates["refresh.xml"],
            rename=templates["rename.xml"],
        )
