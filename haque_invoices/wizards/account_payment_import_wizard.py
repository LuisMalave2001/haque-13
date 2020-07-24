# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPaymentImportWizard(models.TransientModel):
    _name = "account.payment.import.wizard"

    journal_id = fields.Many2one(string="Journal",
        comodel_name="account.journal",
        required=True)
    
    def action_confirm(self):
        self.ensure_one()
        active_ids = self.env.context.get("active_ids")
        lines = self.env["account.payment.import"].browse(active_ids)
        lines.create_payment(self.journal_id)