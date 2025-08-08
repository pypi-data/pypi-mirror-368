from odoo import api, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        if self.env.context.get("pos_session_id"):
            # Restrict to journals of the current POS session.
            session = self.env["pos.session"].browse(self.env.context["pos_session_id"])
            args = [("id", "in", session.payment_method_ids.journal_id.ids)]
        return super().name_search(name=name, args=args, operator=operator, limit=limit)
