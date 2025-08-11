import logging
import warnings

from odoo import models

_DEFAULT_LOGGER_NAME = __name__

logging.getLogger(_DEFAULT_LOGGER_NAME).warning("Runbot Test Warmup Warning")


class SimpleLogger(models.AbstractModel):
    _name = "runbot.logger"
    _description = "Logging Tester"

    def logger(self, logger_name=_DEFAULT_LOGGER_NAME):
        return logging.getLogger(logger_name)

    def do_pywarnings(self, msg, warning_type):
        warnings.warn(msg, warning_type, stacklevel=2)
