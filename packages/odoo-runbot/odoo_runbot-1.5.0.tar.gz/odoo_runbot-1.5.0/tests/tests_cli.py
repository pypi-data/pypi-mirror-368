from typer.testing import CliRunner

from odoo_runbot.cli import app

runner = CliRunner()


def test_app():
    result = runner.invoke(app, ["--workdir", "odoo_project", "--config", "", "diag"])
    assert result.exit_code == 0
