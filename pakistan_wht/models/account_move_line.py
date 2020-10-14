# -*- coding: utf-8 -*-

from odoo import api, fields, models

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_computed_taxes(self):
        self.ensure_one()
        tax_ids = super(AccountMoveLine, self)._get_computed_taxes()
        if self.move_id.partner_id.sale_status_wht_id in [False, "filler"] and self.move_id.is_sale_document(include_receipts=True):
            tax_ids = False
        return tax_ids
