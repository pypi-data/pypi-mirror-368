from __future__ import annotations

import contextlib
import logging
import typing
import unittest

if typing.TYPE_CHECKING:
    import pathlib

    import coverage

from unittest.mock import patch

from xmlrunner import XMLTestRunner
from xmlrunner.result import _TestInfo, _XMLTestResult

_logger = logging.getLogger("odoo_runbot.odoo_internal")
try:
    import odoo
    import odoo.cli
    import odoo.tests
except ModuleNotFoundError:
    from unittest import mock

    odoo = mock.MagicMock()

__all__ = ["odoo", "patch_odoo_test_suite", "run_odoo_and_stop", "setup_odoo"]


class _RunProto(typing.Protocol):
    def run(self, result): ...


class _UpdateProto(typing.Protocol):
    def update(self, other): ...


class _XmlTestInfo(_TestInfo):
    def shortDescription(self):  # noqa: N802
        """
        Taken from unittest.TestCase.shortDescription
        Returns a one-line description of the test, or None if no
        description has been provided.

        The default implementation of this method returns the first line of
        the specified test method's docstring.
        """
        return self.doc.strip().split("\n")[0].strip() if self.doc else None


class OdooXmlTestResult(_XMLTestResult):
    def __init__(self, *args: list, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs, infoclass=_XmlTestInfo)


@contextlib.contextmanager
def patch_odoo_test_suite(output_dir: pathlib.Path, coverage_collector: coverage.Coverage) -> typing.Generator[None]:
    """Patch odoo test suite and Odoo test result.

    - In Odoo 12 and Odoo 13, The test result is the native unittest.TestResult
    - In Odoo 14 and Odoo 15. The test result extend unittest.TestResult and add `update` function. So we call it
    - In 16.0 and more the OdooTestResult don't extend unittest.TestResult.
    I need to patch the `update` function to add result of the `_XmlTestResult`

    Args:
        output_dir: Te patch where to store the xml result
        coverage_collector: A function returning a coverage collector.

    Returns: Nothing, but unpatched function at the end
    """

    odoo_suite_class, odoo_result_class = _try_find_stuff_to_patch()
    if not odoo_suite_class:
        msg = f"Odoo version {odoo.release.version} not supported"
        raise ValueError(msg)
    output_dir.mkdir(exist_ok=True, parents=True)

    _logger.info("Create test result in %s", output_dir.absolute())
    _unpatched_run = odoo_suite_class.run
    patch_odoo_suite_run = f"{odoo_suite_class.__module__}.{odoo_suite_class.__name__}.run"
    _logger.info("Patch %s", patch_odoo_suite_run)
    patch_odoo_suite_update = None
    if odoo_result_class:
        _unpatched_update = odoo_result_class.update
        patch_odoo_suite_update = f"{odoo_result_class.__module__}.{odoo_result_class.__name__}.update"
        _logger.info("Patch %s", patch_odoo_suite_update)

    def patched_suite_run(self, result):
        # Suite run method will be called by the XMLTestRunner,
        # so we need to run the original run method
        with coverage_collector.collect():
            _logger.info("Start Coverage recording...")
            with patch.object(self, "run", lambda result: _unpatched_run(self, result)):
                # Override : XMLTestRunner to run the tests and generate XML reports
                xml_results = XMLTestRunner(
                    output=str(output_dir.absolute()), verbosity=2, resultclass=OdooXmlTestResult
                ).run(self)
                _logger.info(xml_results)
        if hasattr(result, "update"):
            result.update(xml_results)
        elif isinstance(result, unittest.TestResult):
            result.failfast = xml_results.failfast
            result.failures = xml_results.failures
            result.testsRun = xml_results.testsRun
            result.errors = xml_results.errors
            result.skipped = xml_results.skipped
        return result

    def patched_suite_update(self, other):
        # Adapt _XMLTestResult to OdooTestResult
        if isinstance(other, _XMLTestResult):
            self.failures_count += len(other.failures)
            self.errors_count += len(other.errors)
            self.skipped += len(other.skipped)
            self.testsRun += other.testsRun
        else:
            _unpatched_update(self, other)

    with patch(patch_odoo_suite_run, patched_suite_run):
        if odoo_result_class:
            with patch(patch_odoo_suite_update, patched_suite_update):
                yield
        else:
            yield


def _try_find_stuff_to_patch() -> tuple[type[_RunProto] | None, type[_UpdateProto] | None]:
    if "12.0" <= odoo.release.version <= "13.0" or "14.0" <= odoo.release.version <= "15.0":
        from odoo.tests.common import OdooSuite as odoo_suite_class  # noqa: N813, PLC0415

        odoo_result_class = None
    elif "16.0" <= odoo.release.version <= "18.0":
        from odoo.tests.result import OdooTestResult as odoo_result_class  # noqa: N813, PLC0415
        from odoo.tests.suite import OdooSuite as odoo_suite_class  # noqa: N813, PLC0415
    else:
        return None, None

    return odoo_suite_class, odoo_result_class


def run_odoo_and_stop(preload: list[str] | None = None) -> int:
    preload = preload or odoo.tools.config["db_name"].split(",")
    return odoo.service.server.start(preload=preload, stop=True)


def setup_odoo() -> None:
    odoo.cli.server.check_root_user()
    odoo.cli.server.check_postgres_user()
    odoo.cli.server.report_configuration()
    odoo.netsvc.init_logger()


def parse_config(server_args: list[str]) -> None:
    __import__("os").environ["TZ"] = "UTC"
    _logger.info("Start Odoo with args=%s", server_args)
    # Hard set value
    # In test mode we don't care about loading language
    # But il you do multiple step, you load multiple time the registry.
    # And in odoo.modules.loadings.load_module they `pop` this key, idkw
    # So in test mode, we force this option key to None
    odoo.tools.config.options["load_language"] = None
    odoo.tools.config.parse_config(server_args)
