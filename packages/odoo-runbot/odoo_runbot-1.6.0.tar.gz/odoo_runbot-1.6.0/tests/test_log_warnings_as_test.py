import logging

from odoo_runbot import runbot_run_logging as log_handler
from odoo_runbot.runbot_config import RunbotExcludeWarning, RunbotStepConfig
from odoo_runbot.runbot_run_logging import ExcludeWarningFilter, RunbotWarningWatcherHandler
from odoo_runbot.runbot_run_test import execute_test_after_odoo

_logger = logging.getLogger("odoo")


def teardown_function():
    """On teardown, remove all runbot logging handlers"""
    for handler in logging.root.handlers[:]:
        if isinstance(handler, RunbotWarningWatcherHandler):
            logging.root.removeHandler(handler)


def test_log_setup_1_step():
    warn_rule = RunbotExcludeWarning(name="MyRegex", min_match=2, max_match=2, regex=".*This is a warn.*")
    step = RunbotStepConfig(
        name="test",
        modules=["module1"],
        log_filters=[warn_rule],
    )
    assert log_handler.get_handler() not in logging.root.handlers, "The handler is not activated"
    with log_handler.start_warning_log_watcher(step) as log_filters:
        global_handler = log_handler.get_handler()
        assert log_handler.get_handler() in logging.root.handlers, "Runbot Handler activated"
        assert global_handler is not None, "Should be initialized after `start_warning_log_watcher`"
        assert len(global_handler.record_matchers()) == 1, "One warnings rule in step eq 1 filter in log handler"
        assert isinstance(global_handler.record_matchers()[0], ExcludeWarningFilter), (
            "contains only ExcludeWarningFilter"
        )
        assert global_handler.record_matchers()[0].exclude == warn_rule

    log_filters()
    assert not log_handler.get_handler().record_matchers(), "After stop no more warnings rule registered"


def test_log_setup_2_step():
    warn_rule1 = RunbotExcludeWarning(name="warn_rule1", regex=".*This is a warn.*")
    step1 = RunbotStepConfig(
        name="step1",
        modules=["module1"],
        log_filters=[warn_rule1],
    )
    warn_rule2_1 = RunbotExcludeWarning(name="warn_rule2_1", regex=".*This is a warn.*")
    warn_rule2_2 = RunbotExcludeWarning(name="warn_rule2_2", regex=".*This is a warn2.*")
    step2 = RunbotStepConfig(
        name="step2",
        modules=["module1"],
        log_filters=[warn_rule2_1, warn_rule2_2],
    )

    assert log_handler.get_handler() not in logging.root.handlers, "The handler is not activated"
    with log_handler.start_warning_log_watcher(step2) as extractor2:
        assert log_handler.get_handler() in logging.root.handlers, "Runbot Handler step1 activated"
        global_handler = log_handler.get_handler()
        assert len(global_handler.record_matchers()) == 2, "2 filter in step 2"
        with log_handler.start_warning_log_watcher(step1) as extractor1:
            assert len(global_handler.record_matchers()) == 3, "1 filter in step 1 + 2 filters in step2"
            assert all(isinstance(_filter, ExcludeWarningFilter) for _filter in global_handler.record_matchers()), (
                "contains only ExcludeWarningFilter"
            )
            msg1 = "This is a warning. - captured by warn_rule2_1 filter first"
            _logger.warning(msg1)

        filter_warnings = extractor1()
        assert len(filter_warnings) == 1, "1 Filter in step1"
        assert filter_warnings[0].exclude == warn_rule1
        assert len(filter_warnings[0].log_match) == 0, "Catch 0 log line, warn_rule2_1 catch it first"
        assert len(log_handler.get_handler().record_matchers()) == 2, "Still have the 2 filter from step2"
        msg2 = "This is a warning. - captured by warn_rule2_1 filter"
        msg3 = "This is a warn2 - captured by warn_rule2_1 and warn_rule2_2 filters"
        msg4 = "This is a warn2 - not caputred, incorect log level"
        _logger.warning(msg2)
        _logger.warning(msg3)

        _logger.debug(msg4)
        _logger.info(msg4)

    filter_warnings2 = extractor2()
    assert len(filter_warnings2) == 5, "2 Filter in step2 + 3 for the default"
    assert filter_warnings2[0].exclude == warn_rule2_1
    assert filter_warnings2[1].exclude == warn_rule2_2
    assert filter_warnings2[0].log_match.pop(0).getMessage() == msg1
    assert filter_warnings2[0].log_match.pop(0).getMessage() == msg2
    assert filter_warnings2[0].log_match.pop(0).getMessage() == msg3
    assert not filter_warnings2[0].log_match, "More than 3 log catched ? " + str(filter_warnings2[0].log_match)

    assert not filter_warnings2[1].log_match, "No message to catch (all catch by previous filter" + str(
        filter_warnings2[1].log_match,
    )


def test_log_warnings_as_test():
    """I only wan't one line of log with message Containing "This is a warn"
    If 0 -> Failed
    if 1 -> success
    if 2 -> failed
    """
    step = RunbotStepConfig(
        name="test",
        modules=["module1"],
        log_filters=[
            RunbotExcludeWarning(
                name="MyRegex",
                min_match=2,
                max_match=2,
                regex=".*This is a warn.*",
            ),
        ],
    )
    logger = logging.getLogger("odoo")
    sub_logger = logging.getLogger("odoo.sql")
    with log_handler.start_warning_log_watcher(step) as extractor:
        logger.warning("This is a warning line captured")
        sub_logger.warning("This is a warning line captured (second)")
    filters = extractor()
    test_result = execute_test_after_odoo("Fake", filters)
    assert test_result.wasSuccessful(), "Should catch the 2 log line above"
    assert test_result.testsRun == 4, "My Step contains 1 warnings, and the 3 default catch all"


def test_start_and_stop_watching():
    """I only want one line of log with message Containing "This is a warn"
    If 0 -> Failed
    if 1 -> success
    if 2 -> failed
    """
    step = RunbotStepConfig(
        name="test",
        modules=["module1"],
        log_filters=[
            RunbotExcludeWarning(
                name="MyRegex",
                logger="odoo.sql",
                min_match=1,
                max_match=1,
                regex=".*This is a warn.*",
            ),
        ],
    )
    assert log_handler.get_handler() not in logging.root.handlers, "The handler is not activated"
    with log_handler.start_warning_log_watcher(step) as extractor:
        handler_post_start = log_handler.get_handler()
        assert handler_post_start is not None, "After start, the handler is registered"
        assert len(handler_post_start.record_matchers()) == 1
    extractor()
    assert not log_handler.get_handler().filters, "After stop, no filter is activated"


def test_no_rule_default_catcher():
    "Create a step without filter, then all warning logs are catch and this should created a final failed test result"
    step = RunbotStepConfig(
        name="test",
        modules=["module1"],
        log_filters=[],
    )
    assert log_handler.get_handler() not in logging.root.handlers, "The handler is not activated"
    with log_handler.start_warning_log_watcher(step) as extractor:
        handler_post_start = log_handler.get_handler()
        assert handler_post_start is not None, "After start, the handler is registered"
        assert not handler_post_start.filters, "No filter"

        logging.getLogger("my_logger").warning("Catch this log warning")

    log_filter = extractor()
    result = execute_test_after_odoo("Fake", log_filter)
    assert not result.wasSuccessful(), "Should catch the 2 log line above"


def test_no_catch_rule_default_catcher():
    "Create a step without filter, then all warning logs are catch and this should created a final failed test result"
    step = RunbotStepConfig(
        name="test",
        modules=["module1"],
        log_filters=[
            RunbotExcludeWarning(
                name="MyRegex",
                logger="odoo.sql",
                min_match=1,
                max_match=1,
                regex=".*This is a warn.*",
            ),
        ],
    )
    assert log_handler.get_handler() not in logging.root.handlers, "The handler is not activated"
    with log_handler.start_warning_log_watcher(step) as extractor:
        logging.getLogger("my_logger").warning("No catched warning")

    log_filter = extractor()
    result = execute_test_after_odoo("Fake", log_filter)
    assert not result.wasSuccessful(), "Should catch the 2 log line above"


def test_no_catch_only_default_catcher():
    """Create a step without filter.

    then all warning logs are catch and this should created a final failed test result
    """
    step = RunbotStepConfig(
        name="test",
        modules=["module1"],
        log_filters=[],
    )
    assert log_handler.get_handler() not in logging.root.handlers, "The handler is not activated"
    with log_handler.start_warning_log_watcher(step) as extractor:
        logging.getLogger("my_logger").warning("No catched warning")
    log_filter = extractor()
    result = execute_test_after_odoo("Fake", log_filter)
    assert not result.wasSuccessful(), "Should catch the 2 log line above"


def test_catch_critical():
    step = RunbotStepConfig(
        name="test",
        modules=["module1"],
        log_filters=[
            RunbotExcludeWarning(
                name="MyRegex",
                regex=".*This is a warn.*",
                max_match=0,
            ),
        ],
    )
    assert log_handler.get_handler() not in logging.root.handlers, "The handler is not activated"
    with log_handler.start_warning_log_watcher(step) as extractor:
        logging.getLogger("my_logger").critical("critical %s", "msg")
        logging.getLogger("my_logger").error("error %s", "msg")
        logging.getLogger("my_logger").exception("exception %s", "msg")
        logging.getLogger("my_logger").warning("warning %s", "msg")
        logging.getLogger("my_logger").debug("debug %s", "msg")
        logging.getLogger("my_logger").info("info %s", "msg")

    log_filter = extractor()
    result = execute_test_after_odoo("Fake", log_filter)
    assert not result.wasSuccessful(), "Should catch the 2 log line above"
    assert result.testsRun == 4, "3 Default catcher + 1 rule"
    assert len(result.failures) == 3
    assert "AssertionError: Runbot WARNING catch all no filter Failed" in result.failures[0][1], (
        "Assert it's the default catcher, not the rule"
    )
    assert "AssertionError: Runbot ERROR catch all no filter Failed" in result.failures[1][1], (
        "Assert it's the default catcher, not the rule"
    )
    assert "AssertionError: Runbot CRITICAL catch all no filter Failed" in result.failures[2][1], (
        "Assert it's the default catcher, not the rule"
    )


def test_filter_critical():
    step = RunbotStepConfig(
        name="test",
        modules=["module1"],
        log_filters=[
            RunbotExcludeWarning(
                level=logging.getLevelName(logging.CRITICAL),
                name="MyRegex",
                regex=".*msg.*",
                max_match=1,
                min_match=1,
            ),
        ],
    )
    assert log_handler.get_handler() not in logging.root.handlers, "The handler is not activated"
    with log_handler.start_warning_log_watcher(step) as extractor:
        logging.getLogger("my_logger").critical("critical %s", "msg")
        logging.getLogger("my_logger").critical("critical %s", "message")  # Not the correct message
        logging.getLogger("my_logger").error("error %s", "msg")
        logging.getLogger("my_logger").warning("warning %s", "msg")
        logging.getLogger("my_logger").debug("debug %s", "msg")
        logging.getLogger("my_logger").info("info %s", "msg")

    log_filter = extractor()
    result = execute_test_after_odoo("Fake", log_filter)
    assert not result.wasSuccessful()
    assert result.testsRun == 4, "3 Default catcher + 1 rule"
    assert len(result.failures) == 3
    assert "AssertionError: Runbot WARNING catch all no filter Failed" in result.failures[0][1], (
        "Assert it's the default catcher, not the rule"
    )
    assert "AssertionError: Runbot ERROR catch all no filter Failed" in result.failures[1][1], (
        "Assert it's the default catcher, not the rule"
    )
    assert "AssertionError: Runbot CRITICAL catch all no filter Failed" in result.failures[2][1], (
        "Assert it's the default catcher, not the rule"
    )


def test_match_msg_with_args():
    log_filter = RunbotExcludeWarning(
        name="MyRegex",
        regex=".*A msg with args value=toto.*",
    )
    step = RunbotStepConfig(
        name="test",
        modules=["module1"],
        log_filters=[log_filter],
    )
    with log_handler.start_warning_log_watcher(step) as extractor:
        msg1 = "A msg with args value=%s"
        _logger.warning(msg1, "toto")  # Catch by my step filter
        _logger.warning(msg1, "tutu")  # Catch by global filter

    filter_warnings = extractor()
    assert len(filter_warnings) == 4, "1 Filter in step1 + 3 Catch all"
    assert filter_warnings[0].exclude == log_filter
    assert bool(filter_warnings[0].log_match), "Should contains the msg with 'toto'"

    assert filter_warnings[0].log_match.pop(0).getMessage() == "A msg with args value=toto"
    assert filter_warnings[1].log_match.pop(0).getMessage() == "A msg with args value=tutu"
    assert not filter_warnings[0].log_match, "More than 2 log catched ? " + str(filter_warnings[0].log_match)
