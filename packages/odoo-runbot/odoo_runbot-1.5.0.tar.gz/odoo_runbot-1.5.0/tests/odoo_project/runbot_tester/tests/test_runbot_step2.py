import logging

import odoo
from odoo.tests import common
from odoo.tools.misc import mute_logger


class TestStep2(common.TransactionCase):
    """
    Test log capturing and py.warnings capturing in unitest don't need to be captured by step filter
    """

    # In Odoo prior to 15, the complete name of the logger is required
    @mute_logger("odoo.addons.runbot_tester.models.runbot_tester")
    def test_logger1(self):
        """
        Assert `odoo.tools.misc.mute_logger` catch all log line
        If not, the step should failed, because no step filter are avaliable
        """
        self.env["runbot.logger"].logger().info("My info message")
        self.env["runbot.logger"].logger().warning("My warning message")
        self.env["runbot.logger"].logger().critical("My critical message")
        self.env["runbot.logger"].logger().error("My error message")
        self.assertTrue(True, "Dummy assert to be sure this test is passed")

    def test_logger2(self):
        """
        Test when self.assertLogs() is used, you don't need to add a regex on the runbot
        We test with root logger, custom non exitant logger, and classic logger
        Test [unitest.assertLogs][] work as expected
        """
        with self.assertLogs() as logs:
            self.env["runbot.logger"].logger(logger_name=None).warning("My %s", "message1")
        self.assertEqual(logs.output, ["WARNING:root:My message1"])

        with self.assertLogs("odoo.addons.runbot_tester.models.runbot_tester") as l2:
            self.env["runbot.logger"].logger().error("My message2")
        self.assertEqual(l2.output, ["ERROR:odoo.addons.runbot_tester.models.runbot_tester:My message2"])

        with self.assertLogs("custom.logger") as l3:
            self.env["runbot.logger"].logger("custom.logger").critical("My message3")
        self.assertEqual(l3.output, ["CRITICAL:custom.logger:My message3"])

    def test_logger3(self):
        """
        Log message with allowed level in runbot
        - INFO
        - DEBUG
        - RUNBOT (level added by Odoo in test mode)
        """
        self.env["runbot.logger"].logger().info("message INFO")
        self.env["runbot.logger"].logger().debug("message DEBUG")
        if odoo.release.version >= "14.0":
            # Logger level RUNBOT activated in odoo 14 and more
            self.env["runbot.logger"].logger().log(logging.RUNBOT, "message RUNBOT")

    def test_logger4(self):
        """
        Assert you don't need to add a warning-filter on your runbot.step if you do the filtering in your test.
        Test [unitest.assertWarnsRegex][] and [unittest.assertWarns][] works as expected
        """
        with self.assertWarnsRegex(DeprecationWarning, expected_regex="This is depreca.*"):
            self.env["runbot.logger"].do_pywarnings("This is deprecated", DeprecationWarning)
        with self.assertWarns(BytesWarning):
            self.env["runbot.logger"].do_pywarnings("This is deprecated", BytesWarning)
