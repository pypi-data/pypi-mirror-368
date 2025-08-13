"""Contains all the code used to assert Logger and warnings a propely catched."""

from __future__ import annotations

import logging
import types
import typing
import unittest

from xmlrunner import XMLTestRunner
from xmlrunner.result import _XMLTestResult

if typing.TYPE_CHECKING:
    import pathlib
    from warnings import WarningMessage

    from .runbot_run_logging import ExcludeWarningFilter

_logger = logging.getLogger("odoo_runbot")


class XmlResultSilent(_XMLTestResult):
    def _is_relevant_tb_level(self, tb):  # noqa: ANN001 ARG002 ANN202
        return True


def get_test_runner(output_dir: pathlib.Path | None = None) -> unittest.TextTestRunner:
    """Retun a default Runner.

    If an `output_dir` is filed, then `xmlrunner.XMLTestRunner` is returned
    Args:
        output_dir: The path where the test resul;t should be stored

    Returns: The class to run unittest tests

    """
    if output_dir and output_dir.exists():
        return XMLTestRunner(output=str(output_dir.resolve()), failfast=False, resultclass=XmlResultSilent, verbosity=2)
    return unittest.TextTestRunner(failfast=False, resultclass=XmlResultSilent, verbosity=2)


def execute_test_after_odoo(
    dynamic_class_name: str,
    log_filters: list[ExcludeWarningFilter] | None = None,
    warning_message: list[WarningMessage] | None = None,
    *,
    test_runner: unittest.TextTestRunner | None = None,
) -> unittest.result.TestResult:
    """Generate 1 [unittest.TestCase][] for each filter.

    If `test_runner` is `None` then [unittest.TextTestRunner][] is used.

    Note:
        If `filter_to_test` is `None` then A default succeed TestResult is returned.

    Args:
        dynamic_class_name: The name of the class to generate, No sneedTo start with "Test"
        log_filters: All the Log filter to add in the test suite
        warning_message: All the warning message catch, if any then the suite will failed
        test_runner: your custom runner, or [unittest.TextTestRunner][]

    Returns:
        The result of the test runner with your runner if set.

    """
    _logger.info("Execute Logger Filter test suite for %s filters", (log_filters and len(log_filters)) or 0)
    test_runner = test_runner or get_test_runner(None)
    if not log_filters and not warning_message:
        return unittest.result.TestResult()
    test_class = types.new_class(f"Test{_slug_str(dynamic_class_name)}", (_RunbotLoggerUnitTest,), {})
    generated_test_func = []
    suite = unittest.TestSuite()
    for log_filter in log_filters:
        dynamic_name = f"test_{_slug_str(log_filter.exclude.name)}"
        generated_test_func.append((dynamic_name, log_filter))
        setattr(test_class, dynamic_name, test_class._template_logger_filter)  # noqa: SLF001
        suite.addTest(test_class(dynamic_name, logger_filter=log_filter, warning_msg=None))
    if warning_message:
        test_class.test_warnings = test_class._template_test_warning_filter  # noqa: SLF001
        generated_test_func.append("test_warnings")
        suite.addTest(test_class("test_warnings", logger_filter=None, warning_msg=warning_message))

    _logger.debug("Test suite created, run it with %s", type(test_runner).__name__)
    return test_runner.run(suite)


def _slug_str(value: str) -> str:
    return "".join(d.capitalize() for d in value.split()).replace(" ", "").replace("-", "").lower()


class _RunbotLoggerUnitTest(unittest.TestCase):
    def __init__(
        self, method_name: str, logger_filter: ExcludeWarningFilter, warning_msg: list[WarningMessage]
    ) -> None:
        super().__init__(method_name)
        self.logger_filter = logger_filter
        self._testMethodDoc = self._make_description()
        self.warning_filter = warning_msg
        self._testMethodDoc = ""
        if logging.root.handlers:
            self.format_log = logging.root.handlers[0].format
        else:
            self.format_log = logging.Formatter.format

    def _template_logger_filter(self) -> None:
        self.assertTrue(self.logger_filter)  # noqa: PT009
        if self.logger_filter.success:
            self.assertTrue(self.logger_filter.success)  # noqa: PT009
            return

        fail_msg = [
            f"{self.logger_filter.exclude.name} Failed for logger '{self.logger_filter.exclude.logger or 'all'}'",
            f"Expected: {self.logger_filter.exclude.min_match} "
            f"<= len(match_log_lines) <= {self.logger_filter.exclude.max_match}",
            f"Found {len(self.logger_filter.log_match)} "
            f"log line who match the regex r'{self.logger_filter.regex.pattern}'",
        ]
        if self.logger_filter.log_match:
            fail_msg.append("Log line content :")
        fail_msg.extend(["\t> " + self.format_log(log_record) for log_record in self.logger_filter.log_match])
        self.fail("\n".join(fail_msg))

    def _make_description(self) -> str:
        if self.logger_filter:
            return (
                f"{self.logger_filter.exclude.name} Regex Matcher "
                f"for logger '{self.logger_filter.exclude.logger or 'all'}'"
            )
        return ""

    def _template_test_warning_filter(self) -> None:
        self.assertTrue(self.warning_filter)  # noqa: PT009
        fail_msg = ["Some py.warnings found"] + ["\t> " + str(m) for m in self.warning_filter]
        self.fail(msg="\n".join(fail_msg))


class _RunbotPyWarningUnitTest(unittest.TestCase):
    def __init__(self, warning_msg: list[WarningMessage]) -> None:
        super().__init__("test_warning_filter")
        self.warning_filter = warning_msg
        self._testMethodDoc = ""
