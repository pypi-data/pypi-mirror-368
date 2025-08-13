import logging

from odoo.tests import common


class TestStep3(common.TransactionCase):
    def test_filter(self):
        """
        Test the filter of the Step3.
        This filter should capturing the log with the default name of the model `runbot.logger`
        -> `odoo.addons.runbot_tester.models.runbot_tester` it's a child of `odoo.addons.runbot_tester`

        """
        # Step3 - Filter1 should capture this line
        self.env["runbot.logger"].logger().warning("My Warning Filter1")
        print(logging.root.handlers)
        print(logging.root.handlers[0].filters)
        print(logging.root.handlers[1].filters)
        # In this level this should be ok
        # Even if the message match
        self.env["runbot.logger"].logger().info("My Warning Filter1")
