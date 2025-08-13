import pathlib
import sys
from typing import Literal

from odoo_runbot.runbot_config import RunbotExcludeWarning, RunbotToolConfig

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
from . import config_tester

F_FTYPE = Literal["pyproject", "custom"]


def sample_config(fname: str, f_type: F_FTYPE) -> RunbotToolConfig:
    path = pathlib.Path(__file__).resolve().parent.joinpath("sample_config", f"{f_type}_{fname}")
    with path.open(mode="rb") as pyproject_toml:
        data = tomllib.load(pyproject_toml)
    if f_type == "pyproject":
        return RunbotToolConfig.load_from_toml_data(data.get("tool", {}).get("runbot"), config_file=path)
    return RunbotToolConfig.load_from_toml_data(data, config_file=path)


def test_minimal_config():
    """[tool.runbot]
    modules = ["module_to_test"]
    """
    assert sample_config("minimal.toml", "pyproject") == sample_config("minimal.toml", "custom")
    config_tester.minimal_config_test(sample_config("minimal.toml", "pyproject"))
    config_tester.minimal_config_test(sample_config("minimal.toml", "custom"))


def test_minimal_file_config():
    """[tool.runbot]
    modules = ["module_to_test"]
    """
    assert sample_config("classic.file.toml", "pyproject") == sample_config("classic.file.toml", "custom")
    config_tester.classic_file_config_test(sample_config("classic.file.toml", "pyproject"))
    config_tester.classic_file_config_test(sample_config("classic.file.toml", "custom"))


def test_pyproject_classic():
    assert sample_config("classic.toml", "pyproject") == sample_config("classic.toml", "custom")
    assert sample_config("classic.full.toml", "pyproject") == sample_config("classic.full.toml", "custom")
    config_tester.pyproject_classic_test(
        sample_config("classic.toml", "pyproject"), sample_config("classic.full.toml", "pyproject")
    )
    config_tester.pyproject_classic_test(
        sample_config("classic.toml", "custom"), sample_config("classic.full.toml", "custom")
    )
    config_tester.pyproject_classic_test(
        sample_config("classic.toml", "pyproject"), sample_config("classic.full.toml", "custom")
    )


def test_pyproject_complex():
    assert sample_config("complex.toml", "pyproject") == sample_config("complex.toml", "custom")
    config_tester.pyproject_complex_test(sample_config("complex.toml", "pyproject"))
    config_tester.pyproject_complex_test(sample_config("complex.toml", "custom"))


def test_min_max_match_log_filter():
    assert RunbotExcludeWarning(name="A", regex="A", min_match=2) == RunbotExcludeWarning(
        name="A",
        regex="A",
        min_match=2,
        max_match=2,
    ), "Assert Min and max match follow each other if not set"
    assert RunbotExcludeWarning(name="A", regex="A", min_match=10, max_match=2) == RunbotExcludeWarning(
        name="A",
        regex="A",
        max_match=10,
        min_match=10,
    ), "Assert Min and max match follow each other if not set"
    assert RunbotExcludeWarning(name="A", regex="A", min_match=-1) == RunbotExcludeWarning(
        name="A",
        regex="A",
        max_match=1,
        min_match=0,
    ), "Assert if Min is -1 then this means 0 min match"
    assert RunbotExcludeWarning(name="A", regex="A", min_match=0) == RunbotExcludeWarning(
        name="A",
        regex="A",
        max_match=1,
        min_match=0,
    ), "Assert if Min is 0 then this means 0 min match"
    assert RunbotExcludeWarning(name="A", regex="A", max_match=0) == RunbotExcludeWarning(
        name="A",
        regex="A",
        max_match=0,
        min_match=0,
    ), "Assert if Max is 0 means exacly 0 match possible"
    assert RunbotExcludeWarning(name="A", regex="A", max_match=999) == RunbotExcludeWarning(
        name="A",
        regex="A",
        max_match=100,
        min_match=1,
    ), "Assert if Max can't be more than 100If you want more than 100, you should fix this logger :-)"
