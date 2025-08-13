from __future__ import annotations

import dataclasses
import enum
import importlib
import logging
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
import typing

if typing.TYPE_CHECKING:
    import pathlib

_logger = logging.getLogger("odoo_runbot")

RUNBOT_PREFIX = "RUNBOT_"
SET_ODOO_PREFIX = "SET_ODOO_"


def _apply_default_if_none(data_class: object) -> None:
    if not dataclasses.is_dataclass(data_class):
        err = f"Only valid call for dataclasses {type(data_class)}"
        raise ValueError(err)
    # Loop through the fields
    for field in dataclasses.fields(data_class):
        # If there is a default and the value of the field is none we can assign a value
        if not isinstance(field.default, type(dataclasses.MISSING)) and getattr(data_class, field.name) is None:
            setattr(data_class, field.name, field.default)
        if not isinstance(field.default_factory, type(dataclasses.MISSING)) and getattr(data_class, field.name) is None:
            setattr(data_class, field.name, field.default_factory())


@dataclasses.dataclass()
class RunbotExcludeWarning:
    """Container for a regex to exclude in the log
    Attributes:
        name (str): A name for this regex.
            Allow to print if this regex found a warning to exclude
        level (str) : The level of the logger expected. WARNING by default
        min_match (int): Min occurrence of this warning in the log. The runbot should failed otherwaise
        max_match (int): Max occurrence of this warning in the log. The runbot should failed otherwaise
        regex (str): A regular expression to exclude
    """

    name: str
    regex: str
    logger: str = dataclasses.field(default="")
    level: str = dataclasses.field(default=logging.getLevelName(logging.WARNING))
    min_match: int = dataclasses.field(default=1)
    max_match: int = dataclasses.field(default=1)

    def __post_init__(self) -> None:
        _apply_default_if_none(self)
        self.max_match = min(max(self.max_match, self.min_match), 100) if self.max_match > 0 else 0
        self.min_match = max(min(self.min_match, self.max_match), 0) if self.max_match > 0 else 0


@dataclasses.dataclass()
class RunbotPyWarningsFilter:
    """Dataclass storing wich py.warnings to filter"""

    name: str
    action: str
    message: str | None = dataclasses.field(default=None)
    category: str | None = dataclasses.field(default=None)

    def __post_init__(self) -> None:
        _apply_default_if_none(self)


class StepAction(enum.Enum):
    TESTS = "tests"
    INSTALL = "install"


@dataclasses.dataclass()
class RunbotStepConfig:
    """Contain the config for one warmup"""

    name: str
    modules: list[str]
    action: StepAction = dataclasses.field(default=StepAction.TESTS)
    test_tags: list[str] = dataclasses.field(default_factory=list)
    coverage: bool = dataclasses.field(default=True)
    log_filters: list[RunbotExcludeWarning] = dataclasses.field(default_factory=list)
    allow_warnings: bool = dataclasses.field(default=True)

    def __post_init__(self) -> None:
        _apply_default_if_none(self)


@dataclasses.dataclass()
class RunbotToolConfig:
    """The class containing all the config to run the tests.
    The data are read from the `pyproject.toml` and focus on the `tool.mangono.runbot` section
    """

    include_current_project: bool = dataclasses.field(default=True)
    steps: list[RunbotStepConfig] = dataclasses.field(default_factory=list)
    """The config for the test phase (after warmup)"""
    pretty: bool = dataclasses.field(default=True)
    """Use color and pretty printing in log"""
    warning_filters: list[RunbotPyWarningsFilter] = dataclasses.field(default_factory=list)
    """"""
    failfast: bool = dataclasses.field(default=True)

    def __post_init__(self) -> None:
        _apply_default_if_none(self)

    def get_step(self, step_name: str) -> RunbotStepConfig:
        for step in self.steps:
            if step.name == step_name:
                return step
        msg = f"No such step: {step_name}"
        raise KeyError(msg)

    @classmethod
    def load_from_file(cls, path: pathlib.Path) -> RunbotToolConfig:
        """Create a config from a TOML file path using tomllib or toml depending of the python version.

        Args:
            path:

        Returns:

        """
        with path.open(mode="rb") as pyproject_toml:
            data = tomllib.load(pyproject_toml)

        if path.name == "pyproject.toml":
            return cls.load_from_toml_data(data.get("tool", {}).get("runbot", {}), config_file=path)
        return cls.load_from_toml_data(data, config_file=path)

    @classmethod
    def load_from_toml_data(cls, runbot_data: dict, config_file: pathlib.Path) -> RunbotToolConfig:
        """Convert the Toml data to a RunbotToolConfig object.

        Args:
            runbot_data: All the data for the sub kley of `runbot.tool`

        Returns: A `RunbotToolConfig` object

        """
        if not runbot_data:
            msg = "No runbot information found in %s", str(config_file)
            raise ValueError(msg)
        base_path = config_file.parent
        version_log_filter = log_filter_by_odoo_version()
        global_log_filter = cls._get_log_filters(version_log_filter, runbot_data)
        global_pywarnings = warning_filter_by_odoo_version() + [
            RunbotPyWarningsFilter(
                name=py_filter_data.get("name", f"Global PyWarnings Filter {_idx}"),
                action=py_filter_data.get("action"),
                message=py_filter_data.get("message"),
                category=py_filter_data.get("category"),
            )
            for _idx, py_filter_data in enumerate(runbot_data.get("pywarnings-filter", []))
        ]
        default_modules = []
        if runbot_data.get("modules") or runbot_data.get("modules-files"):
            default_modules = cls.find_modules(runbot_data, base_path=base_path)

        cls._inject_default_step(runbot_data)

        steps = []
        for _idx_step, (step_name, step_data) in enumerate(runbot_data.get("step").items()):
            log_filter = cls._get_log_filters(global_log_filter, step_data, step_name=step_name)
            action = cls._get_action(step_name, step_data)
            modules = cls.find_modules(step_data, base_path=base_path)
            if not modules:
                modules = default_modules
            modules.sort()
            step_obj = RunbotStepConfig(
                name=step_name,
                allow_warnings=step_data.get("allow-warnings", runbot_data.get("allow-warnings")),
                coverage=action == StepAction.TESTS and step_data.get("coverage", runbot_data.get("coverage")),
                modules=modules,
                action=action,
                test_tags=step_data.get("test-tags"),
                log_filters=log_filter,
            )
            steps.append(step_obj)

        return cls(
            include_current_project=runbot_data.get("include-current-project"),
            pretty=True,
            failfast=runbot_data.get("failfast"),
            steps=steps,
            warning_filters=global_pywarnings,
        )

    @staticmethod
    def find_modules(data: dict[str, typing.Any], *, base_path: pathlib.Path) -> list[str]:
        modules = data.get("modules", [])
        modules_files = data.get("modules-files", [])
        result_modules = set()
        if modules:
            return modules
        for modules_file in modules_files:
            ppath = base_path / modules_file
            if ppath.exists() and ppath.is_file():
                with ppath.open("r") as mfile:
                    result_modules.update(
                        {
                            mod_name.strip()
                            for mod_name in mfile.readlines()
                            if mod_name and not mod_name.startswith("#")
                        }
                    )
            else:
                _logger.error("File [%s] not found", ppath)

        return list(result_modules)

    @classmethod
    def _inject_default_step(cls, runbot_data: dict[str, typing.Any]) -> None:
        if not runbot_data.get("step"):
            runbot_data["step"] = {
                "default": {
                    "coverage": runbot_data.get("coverage"),
                    "unittest-output": runbot_data.get("unittest-output"),
                    "modules": runbot_data.get("modules"),
                    "action": StepAction.TESTS.name,
                    "test-tags": [],
                    "log-filters": [],
                }
            }

    @classmethod
    def _get_log_filters(
        cls,
        global_log_filter: list[RunbotExcludeWarning],
        step_data: dict[str, typing.Any],
        step_name: str | None = None,
    ) -> list[RunbotExcludeWarning]:
        log_filter = (global_log_filter and global_log_filter[:]) or []
        for _idx_log_filter, data in enumerate(step_data.get("log-filters", []), start=len(log_filter) + 1):
            default_name = f"All Steps - Logger Filter {_idx_log_filter}"
            if step_name:
                default_name = f"Step {step_name} - Logger Filter {_idx_log_filter}"
            _data = data
            if isinstance(data, str):
                _data = {"regex": data}
            log_filter.append(
                RunbotExcludeWarning(
                    name=_data.get("name", default_name),
                    regex=_data["regex"],
                    logger=_data.get("logger"),
                    min_match=_data.get("min-match"),
                    max_match=_data.get("max-match"),
                ),
            )
        return log_filter

    @staticmethod
    def _get_action(step_name: str, step_data: dict[str, typing.Any]) -> StepAction:
        config_value = step_data.get("action", step_name)
        if config_value in ("install", "warmup"):
            return StepAction.INSTALL
        return StepAction.TESTS


def log_filter_by_odoo_version() -> list[RunbotExcludeWarning]:
    """Returns a list of `RunbotExcludeWarning` objects predefined by odoo version
    This list avoid duplication accross project to filter odoo log warning.

    Returns: The list of `RunbotExcludeWarning` objects for the current odoo version or an empty list

    """
    if importlib.util.find_spec("odoo"):
        return [
            RunbotExcludeWarning(
                name="Default - unaccent not loadable",
                logger="odoo.modules.registry",
                regex=r".*no unaccent\(\) function was found in database.*",
                min_match=0,
                max_match=99,
            ),
        ]

    return []


def warning_filter_by_odoo_version() -> list[RunbotPyWarningsFilter]:
    """Returns a list of `RunbotPyWarningsFilter` objects predefined by odoo version
    This list avoid duplication accross project to filter odoo log warning.

    Returns: The list of `RunbotPyWarningsFilter` objects for the current odoo version or an empty list

    """
    if importlib.util.find_spec("odoo"):
        return [
            RunbotPyWarningsFilter(
                name="[Default] Exclude error in reportlab/pdfbase",
                action="ignore",
                category=SyntaxWarning.__name__,
                message='.*"is" with a literal. Did you mean.*',
            ),
            RunbotPyWarningsFilter(
                name="[Default] Exclude error in vobject/base.py",
                action="ignore",
                category=SyntaxWarning.__name__,
                message=".*invalid escape sequence*",
            ),
        ]

    return []
