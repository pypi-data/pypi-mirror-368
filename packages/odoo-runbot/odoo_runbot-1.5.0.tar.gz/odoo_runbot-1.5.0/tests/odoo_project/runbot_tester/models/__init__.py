import logging

_logger = logging.getLogger(__name__)
try:
    from odoo import models

    from . import runbot_tester
except ImportError:
    _logger.error("Please install odoo to use runbot tester")
