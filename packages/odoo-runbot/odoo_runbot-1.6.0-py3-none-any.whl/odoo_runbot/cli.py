from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import List, Union

import typer
from rich.console import Console, ConsoleOptions, Group, RenderResult
from rich.panel import Panel
from rich.table import Table
from typer import Typer
from typing_extensions import Annotated

from . import runbot_init
from .runbot_config import RunbotStepConfig, RunbotToolConfig, StepAction
from .runbot_env import RunbotEnvironment
from .runbot_run import StepRunner

app = Typer()

env: RunbotEnvironment = None


def rich_force_colors() -> bool:
    """In Gitlab CI runner there is no tty, and no color.

    This function force the color even if there is no TTY
    See Also:
        https://github.com/nf-core/tools/pull/760/files
        https://github.com/Textualize/rich/issues/343
    Returns:
        True if in CI/CD Job or if color is forced
    """
    return bool(
        os.getenv("CI")
        or os.getenv("GITHUB_ACTIONS")
        or os.getenv("FORCE_COLOR")
        or os.getenv("PY_COLORS")
        or os.getenv("COLORTERM") == "truecolor"
    )


console = Console(width=150, force_terminal=rich_force_colors())

_logger = logging.getLogger("odoo_runbot")


@app.callback()
def _callback(workdir: Path = None, config: Union[Path, None] = None, *, verbose: bool = False) -> None:  # noqa: UP007
    global env  # noqa: PLW0603
    env = RunbotEnvironment(dict(os.environ), workdir=workdir, config=config, verbose=verbose)
    env.setup_logging_for_runbot(console)
    if verbose:
        env.print_info()
    if not env.check_ok():
        raise typer.Abort(300)


@app.command("init")
def init_runbot() -> None:
    """Init the current project to run test
    - Find external addons depedency, install them if needed (git clone + pip install)
    - Init database, and wait postgresql is ready
    - Create basic config file for Odoo using $ODOO_RC
    """
    current_project_key = f"ADDONS_LOCAL_{env.abs_curr_dir.name.upper()}"
    try:
        project_config = RunbotToolConfig.load_from_file(env.runbot_config_path)
    except ValueError as e:
        _logger.exception(exec_info=e)
        raise typer.Abort from e
    _logger.info(
        "Add current project %s=%s ? %s",
        current_project_key,
        str(env.abs_curr_dir),
        project_config.include_current_project,
    )
    if project_config.include_current_project:
        env.environ[current_project_key] = str(env.abs_curr_dir)
    info, addons = runbot_init.show_addons(env)
    console.print(info)
    runbot_init.install_addons(addons)
    runbot_init.init_folders(env)
    console.print(runbot_init.init_database(env))
    console.print(runbot_init.init_config(env))


@app.command("run", help="""Run the steps after initializing the project""")
def run_runbot(
    steps: Annotated[List[str], typer.Option()] = None,
    only_action: Annotated[StepAction, typer.Option()] = None,
) -> None:
    """Run the steps after initializing the project

    You can filter the step you want to run with the `step_name` argument.

    warning:
        If no step is run, then mangono-runbot will exit with code 100.

    Args:
        steps:  The step to run, if None, are "all" then no filter is applied
        only_action:  Choose wich action to only run

    """
    step_names = set(steps or [])
    if not steps and env.environ.get("RUNBOT_STEPS"):
        step_names = set(env.environ.get("RUNBOT_STEPS").split(","))

    _logger.info("Running %s steps", list(step_names))
    if not Path(env.ODOO_RC).exists():
        _logger.error("[red] Please run `mangono-runbot init config` to create your odoo config file")
        raise typer.Abort

    try:
        project_config = RunbotToolConfig.load_from_file(env.runbot_config_path)
    except ValueError as e:
        _logger.exception("Error on config :", exec_info=e)
        raise typer.Abort from e
    steps_to_run = []
    for step in project_config.steps:
        if only_action and step.action != only_action:
            _logger.debug("Filter step %s, only want action=%s", step.name, only_action.name)
            continue
        if step_names and not step_names.intersection({None, "all", step.name}):
            _logger.info("Skip %s not in filtered names [%s]", step.name, ", ".join(step_names))
            continue
        steps_to_run.append(step)

    step_runner = StepRunner(env)
    step_runner.setup_warning_filter(project_config.warning_filters)
    step_runner.setup_odoo()
    for step in steps_to_run:
        console.print(RichStep(step))
        rc = step_runner.execute(step)
        if rc:
            console.print(f"[red] Step {step.name} {bool_to_emoji(False)}")  # noqa: FBT003
        console.print(f"[green] Step {step.name} {bool_to_emoji(True)}")  # noqa: FBT003
        write_exit_code(step, return_code=rc, failfast=project_config.failfast)

    if not step_runner.has_run:
        write_exit_code(step=None, return_code=100, failfast=True)


def write_exit_code(step: RunbotStepConfig | None, *, return_code: int, failfast: bool) -> None:
    if env.in_ci and step:
        datas = {}
        exit_file = Path(env.result_path / "runbot-exit.json")
        exit_file.touch(exist_ok=True)
        if exit_file.stat().st_size > 0:
            datas = json.load(exit_file.open())
        datas[step.name] = return_code
        exit_file.write_text(json.dumps(datas))
        color = "red" if return_code else "green"
        console.print(f"[{color}] Write exit code '{return_code}' to {exit_file!s}")

    if failfast and return_code:
        rc_code = return_code
        if env.in_ci:
            rc_code = 0
        raise typer.Exit(rc_code)


def get_exit_codes() -> dict[str, int]:
    exit_file = Path(env.result_path / "runbot-exit.json")
    if not exit_file.exists():
        return {}
    return json.load(exit_file.open())


@app.command("report")
def report() -> None:
    project_config = RunbotToolConfig.load_from_file(env.runbot_config_path)
    rc_code = 0
    for step_name, rc in get_exit_codes().items():
        step = project_config.get_step(step_name)
        console.print(RichStep(step, "red" if rc > 0 else None))
        rc_code += rc
    step_runner = StepRunner(env)
    coverage = step_runner.get_coverage()
    coverage.load()
    if coverage.get_data():
        coverage.report()
        coverage.xml_report(outfile=str(env.result_path / "coverage.xml"))
        coverage.html_report(directory=str(env.result_path / "coverage_html"))
    raise typer.Exit(rc_code)


def bool_to_emoji(v: bool) -> str:  # noqa: FBT001
    return ":heavy_check_mark:" if v else ":x:"


ASCII_ART_MANGONO = """
                          [medium_spring_green]      %    %             [/]
                          [medium_spring_green]    %%%   %%%   %%%%%%%  [/]
                          [medium_spring_green]  %%%%   %%%   %%%    %%%[/]
                          [medium_spring_green]%%%%     %%%   %%     %%%[/]
                          [medium_spring_green]  %%%%   %%%   %%%    %%%[/]
                          [medium_spring_green]    %%%   %%%   %%%%%%%  [/]
                          [medium_spring_green]      %    %             [/]

          @@@    @@@@   @@@@    @@@   @@   @@@@@@    @@@@@@   @@@   @@   @@@@@@    [medium_spring_green]%%%[/]
          @@@@   @@@@   @@@@    @@@@  @@  @@   @@@  @@@  @@@@ @@@@  @@  @@@  @@@   [medium_spring_green]  %%%[/]
          @@@@@ @@@@@  @@@ @@   @@ @@ @@ @@@ @@@@@@@@@    @@@ @@ @@ @@ @@@    @@@  [medium_spring_green]   %%%%[/]
          @@@ @@@ @@@ @@@@@@@@  @@  @@@@  @@    @@  @@@  @@@@ @@  @@@@  @@@  @@@   [medium_spring_green]  %%%[/]
          @@@ @@@ @@@ @@    @@@ @@   @@@   @@@@@@    @@@@@@   @@   @@@   @@@@@@    [medium_spring_green]%%%[/]

             @ @ @@ @  @@ @ @ @@@ @ @@  @@ @@@ @ @  [medium_spring_green]%%%%%%%%%[/]
                                                    [medium_spring_green]%%%%%%%%%[/]
"""


@app.command("diag")
def diag_print(step_names: bool = False, only_action: Annotated[StepAction, typer.Option()] = None) -> None:  # noqa: FBT001,FBT002
    if step_names:
        for s in RunbotToolConfig.load_from_file(env.runbot_config_path).steps:
            if only_action and s.action != only_action:
                continue
            console.print(s.name)
        return
    console.print(ASCII_ART_MANGONO)
    from . import __about__ as about  # noqa: PLC0415

    console.print(f"Version: {about.__version__}")
    console.print(f"Main Author: {about.__author__}({about.__author_email__})")
    console.print(f"Workdir: {env.abs_curr_dir}")
    console.print("Result (Test & Coverage): %s", env.result_path)
    from coverage import cmdline  # noqa: PLC0415

    cmdline.show_help(topic="version")
    t_warn = Table(
        "Name",
        "Action",
        "Message Filter",
        "Wanted Category",
        title="py.warnings Filters",
    )

    try:
        project_config = RunbotToolConfig.load_from_file(env.runbot_config_path)
    except ValueError as e:
        raise typer.Abort(e.args) from e
    if project_config.warning_filters:
        for log_filter in project_config.warning_filters:
            t_warn.add_row(
                log_filter.name,
                log_filter.action,
                f"r'{log_filter.message}'",
                log_filter.category,
            )
    else:
        t_warn.add_row("[DEFAULT] No py.warnings allowed", "always", ".*", "Warnings", "*")
    console.print(t_warn)
    table = Table(
        "Step",
        "Module",
        "Run tests",
        "Activate Coverage",
        "Tags to test",
        "Logger filter",
        title="Steps",
    )
    for step in project_config.steps:
        table.add_row(
            step.name,
            (step.modules and ",".join(step.modules)) or str(step.modules),
            step.action.name,
            bool_to_emoji(step.action == StepAction.TESTS and step.coverage),
            ",".join(step.test_tags),
            ",".join([f.name for f in step.log_filters]),
        )
    console.print(table)

    for step in project_config.steps:
        console.print(RichStep(step))


class RichStep:
    def __init__(self, step: RunbotStepConfig, color: str | None = None) -> None:
        self.step = step
        self._color = color or "green" if self.step.action == StepAction.TESTS else "dodger_blue2"

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        t_log = Table("Name", "Regex", "Match", "logger", title="Log Filters", width=146)
        if self.step.log_filters:
            for log_filter in self.step.log_filters:
                match_txt = f"Between {log_filter.min_match} and {log_filter.max_match}"
                if log_filter.min_match == log_filter.max_match:
                    match_txt = f"Exactly {log_filter.min_match}"
                t_log.add_row(
                    log_filter.name,
                    f"r'{log_filter.regex}'",
                    match_txt,
                    log_filter.logger + " (and all child logger)",
                )
        else:
            t_log.add_row("[DEFAULT] No log allowed", ".*", "Exactly 0", "odoo (and all child logger)")

        yield Panel(
            Group(
                f"Install : {self.step.modules}",
                f"Action : {self.step.action.name}",
                f"Activate Coverage: {bool_to_emoji(self.step.action == StepAction.TESTS and self.step.coverage)}",
                f"Allow warnings: {bool_to_emoji(self.step.allow_warnings)}",
                f"Test Tags: {self.step.test_tags}",
                t_log,
            ),
            style=self._color,
            title=self.step.name,
        )


if __name__ == "__main__":
    app()
