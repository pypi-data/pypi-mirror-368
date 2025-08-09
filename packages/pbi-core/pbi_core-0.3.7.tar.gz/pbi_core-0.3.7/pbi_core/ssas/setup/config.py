from pathlib import Path
from typing import Any

import jinja2

from pbi_core.logging import get_logger
from pbi_core.pydantic import BaseValidation

logger = get_logger()

PACKAGE_DIR = Path(__file__).parents[2]
assert PACKAGE_DIR.name == "pbi_core"


class PbiCoreStartupConfig(BaseValidation):
    cert_dir: Path
    msmdsrv_ini: Path
    msmdsrv_exe: Path
    workspace_dir: Path

    def model_post_init(self, __context: Any, /) -> None:
        if not self.cert_dir.is_absolute():
            self.cert_dir = PACKAGE_DIR / self.cert_dir
        if not self.msmdsrv_ini.is_absolute():
            self.msmdsrv_ini = PACKAGE_DIR / self.msmdsrv_ini
        if not self.msmdsrv_exe.is_absolute():
            self.msmdsrv_exe = PACKAGE_DIR / self.msmdsrv_exe
        if not self.workspace_dir.is_absolute():
            self.workspace_dir = PACKAGE_DIR / self.workspace_dir

    def msmdsrv_ini_template(self) -> jinja2.Template:
        return jinja2.Template(self.msmdsrv_ini.read_text())


def get_startup_config() -> PbiCoreStartupConfig:
    try:
        with (PACKAGE_DIR / "local" / "settings.json").open("r") as f:
            return PbiCoreStartupConfig.model_validate_json(f.read())
    except FileNotFoundError as e:
        msg = 'Please run "python -m pbi_core setup" to initialize dependencies'
        raise FileNotFoundError(msg) from e
