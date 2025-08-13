from __future__ import annotations

import logging
import os
import pathlib
import sys

if sys.version_info >= (3, 11):
    pass
else:
    pass
import typing

from rich.logging import RichHandler

if typing.TYPE_CHECKING:
    from rich.console import Console

_logger = logging.getLogger("odoo_runbot")
# prefix for all env variable to force interactive input

RUNBOT_PREFIX = "RUNBOT_"
SET_ODOO_PREFIX = "SET_ODOO_"


class RunbotEnvironment:
    """The complete env of the runbot"""

    UNIQUE_ID: str
    """Unique string id, based on Gitlab CI_JOB_ID and CI_NODE_INDEX in case of parallel"""
    ODOO_VERSION: str
    """
    The Odoo version to test, provided by the image where the runbot run.
    """
    GITLAB_READ_API_TOKEN: str
    """
    The token used to access the Gitlab API.
    This token is taken from `CI_JOB_TOKEN` or `PERSONAL_GITLAB_TOKEN` or `GITLAB_TOKEN` environment variable.
    In GitLab CI job be sure `CI_JOB_TOKEN` have the correct right. [https://docs.gitlab.com/ee/ci/jobs/ci_job_token.html]
    """

    def __init__(
        self,
        environ: dict[str, str],
        *,
        workdir: pathlib.Path | None = None,
        config: pathlib.Path | None = None,
        verbose: bool = False,
    ) -> None:
        self.environ = environ
        self.verbose = verbose or environ.get("RUNBOT_VERBOSE", False)
        self.CI_COMMIT_REF_NAME = environ.get("CI_COMMIT_REF_NAME")
        self.CI_MERGE_REQUEST_TARGET_BRANCH_NAME = environ.get("CI_MERGE_REQUEST_TARGET_BRANCH_NAME")
        self.CI_PROJECT_NAME = environ.get("CI_PROJECT_NAME")
        self.CI_JOB_TOKEN = environ.get("CI_JOB_TOKEN")
        self.CI_DEPLOY_TOKEN = environ.get("CI_DEPLOY_TOKEN")
        self.CI_PROJECT_PATH = environ.get("CI_PROJECT_PATH")
        self.CI_API_V4_URL = environ.get("CI_API_V4_URL")
        self.CI_SERVER_URL = environ.get("CI_SERVER_URL")
        self.ODOO_VERSION = str(environ.get("ODOO_VERSION"))
        self.UNIQUE_ID = "-".join(
            [
                "job",
                environ.get("CI_JOB_ID") or environ.get("RUNBOT_RANDOM_ID", "0"),
                environ.get("CI_NODE_INDEX", "1"),
            ],
        )
        self.GITLAB_READ_API_TOKEN = (
            environ.get("GITLAB_READ_API_TOKEN") or environ.get("CI_JOB_TOKEN") or environ.get("GITLAB_TOKEN")
        )
        self.in_ci = "CI" in os.environ
        self.abs_curr_dir = pathlib.Path.cwd().absolute().resolve()
        if workdir:
            self.abs_curr_dir = workdir.resolve().absolute()

        self.runbot_config_path = None
        if config and config.exists() and config.is_file():
            self.runbot_config_path = config

        if not self.runbot_config_path and (self.abs_curr_dir / "runbot.toml").exists():
            self.runbot_config_path = self.abs_curr_dir / "runbot.toml"

        if not self.runbot_config_path and (self.abs_curr_dir / "pyproject.toml").exists():
            self.runbot_config_path = self.abs_curr_dir / "pyproject.toml"

        self.result_path = self.abs_curr_dir / "runbot_result"
        self.ODOO_RC = environ.get("ODOO_RC", str(self.abs_curr_dir / "odoo-config.ini"))
        self.environ["DATABASE"] = "_".join(["runbot_db", self.UNIQUE_ID.replace("-", "_")])
        self.environ["DB_NAME"] = self.environ["DATABASE"]

    def chdir(self, new_dir: pathlib.Path | None) -> None:
        if new_dir:
            os.chdir(new_dir)
            self.__dict__.pop("project_config", None)

    @property
    def CI_PROJECT_DIR(self) -> pathlib.Path:  # noqa: N802
        """Returns: The CI_PROJECT_DIR provide by Gitlab CI as a [pathlib.Path][] object."""
        return pathlib.Path(os.environ["CI_PROJECT_DIR"])

    def setup_logging_for_runbot(self, console: Console) -> None:
        level = logging.DEBUG if self.verbose else logging.INFO
        rich_handler = RichHandler(
            level, console=console, rich_tracebacks=True, enable_link_path=not self.environ.get("CI", False)
        )
        rich_handler.addFilter(logging.Filter("odoo_runbot"))
        _logger = logging.getLogger("odoo_runbot")
        _logger.addHandler(rich_handler)
        _logger.setLevel(level)

    def check_ok(self) -> bool:
        res = True
        if not self.runbot_config_path:
            _logger.error("Config file not found in %s. Tried [runbot.toml, pyproject.toml]", self.abs_curr_dir)
            res = False
        elif not self.runbot_config_path.exists() or not self.runbot_config_path.is_file():
            _logger.error("Config file %s don't exist", self.runbot_config_path)
            res = False
        try:
            from odoo import release  # noqa: PLC0415

            if release.version < "12.0":
                _logger.error("This runbot can't run the test from Odoo less than 12.0")
                res = False
        except ImportError:
            pass

        return res

    def print_info(self) -> None:
        _logger.info("Run in %s", str(self.abs_curr_dir))
        _logger.info("With Toml config %s", str(self.runbot_config_path))
        _logger.info("Test result in %s", str(self.result_path))
        if os.getenv("ODOO_DEPENDS"):
            _logger.error("Il ne faut plus utiliser `ODOO_DEPENDS` ni même la renseigner dans le runbot.")
            _logger.error("Il faut au lieu utiliser les variables `ADDONS_GIT_XXX` supportée par `addons-installer`")
        _logger.info("Odoo version: %s", self.ODOO_VERSION)
        _logger.info("Odoo config file: %s", self.ODOO_RC)
