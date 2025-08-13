"""This lib is a CLI using typer.

I tried to separate the code by feature part.

- [odoo_runbot.cli][] Contains the entrypoint, All the rich display is done here. (Other than log)
- [odoo_runbot.runbot_env][] Contains il a python way the env in wich the runbot is running.
- [odoo_runbot.runbot_init][] Contains all the code to execute to initialize the Odoo to run test
- [odoo_runbot.runbot_init_branch_resolver][] Contains the working branch resolving (Pull other add-ons from git)
"""

__import__("os").environ["TZ"] = "UTC"
__import__("os").environ["WITHOUT_DEMO"] = "False"
