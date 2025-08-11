import pydantic
from bs4 import BeautifulSoup
from structlog import get_logger

from pbi_core.ssas.server._commands import BaseCommands, ModelCommands, NoCommands, RefreshCommands, RenameCommands

from .base_ssas_table import SsasTable
from .enums import RefreshType

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

    _commands: BaseCommands

    def alter(self) -> BeautifulSoup:
        """Updates a non-name field of an object."""
        xml_command = self.render_xml_command(
            self.xml_fields(),
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
    _commands: RenameCommands

    def rename(self) -> BeautifulSoup:
        """Updates a name field of an object."""
        xml_command = self.render_xml_command(
            self.xml_fields(),
            self._commands.rename,
            self.tabular_model.db_name,
        )
        logger.info("Syncing Rename Changes to SSAS", obj=self._db_type_name())
        return self.query_xml(xml_command, db_name=self.tabular_model.db_name)


class SsasCreate(SsasTable):
    """Class for SSAS records that implement create functionality.

    The `create <https://learn.microsoft.com/en-us/analysis-services/tmsl/create-command-tmsl?view=asallproducts-allversions>`_ spec
    """  # noqa: E501

    _commands: BaseCommands

    def create(self) -> BeautifulSoup:
        """Creates a new SSAS object based on the python object."""
        xml_command = self.render_xml_command(
            self.xml_fields(),
            self._commands.create,
            self.tabular_model.db_name,
        )
        logger.info("Syncing Create Changes to SSAS", obj=self._db_type_name())
        return self.tabular_model.server.query_xml(xml_command, db_name=self.tabular_model.db_name)


class SsasDelete(SsasTable):
    """Class for SSAS records that implement delete functionality.

    The `delete <https://learn.microsoft.com/en-us/analysis-services/tmsl/delete-command-tmsl?view=asallproducts-allversions>`_ spec
    """  # noqa: E501

    _db_id_field: str = "id"  # we're comparing the name before the translation back to SSAS casing
    _commands: BaseCommands

    def delete(self) -> BeautifulSoup:
        data = {
            self._db_id_field: getattr(self, self._db_id_field),
        }
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
    _commands: RefreshCommands

    def refresh(self, refresh_type: RefreshType | None = None) -> BeautifulSoup:
        xml_command = self.render_xml_command(
            self.xml_fields(),
            self._commands.refresh,
            self.tabular_model.db_name,
        )
        logger.info("Syncing Refresh Changes to SSAS", obj=self)
        return self.query_xml(xml_command, db_name=self.tabular_model.db_name)


class SsasReadonlyRecord(SsasTable):
    """Class for SSAS records that implement no command."""

    _commands: NoCommands


class SsasEditableRecord(SsasCreate, SsasAlter, SsasDelete):
    _commands: BaseCommands


class SsasRenameRecord(SsasCreate, SsasAlter, SsasDelete, SsasRename):
    _commands: RenameCommands  # pyright: ignore reportIncompatibleVariableOverride


class SsasRefreshRecord(SsasCreate, SsasAlter, SsasDelete, SsasRename, SsasRefresh):
    _commands: RefreshCommands  # pyright: ignore reportIncompatibleVariableOverride


class SsasModelRecord(SsasAlter, SsasRefresh, SsasRename):
    """Solely used for the single Model record."""

    _commands: ModelCommands  # pyright: ignore reportIncompatibleVariableOverride
