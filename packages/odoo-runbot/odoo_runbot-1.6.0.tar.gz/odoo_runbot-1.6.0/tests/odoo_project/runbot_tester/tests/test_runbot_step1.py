from odoo.tests import common


class TestStep1(common.TransactionCase):
    """
    A simple to ensure odoo demo data are loaded
    Odoo can't run test without demo, but we have a warmup step (install this module without test-enable)
    So we ensure that odoo demo data are loaded even without test-enable
    """

    def test_step1(self):
        self.assertTrue(self.env.ref("base.user_demo"), "Big trouble, no demo data in your database ?")
