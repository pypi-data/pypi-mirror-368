import pathlib
import sys

from odoo_runbot.runbot_config import RunbotExcludeWarning, RunbotStepConfig, RunbotToolConfig, StepAction

if sys.version_info >= (3, 11):
    pass
else:
    pass


def sample_config(fname: str) -> RunbotToolConfig:
    path = pathlib.Path(__file__).resolve().parent.joinpath("sample_config", fname)
    return RunbotToolConfig.load_from_file(path)


def minimal_config_test(config: RunbotToolConfig):
    """[tool.runbot]
    modules = ["module_to_test"]
    """
    global_module = ["module_to_test"]
    assert config == RunbotToolConfig(
        include_current_project=True,
        steps=[
            RunbotStepConfig(
                name="default",
                modules=global_module,
                action=StepAction.TESTS,
                test_tags=[],
                coverage=True,
                log_filters=[],
            ),
        ],
        pretty=True,
    )


def classic_file_config_test(config: RunbotToolConfig):
    assert config == RunbotToolConfig(
        include_current_project=True,
        steps=[
            RunbotStepConfig(
                name="install",
                modules=["moduleA", "moduleB"],
                action=StepAction.INSTALL,
                test_tags=[],
                coverage=False,
                log_filters=[],
            ),
            RunbotStepConfig(
                name="step1",
                modules=["module3"],
                action=StepAction.TESTS,
                test_tags=[],
                coverage=True,
                log_filters=[],
            ),
            RunbotStepConfig(
                name="step2",
                modules=["module_step2"],
                action=StepAction.TESTS,
                test_tags=[],
                coverage=True,
                log_filters=[],
            ),
            RunbotStepConfig(
                name="step3",
                modules=["moduleA", "moduleB"],
                action=StepAction.TESTS,
                test_tags=[],
                coverage=True,
                log_filters=[],
            ),
        ],
        pretty=True,
    )


def pyproject_classic_test(config: RunbotToolConfig, config_full: RunbotToolConfig):
    global_module = ["module_to_test", "module_to_test_2"]
    global_log_filter = [
        RunbotExcludeWarning(
            name="All Steps - Logger Filter 1",
            regex=".*log to accept.*",
            logger="",
            min_match=1,
            max_match=1,
        )
    ]
    assert (
        config
        == config_full
        == RunbotToolConfig(
            include_current_project=True,
            steps=[
                RunbotStepConfig(
                    name="install",
                    modules=global_module,
                    action=StepAction.INSTALL,
                    test_tags=[],
                    coverage=False,
                    log_filters=global_log_filter,
                ),
                RunbotStepConfig(
                    name="tests",
                    modules=global_module,
                    action=StepAction.TESTS,
                    test_tags=["/module_to_test:MyTestCase", "/module_to_test"],
                    coverage=True,
                    log_filters=global_log_filter,
                ),
            ],
            pretty=True,
        )
    )


def pyproject_complex_test(config: RunbotToolConfig):
    global_regex = [
        RunbotExcludeWarning(
            name="All Steps - Logger Filter 1",
            regex=r".*global-regex-warning-1.*",
        ),
        RunbotExcludeWarning(
            name="global-regex-warning-2",
            regex=r".*global-regex-warning-2.*",
            min_match=1,
            max_match=2,
        ),
    ]
    global_module = ["module_to_test", "module_to_test2"]
    global_coverage = False

    assert config == RunbotToolConfig(
        include_current_project=True,
        steps=[
            RunbotStepConfig(
                name="install",
                modules=["first_module_to_install"],
                action=StepAction.INSTALL,
                test_tags=[],
                coverage=global_coverage,
                log_filters=[
                    *global_regex,
                    RunbotExcludeWarning(
                        regex=".*Install filter.*",
                        name="Step install - Logger Filter 3",
                        min_match=1,
                        max_match=1,
                    ),
                ],
            ),
            RunbotStepConfig(
                name="tests",
                modules=global_module,
                action=StepAction.TESTS,
                test_tags=["+at-install", "-post-install"],
                coverage=True,
                log_filters=[
                    *global_regex,
                    RunbotExcludeWarning(
                        regex=".*regex warning.*",
                        name="test-regex-log-warning-2",
                        min_match=1,
                        max_match=1,
                    ),
                ],
            ),
            RunbotStepConfig(
                name="warmup",
                modules=["second_module_to_install"],
                action=StepAction.INSTALL,
                test_tags=[],
                coverage=global_coverage,
                log_filters=global_regex,
            ),
            RunbotStepConfig(
                name="Post install test",
                modules=["module_to_test2"],
                action=StepAction.TESTS,
                test_tags=["-at-install", "+post-install"],
                coverage=False,
                log_filters=[
                    *global_regex,
                    RunbotExcludeWarning(
                        name="Step Post install test - Logger Filter 3",
                        regex=".*Post install test regex-warnings.*",
                        min_match=2,
                        max_match=2,
                    ),
                ],
            ),
        ],
        pretty=True,
    )
