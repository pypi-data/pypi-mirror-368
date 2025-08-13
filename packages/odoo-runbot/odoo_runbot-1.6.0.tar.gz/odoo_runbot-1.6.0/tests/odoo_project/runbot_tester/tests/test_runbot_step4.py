from odoo.tests import common


class TestStep4(common.TransactionCase):
    def test_filter(self):
        # Step3 - Filter2 will capture this line but not Filter1 (no same logger name)
        base_msg = "My Warning message - in %s"
        self.env["runbot.logger"].logger(None).warning(base_msg, "root")
        self.env["runbot.logger"].logger("Custom.logger").warning(base_msg, "custom")
        self.env["runbot.logger"].logger("odoo.addons.base").warning(base_msg, "base")
