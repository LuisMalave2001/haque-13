# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class Invoice(models.Model):
    _inherit = "account.move"

    invoice_date_invalid = fields.Date("Invalid Date")
    late_fee_amount = fields.Monetary()
    late_fee_was_applied = fields.Boolean(default=False)

    @api.model
    def _default_late_fee_amount(self):
        company_late_fee = self.company_id.late_fee_amount_default
        journal_late_fee = self.journal_id.late_fee_amount_default

        return journal_late_fee if journal_late_fee else company_late_fee

    @api.model
    def create(self, vals):
        vals["late_fee_was_applied"] = False
        record_ids = super(Invoice, self).create(vals)
        for record in record_ids:

            company_late_fee = record.company_id.late_fee_amount_default
            journal_late_fee = record.journal_id.late_fee_amount_default

            late_fee = journal_late_fee if journal_late_fee else company_late_fee

            record.write({
                "late_fee_amount": late_fee
            })

        return record_ids

    def cron_include_late_fees(self):
        now_date = datetime.now().date()
        overdue_invoices = self.sudo().search(
            [("invoice_date_due", "<", now_date),
             ("type", "=", "out_invoice"),
             ("invoice_payment_state", "!=", "paid"),
             ("late_fee_was_applied", "=", False)])

        late_fee_product_id = self.env.ref("haque_invoices.late_fee_product")

        late_fee_account_monthly_dict = {
            7: "211122",
            8: "211124",
            9: "211126",
            10: "211128",
            11: "211130",
            12: "211132",
            1: "211134",
            2: "211136",
            3: "211138",
            4: "211140",
            5: "211142",
            6: "211144",
        }

        account_code = late_fee_account_monthly_dict.get(now_date.month, False)
        late_fee_monthly_account_id = self.sudo().env["account.account"].search([("code", "=", account_code)])

        for invoice in overdue_invoices:
            invoice = invoice.sudo()

            if invoice.state == "posted":
                invoice.sudo().mapped('line_ids').remove_move_reconcile()
                invoice.sudo().write({'state': 'draft'})
            
            invoice.sudo().write({
                "invoice_line_ids": [(0, 0, {
                    "product_id": late_fee_product_id. get_single_product_variant().get("product_id", False),
                    "price_unit": invoice.late_fee_amount,
                    "account_id": late_fee_monthly_account_id.id,
                    "quantity": 1,
                    "tax_ids": late_fee_product_id.taxes_id.ids,
                })],
                "late_fee_was_applied": True
            })

            if invoice.state == "posted":
                invoice.sudo().post()
        _logger.info("Hola: ", self)
