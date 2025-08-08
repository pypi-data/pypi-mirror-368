# Copyright 2017 Okia SPRL (https://okia.be)
# Copyright 2020 Tecnativa - Manuel Calero
# Copyright 2020 Tecnativa - João Marques
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re
from datetime import datetime

from dateutil import relativedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError
from odoo.tests import Form, RecordCapturer, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestCreditControlRunCase(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref(
            "account_credit_control.group_account_credit_control_manager"
        )
        journal = cls.company_data["default_journal_sale"]

        account = cls.env["account.account"].create(
            {
                "code": "TEST430001",
                "name": "Clients (test)",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        tag_operation = cls.env.ref("account.account_tag_operating")
        analytic_account = cls.env["account.account"].create(
            {
                "code": "TEST701001",
                "name": "Ventes en Belgique (test)",
                "account_type": "income",
                "reconcile": True,
                "tag_ids": [(6, 0, [tag_operation.id])],
            }
        )
        payment_term = cls.env.ref("account.account_payment_term_immediate")
        product = cls.env["product.product"].create({"name": "Product test"})
        cls.policy = cls.env.ref("account_credit_control.credit_control_3_time")
        cls.policy.write({"account_ids": [(6, 0, [account.id])]})

        # There is a bug with Odoo ...
        # The field "credit_policy_id" is considered as an "old field" and
        # the field property_account_receivable_id like a "new field"
        # The ORM will create the record with old field
        # and update the record with new fields.
        # However constrains are applied after the first creation.
        partner = cls.env["res.partner"].create(
            {"name": "Partner", "property_account_receivable_id": account.id}
        )
        partner.credit_policy_id = cls.policy.id
        date_invoice = datetime.today() - relativedelta.relativedelta(years=1)

        # Create an invoice
        invoice_form = Form(
            cls.env["account.move"].with_context(
                default_move_type="out_invoice", check_move_validity=False
            )
        )
        invoice_form.invoice_date = date_invoice
        invoice_form.invoice_date_due = date_invoice
        invoice_form.partner_id = partner
        invoice_form.journal_id = journal
        invoice_form.invoice_payment_term_id = payment_term
        with invoice_form.invoice_line_ids.new() as invoice_line_form:
            invoice_line_form.product_id = product
            invoice_line_form.quantity = 1
            invoice_line_form.price_unit = 500
            invoice_line_form.account_id = analytic_account
            invoice_line_form.tax_ids.clear()
        cls.invoice = invoice_form.save()
        cls.invoice.action_post()


@tagged("post_install", "-at_install")
class TestCreditControlRun(TestCreditControlRunCase):
    def test_check_run_date(self):
        """
        Create a control run older than the last control run
        """
        control_run = self.env["credit.control.run"].create(
            {"date": fields.Date.today(), "policy_ids": [(6, 0, [self.policy.id])]}
        )

        with self.assertRaises(UserError):
            today = datetime.today()
            previous_date = today - relativedelta.relativedelta(days=15)
            previous_date_str = fields.Date.to_string(previous_date)
            control_run._check_run_date(previous_date_str)

    def test_generate_credit_lines(self):
        """
        Test the method generate_credit_lines
        """
        self.env = self.env(
            context=dict(
                self.env.context,
                tracking_disable=False,
                mail_create_nosubscribe=False,
            )
        )
        control_run = self.env["credit.control.run"].create(
            {"date": fields.Date.today(), "policy_ids": [(6, 0, [self.policy.id])]}
        )
        extra_partner = self.env["res.partner"].create({"name": "Test extra partner"})
        self.invoice.partner_id.message_subscribe(
            partner_ids=extra_partner.ids,
            subtype_ids=self.env.ref(
                "account_credit_control.mt_credit_control_new"
            ).ids,
        )

        control_run.with_context(lang="en_US").generate_credit_lines()

        self.assertEqual(len(self.invoice.credit_control_line_ids), 1)
        self.assertEqual(control_run.state, "done")
        self.assertIn(
            extra_partner,
            self.invoice.credit_control_line_ids.message_follower_ids.mapped(
                "partner_id"
            ),
        )

        report_regex = (
            rf'Policy "<b>{self.policy.name}</b>" has generated <b>'
            r"\d+ Credit Control Lines.</b><br>"
        )
        regex_result = re.search(report_regex, control_run.report)
        self.assertIsNotNone(regex_result)

    def test_generate_credit_lines_with_max_level(self):
        """
        Test the method generate_credit_lines with max level group.
        For more than one invoice with date different due we need various credit control
        runs.
        """
        self.policy.apply_max_policy_level = True

        invoice1 = self.invoice.copy()
        invoice1.invoice_date = "2024-12-01"
        invoice1.invoice_date_due = "2024-12-01"
        invoice1.action_post()

        invoice2 = self.invoice.copy()
        invoice2.invoice_date = "2025-01-01"
        invoice2.invoice_date_due = "2025-01-01"
        invoice2.action_post()

        control_run = self.env["credit.control.run"].create(
            {"date": "2024-12-30", "policy_ids": [(6, 0, [self.policy.id])]}
        )
        control_run.with_context(lang="en_US").generate_credit_lines()
        control_run.set_to_ready_lines()
        # This module uses SQL queries to search records so we have to
        # store previous control lines
        self.env.cr.flush()

        control_run = self.env["credit.control.run"].create(
            {"date": "2025-01-30", "policy_ids": [(6, 0, [self.policy.id])]}
        )
        control_run.with_context(lang="en_US").generate_credit_lines()
        self.assertEqual(len(control_run.line_ids.mapped("level")), 3)
        # All control lines have the level 2
        self.assertEqual(set(control_run.line_ids.mapped("level")), {2})

    def test_multi_credit_control_run(self):
        """
        Generate several control run
        """

        six_months = datetime.today() - relativedelta.relativedelta(months=6)
        six_months_str = fields.Date.to_string(six_months)
        three_months = datetime.today() - relativedelta.relativedelta(months=2)
        three_months_str = fields.Date.to_string(three_months)

        # First run
        first_control_run = self.env["credit.control.run"].create(
            {"date": six_months_str, "policy_ids": [(6, 0, [self.policy.id])]}
        )
        first_control_run.with_context(lang="en_US").generate_credit_lines()
        self.assertEqual(len(self.invoice.credit_control_line_ids), 1)

        # Second run
        second_control_run = self.env["credit.control.run"].create(
            {"date": three_months_str, "policy_ids": [(6, 0, [self.policy.id])]}
        )
        second_control_run.with_context(lang="en_US").generate_credit_lines()
        self.assertEqual(len(self.invoice.credit_control_line_ids), 2)

        # Last run
        last_control_run = self.env["credit.control.run"].create(
            {"date": fields.Date.today(), "policy_ids": [(6, 0, [self.policy.id])]}
        )
        last_control_run.with_context(lang="en_US").generate_credit_lines()
        self.assertEqual(len(self.invoice.credit_control_line_ids), 3)

    def test_wiz_print_lines(self):
        """
        Test the wizard Credit Control Printer
        """
        control_run = self.env["credit.control.run"].create(
            {"date": fields.Date.today(), "policy_ids": [(6, 0, [self.policy.id])]}
        )

        control_run.with_context(lang="en_US").generate_credit_lines()

        self.assertTrue(len(self.invoice.credit_control_line_ids), 1)
        self.assertEqual(control_run.state, "done")

        report_regex = (
            rf'Policy "<b>{self.policy.name}</b>" has generated <b>'
            r"\d+ Credit Control Lines.</b><br>"
        )
        regex_result = re.search(report_regex, control_run.report)
        self.assertIsNotNone(regex_result)

        # Mark lines to be send
        control_lines = self.invoice.credit_control_line_ids
        marker = self.env["credit.control.marker"].create(
            {"name": "to_be_sent", "line_ids": [(6, 0, control_lines.ids)]}
        )
        marker.mark_lines()

        # Create wizard
        emailer_obj = self.env["credit.control.emailer"]
        wiz_emailer = emailer_obj.create({})
        wiz_emailer.line_ids = control_lines

        # Send email
        wiz_emailer.email_lines()

    def test_wiz_credit_control_emailer(self):
        """
        Test the wizard credit control emailer
        """
        control_run = self.env["credit.control.run"].create(
            {"date": fields.Date.today(), "policy_ids": [(6, 0, [self.policy.id])]}
        )

        control_run.with_context(lang="en_US").generate_credit_lines()

        self.assertTrue(len(self.invoice.credit_control_line_ids), 1)
        self.assertEqual(control_run.state, "done")

        report_regex = (
            rf'Policy "<b>{self.policy.name}</b>" has generated <b>'
            r"\d+ Credit Control Lines.</b><br>"
        )
        regex_result = re.search(report_regex, control_run.report)
        self.assertIsNotNone(regex_result)

        # Mark lines to be send
        control_lines = self.invoice.credit_control_line_ids
        marker = self.env["credit.control.marker"].create(
            {"name": "to_be_sent", "line_ids": [(6, 0, control_lines.ids)]}
        )
        marker.mark_lines()

        # Create wizard
        printer_obj = self.env["credit.control.printer"]
        wiz_printer = printer_obj.with_context(
            active_model="credit.control.line", active_ids=control_lines.ids
        ).create({})
        wiz_printer.print_lines()

    def test_sent_email_invoice_detail(self):
        """
        Verify that the email is sent and includes the invoice details
        """
        policy_level_expected = self.env.ref("account_credit_control.3_time_1")
        # assign a email to ensure does not fallback to letter
        self.invoice.partner_id.email = "test@test.com"
        control_run = self.env["credit.control.run"].create(
            {"date": fields.Date.today(), "policy_ids": [(6, 0, [self.policy.id])]}
        )
        control_run.with_context(lang="en_US").generate_credit_lines()
        self.assertTrue(len(self.invoice.credit_control_line_ids), 1)
        control_lines = self.invoice.credit_control_line_ids
        self.assertEqual(control_lines.policy_level_id, policy_level_expected)
        # CASE 1: set the policy level to show invoice details = True
        control_lines.policy_level_id.mail_show_invoice_detail = True
        marker = self.env["credit.control.marker"].create(
            {"name": "to_be_sent", "line_ids": [(6, 0, control_lines.ids)]}
        )
        marker.mark_lines()
        wiz_emailer = self.env["credit.control.emailer"].create({})
        wiz_emailer.line_ids = control_lines
        self.env.user.company_id.email = "test@example.com"
        with RecordCapturer(self.env["credit.control.communication"], []) as capture:
            wiz_emailer.with_context(queue_job__no_delay=True).email_lines()
        new_communication = capture.records
        self.assertEqual(len(new_communication), 1)
        self.assertEqual(len(new_communication.message_ids), 1)
        # Verify that the email include the invoice details.
        self.assertIn("Invoices summary", new_communication.message_ids.body)
        self.assertIn(self.invoice.name, new_communication.message_ids.body)

    def test_sent_email_no_invoice_detail(self):
        """
        Verify that the email is sent and does not include the invoice details
        """
        policy_level_expected = self.env.ref("account_credit_control.3_time_1")
        self.invoice.partner_id.email = "test@test.com"
        self.env.user.company_id.email = "test@example.com"
        control_run = self.env["credit.control.run"].create(
            {"date": fields.Date.today(), "policy_ids": [(6, 0, [self.policy.id])]}
        )
        control_run.with_context(lang="en_US").generate_credit_lines()
        self.assertTrue(len(self.invoice.credit_control_line_ids), 1)
        control_lines = self.invoice.credit_control_line_ids
        self.assertEqual(control_lines.policy_level_id, policy_level_expected)
        # CASE 2: set the policy level to show invoice details = False
        control_lines.policy_level_id.mail_show_invoice_detail = False
        marker = self.env["credit.control.marker"].create(
            {"name": "to_be_sent", "line_ids": [(6, 0, control_lines.ids)]}
        )
        marker.mark_lines()
        wiz_emailer = self.env["credit.control.emailer"].create({})
        wiz_emailer.line_ids = control_lines
        with RecordCapturer(self.env["credit.control.communication"], []) as capture:
            wiz_emailer.with_context(queue_job__no_delay=True).email_lines()
        new_communication = capture.records
        self.assertEqual(len(new_communication), 1)
        self.assertEqual(len(new_communication.message_ids), 1)
        # Verify that the email does not include the invoice details.
        self.assertNotIn("Invoices summary", new_communication.message_ids.body)
        self.assertNotIn(self.invoice.name, new_communication.message_ids.body)

    def test_open_credit_lines(self):
        """
        Test access rights when invoking method open_credit_lines
        """
        # Create credit lines
        control_run = self.env["credit.control.run"].create(
            {"date": fields.Date.today(), "policy_ids": [(6, 0, [self.policy.id])]}
        )
        control_run.with_context(lang="en_US").generate_credit_lines()
        self.assertEqual(len(self.invoice.credit_control_line_ids), 1)
        self.assertEqual(control_run.state, "done")

        # Set company_ids for user demo
        user_demo = self.env.ref("base.user_demo")
        user_demo.company_ids += control_run.company_id

        # User demo tries to read credit_control_line_action directly
        action_name = "account_credit_control.credit_control_line_action"
        action = self.env.ref(action_name)
        with self.assertRaises(AccessError):
            # AccessError raised
            action.with_user(user_demo.id).read()[0]

        # Invoking open_credit_lines: AccessError not raised
        action = control_run.with_user(user_demo.id).open_credit_lines()
        self.assertIn("domain", action)

    def test_open_credit_communications(self):
        """
        Test access rights when invoking method open_credit_communications
        """
        # Create credit lines
        control_run = self.env["credit.control.run"].create(
            {"date": fields.Date.today(), "policy_ids": [(6, 0, [self.policy.id])]}
        )
        control_run.with_context(lang="en_US").generate_credit_lines()
        self.assertEqual(len(self.invoice.credit_control_line_ids), 1)
        self.assertEqual(control_run.state, "done")

        # Set company_ids for user demo
        user_demo = self.env.ref("base.user_demo")
        user_demo.company_ids += control_run.company_id

        # User demo tries to read credit_control_communication_action directly
        action_name = "account_credit_control.credit_control_communication_action"
        action = self.env.ref(action_name)
        with self.assertRaises(AccessError):
            # AccessError raised
            action.with_user(user_demo.id).read()[0]

        # Invoking open_credit_communications: AccessError not raised
        action = control_run.with_user(user_demo.id).open_credit_communications()
        self.assertIn("domain", action)
