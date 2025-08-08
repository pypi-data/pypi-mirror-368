# Copyright 2017 Creu Blanca <https://creublanca.es/>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import odoo
from odoo.tests import Form

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
from odoo.addons.point_of_sale.tests.common import TestPointOfSaleCommon


@odoo.tests.tagged("post_install", "-at_install")
class TestSessionPayInvoice(TestPointOfSaleCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.pos_config.cash_control = True
        cls.new_journal = cls.env["account.journal"].create(
            {
                "type": "cash",
                "name": "New Cash",
                "code": "NEWCASH",
                "company_id": cls.env.company.id,
            }
        )
        cls.journal_cash = cls.company_data["default_journal_cash"]
        cls.invoice_out = cls.env["account.move"].create(
            {
                "company_id": cls.company.id,
                "partner_id": cls.partner1.id,
                "date": "2016-03-12",
                "invoice_date": "2016-03-12",
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    odoo.Command.create(
                        {
                            "product_id": cls.product3.id,
                            "name": "Producto de prueba",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "tax_ids": [],
                        },
                    )
                ],
            }
        )
        cls.invoice_out.action_post()
        cls.invoice_in = cls.env["account.move"].create(
            {
                "partner_id": cls.partner4.id,
                "company_id": cls.company.id,
                "move_type": "in_invoice",
                "date": "2016-03-12",
                "invoice_date": "2016-03-12",
                "invoice_line_ids": [
                    odoo.Command.create(
                        {
                            "product_id": cls.product3.id,
                            "name": "Producto de prueba",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "tax_ids": [],
                        },
                    )
                ],
            }
        )
        cls.invoice_in.action_post()
        refund_wizard = (
            cls.env["account.move.reversal"]
            .with_context(
                active_ids=cls.invoice_out.ids,
                active_id=cls.invoice_out.id,
                active_model=cls.invoice_out._name,
            )
            .create({"journal_id": cls.invoice_out.journal_id.id})
            .reverse_moves()
        )
        cls.refund = cls.env[refund_wizard["res_model"]].browse(refund_wizard["res_id"])
        cls.refund.action_post()

    def test_pos_in_invoice(self):
        self.assertEqual(self.invoice_in.amount_residual, 100.0)
        self.pos_config._action_to_open_ui()
        session = self.pos_config.current_session_id
        self.assertTrue(session.cash_control)
        self.assertTrue(session.cash_journal_id)
        session.action_pos_session_open()
        wizard_context = session.button_show_wizard_pay_in_invoice()["context"]
        cash_in = self.env["cash.pay.invoice"].with_context(**wizard_context)
        with Form(cash_in) as form:
            form.journal_id = self.journal_cash
            form.invoice_id = self.invoice_in
            self.assertEqual(form.amount, -100)
        cash_in.browse(form.id).action_pay_invoice()
        session.action_pos_session_closing_control()
        session.invalidate_recordset()
        self.invoice_in.invalidate_recordset()
        self.invoice_in._compute_amount()
        self.assertEqual(self.invoice_in.amount_residual, 0.0)

    def test_pos_out_invoice(self):
        self.assertEqual(self.invoice_out.amount_residual, 100.0)
        self.pos_config._action_to_open_ui()
        session = self.pos_config.current_session_id
        wizard_context = session.button_show_wizard_pay_out_invoice()["context"]
        cash_out = self.env["cash.pay.invoice"].with_context(**wizard_context)
        with Form(cash_out) as form:
            form.journal_id = self.journal_cash
            form.invoice_id = self.invoice_out
            self.assertEqual(form.amount, 100)
            form.amount = 75
        cash_out.browse(form.id).action_pay_invoice()
        session.action_pos_session_closing_control()
        session.invalidate_recordset()
        self.invoice_out.invalidate_recordset()
        self.invoice_out._compute_amount()
        self.assertEqual(self.invoice_out.amount_residual, 25.0)

    def test_pos_invoice_refund(self):
        self.assertEqual(self.refund.amount_residual, 100.0)
        self.pos_config._action_to_open_ui()
        session = self.pos_config.current_session_id
        wizard_context = session.button_show_wizard_pay_out_refund()["context"]
        cash_out = self.env["cash.pay.invoice"].with_context(**wizard_context)
        with Form(cash_out) as form:
            form.journal_id = self.journal_cash
            form.invoice_id = self.refund
            self.assertEqual(form.amount, -100)
        cash_out.browse(form.id).action_pay_invoice()
        session.action_pos_session_closing_control()
        session.invalidate_recordset()
        self.invoice_out.invalidate_recordset()
        self.refund.invalidate_recordset()
        self.assertEqual(self.refund.amount_residual, 0.0)

    def test_journal_availables(self):
        """Test that only the journals of the POS session are available
        when the context pos_session_id is set.
        """
        self.pos_config.open_ui()
        pos_session = self.pos_config.current_session_id
        self.assertIn(
            self.journal_cash.id, pos_session.payment_method_ids.journal_id.ids
        )
        self.assertNotIn(
            self.new_journal.id, pos_session.payment_method_ids.journal_id.ids
        )
        # Without pos_session_id in the context, all cash journals are available.
        journals = self.env["account.journal"].name_search("Cash")
        journal_ids = [journal[0] for journal in journals]
        self.assertIn(self.new_journal.id, journal_ids)
        self.assertIn(self.journal_cash.id, journal_ids)
        # With pos_session_id in the context, only the journals of the session are available.
        journals = (
            self.env["account.journal"]
            .with_context(pos_session_id=pos_session.id)
            .name_search("Cash")
        )
        journal_ids = [journal[0] for journal in journals]
        self.assertNotIn(self.new_journal.id, journal_ids)
        self.assertIn(self.journal_cash.id, journal_ids)
