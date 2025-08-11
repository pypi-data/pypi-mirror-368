from odoo.tests import common


class TestStep6(common.TransactionCase):
    def test_simple_filter(self):
        self.env["runbot.logger"].logger("odoo.addons.base").warning("message for %s", "step6")
