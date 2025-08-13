from __future__ import annotations

import builtins
import contextlib
import logging
import typing
import warnings

import coverage
from odoo_env_config import api, entry

from . import _odoo_internal, runbot_run_logging, runbot_run_test
from .runbot_config import RunbotPyWarningsFilter, StepAction

if typing.TYPE_CHECKING:
    from pathlib import Path
    from warnings import WarningMessage

    from .runbot_env import RunbotEnvironment, RunbotStepConfig

_logger = logging.getLogger("odoo_runbot")

__all__ = ["StepRunner"]


class StepRunner:
    """The main logique to execiute a runbot step-by-step. See `run`"""

    def __init__(self, env: RunbotEnvironment) -> None:
        self.env = env
        self.has_run: bool = False

    def get_server_args_from_step(self, step: RunbotStepConfig) -> list[str]:
        update_install = entry.env_to_section(entry.UpdateInstallSection)
        misc = entry.env_to_section(entry.MiscSection)
        http_sec = entry.env_to_section(entry.HttpOdooConfigSection)
        test_sec = entry.env_to_section(entry.TestOdooConfigSection)
        update_install.install = step.modules
        misc.stop_after_init = True
        http_sec.interface = "127.0.0.1"
        http_sec.enable = True
        test_sec.enable = step.action == StepAction.TESTS
        if test_sec.enable and step.test_tags:
            test_sec.test_tags = ",".join(step.test_tags)
        values_update = {}
        values_update.update(test_sec.to_values())
        values_update.update(update_install.to_values())
        values_update.update(misc.to_values())
        values_update.update(http_sec.to_values())
        return api.dict_to_odoo_args(values_update)

    def setup_odoo(self) -> None:
        _odoo_internal.setup_odoo()

    def execute(self, step: RunbotStepConfig) -> int:
        """The module to install before runnning the test.
        This modules can be a `CSV` value to install multiple value.
        Usage:
            module_name="account,my_project_config"
        Warning: When this variable is used, the test are disabled, so all the test with tag `+post_install` are not run
        """
        _logger.info("Run step %s(action=%s)", step.name, str(step.action.value))
        self.has_run = True
        if step.action == StepAction.INSTALL:
            return self._do_execute_action_install(step)
        if step.action == StepAction.TESTS:
            return self._do_execute_action_tests(step)
        _logger.error("Unknown action: %s", step.action)
        return 404

    def _do_execute_action_install(self, step: RunbotStepConfig) -> int:
        """The module to install before runnning the test.
        This modules can be a `CSV` value to install multiple value.
        Usage:
            module_name="account,my_project_config"
        Warning: When this variable is used, the test are disabled, so all the test with tag `+post_install` are not run
        """
        _odoo_internal.parse_config(self.get_server_args_from_step(step))
        output_dir = self.env.result_path / "x_unittest"
        with runbot_run_logging.start_warning_log_watcher(step) as log_filters_extractor:  # noqa: SIM117
            with warnings.catch_warnings(record=True) as warnings_list:
                rc = _odoo_internal.run_odoo_and_stop()
                _logger.info("Odoo Done rc=%s", rc)
        log_filters = log_filters_extractor()
        return abs(rc) + self._execute_to_filters(step, log_filters, warnings_list, output_dir=output_dir)

    def _do_execute_action_tests(self, step: RunbotStepConfig) -> int:
        """Run a step and activate all the test feat:
        - coverage
        - Logger matching
        - Xunit report with [xmlrunner](https://unittest-xml-reporting.readthedocs.io/en/latest/)

        Args:
            step: The step to run, containing log filter and warning filter

        Returns: The result code > 1 mean error

        """

        coverage_watcher = self.get_coverage()
        if not step.coverage:
            coverage_watcher = DummyCoverage(coverage_watcher)

        _logger.info("Setup Odoo ...")
        _odoo_internal.parse_config(self.get_server_args_from_step(step))

        logging.getLogger("odoo.tests.stats").setLevel(logging.DEBUG)
        output_dir = self.env.result_path / "x_unittest"
        with runbot_run_logging.start_warning_log_watcher(step) as log_filters_extractor:  # noqa: SIM117
            with _odoo_internal.patch_odoo_test_suite(output_dir, coverage_watcher):
                with warnings.catch_warnings(record=True) as warnings_list:
                    rc = _odoo_internal.run_odoo_and_stop()
                    _logger.info("Odoo Done rc=%s", rc)
        log_filters = log_filters_extractor()
        if not abs(rc) and step.coverage:
            _logger.info("Save Coverage recording in [%s] ...", coverage_watcher.config.data_file)
        coverage_watcher.report()
        return abs(rc) + self._execute_to_filters(step, log_filters, warnings_list, output_dir=output_dir)

    def get_coverage(self) -> coverage.Coverage:
        debug = None
        if self.env.verbose:
            debug = ["config"]
        return coverage.Coverage(
            debug=debug,
            config_file=str(self.env.abs_curr_dir.joinpath("pyproject.toml")),
            omit=["**/__manifest__.py", "**/__init__.py", "/odoo/odoo-src/**"],
            data_file=self.env.result_path / ".coverage",
        )

    def _execute_to_filters(
        self,
        step: RunbotStepConfig,
        log_filters: list[runbot_run_logging.ExcludeWarningFilter],
        warnings_list: list[WarningMessage],
        output_dir: Path,
    ) -> int:
        if log_filters or warnings_list:
            _logger.info("Test Logger and py.warnings...")
            res = runbot_run_test.execute_test_after_odoo(
                step.name,
                log_filters,
                warnings_list if not step.allow_warnings else [],
                test_runner=runbot_run_test.get_test_runner(output_dir),
            )
            rc = int(not res.wasSuccessful())
            _logger.info("Test logger rc=%s", rc)
            return rc
        return 0

    def setup_warning_filter(self, warning_filters: list[RunbotPyWarningsFilter]) -> None:
        for waring_filer in warning_filters:
            warnings.filterwarnings(
                action=waring_filer.action,
                category=getattr(builtins, waring_filer.category, Warning),
                message=waring_filer.message,
            )


class DummyCoverage:
    def __init__(self, origin: coverage.Coverage) -> None:
        self.origin = origin
        _logger.info("Disable coverage reporting")

    def __getattr__(self, item: str) -> typing.Any:  # noqa: ANN401
        return getattr(self.origin, item)

    @contextlib.contextmanager
    def collect(self) -> None:
        yield

    def report(self) -> None:
        pass
