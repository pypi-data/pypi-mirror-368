from __future__ import annotations

import configparser
import importlib
import logging
import time
import typing
from pathlib import Path

import odoo_env_config
from addons_installer.addons_installer import AddonsFinder, AddonsInstaller, OdooAddonsDef
from odoo_env_config import entry, section

if typing.TYPE_CHECKING:
    from rich.console import ConsoleRenderable

    from .runbot_env import RunbotEnvironment

from rich.table import Table

from . import _odoo_internal
from .runbot_init_branch_resolver import AddonsBranchResolver, AddonsToInstall

_logger = logging.getLogger("odoo_runbot")


def show_addons(env: RunbotEnvironment) -> ConsoleRenderable:
    """Returns:"""
    _logger.debug("Find debpends addons from environement variables")
    addons: set[OdooAddonsDef] = AddonsFinder().parse_env(env.environ)
    addons_branch_resolver = AddonsBranchResolver(env, addons)
    addons_to_install: list[AddonsToInstall] = addons_branch_resolver.resolve_branch_addons_git()
    table = Table("Name", "Branch to test", "Used", "Install Path", "Exist")
    for to_install in addons_to_install:
        exist = ":heavy_check_mark:" if Path(to_install.addon.addons_path).exists() else ":x:"
        table.add_row(
            to_install.addon.name,
            ", ".join(to_install.branch_try),
            to_install.branch_to_use,
            to_install.addon.addons_path,
            exist,
        )
    return table, addons_to_install


def install_addons(addons_to_install: list[AddonsToInstall]) -> None:
    for addon in addons_to_install:
        AddonsInstaller.install(addon.addon)


def init_database(env: RunbotEnvironment, max_retry: int = 3) -> int:
    """Returns:"""
    if not importlib.util.find_spec("psycopg2"):
        _logger.warning("psycopg2 not installed")

    db_section = entry.env_to_section(section.DatabaseOdooConfigSection, extra_env=env.environ)
    _logger.info("Creating database %s on %s:%s...", db_section.name, db_section.host, db_section.port)
    if _db_exist(db_section):
        _logger.info("Database %s on %s:%s already created", db_section.name, db_section.host, db_section.port)
        return 0

    import psycopg2  # noqa: PLC0415
    from psycopg2 import sql  # noqa: PLC0415

    conn = psycopg2.connect(
        dbname=db_section.user,
        user=db_section.user,
        password=db_section.password,
        host=db_section.host,
        port=db_section.port,
    )
    conn.autocommit = True
    retry = 0
    db_created = False
    createdb_cmd = sql.SQL("CREATE DATABASE {} ENCODING 'unicode' LC_COLLATE 'C' TEMPLATE template0;").format(
        sql.Identifier(db_section.name),
    )
    while retry <= max_retry and not db_created:
        time.sleep(5)
        try:
            with conn.cursor() as curs:
                curs.execute(createdb_cmd)
                db_created = True
                _logger.info(
                    "Database %s on %s:%s created successfully",
                    db_section.name,
                    db_section.host,
                    db_section.port,
                )
        except psycopg2.OperationalError:
            retry += 1
            _logger.info(
                "Failed to create database %s on %s:%s. retry in 5 seconds (%s / %s)",
                db_section.name,
                db_section.host,
                db_section.port,
                retry,
                max_retry,
            )
            if retry > max_retry:
                raise
    return 0


def init_config(env: RunbotEnvironment) -> ConsoleRenderable:
    """Returns:"""
    odoo_env_config.entry.direct_run_command(_odoo_internal.odoo, [], env.ODOO_RC, other_env=env.environ)
    config = configparser.RawConfigParser()
    config.read(env.ODOO_RC)

    table = Table("property", "value", title="options")
    for ini_section in config.sections():
        for option in config.options(ini_section):
            table.add_row(option, config.get(ini_section, option))
    _odoo_internal.odoo.netsvc.init_logger()
    logging.getLogger("odoo").setLevel(logging.INFO)
    _logger.info("Init Logging for Odoo")
    return table


def init_folders(env: RunbotEnvironment) -> None:
    try:
        env.result_path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        if not env.result_path.exists():
            _logger.warning("Can't create folder %s", str(env.result_path))


def _db_exist(db_section: section.DatabaseOdooConfigSection) -> bool:
    """Args:
        db_section:

    Returns:

    """
    import psycopg2  # noqa: PLC0415
    from psycopg2 import sql  # noqa: PLC0415

    try:
        conn = psycopg2.connect(
            dbname=db_section.name,
            user=db_section.user,
            password=db_section.password,
            host=db_section.host,
            port=db_section.port,
        )
        with conn, conn.cursor() as curs:
            curs.execute(sql.SQL("SELECT 1;"))
            return True
    except psycopg2.OperationalError:
        return False
