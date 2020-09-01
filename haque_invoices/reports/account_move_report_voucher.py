# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AccountMoveReportVoucher(models.AbstractModel):
    _name = "report.haque_invoices.account_move_report_voucher"

    @api.model
    def _get_report_values(self, docids, data=None):
        moves = self.env["account.move"].browse(docids)

        inter_transfer_ids = []
        bank_payment_ids = []
        cash_payment_ids = []
        journal_ids = []
        checks = {}
        unposted_moves = moves.filtered(lambda m: m.state != "posted")
        if unposted_moves:
            raise ValidationError("Cannot print voucher for unposted entries: " + ", ".join(str(id) for id in unposted_moves.ids))
        for move in moves:
            matched_payment = self.env["account.payment"].search([("move_line_ids","in",move.line_ids.ids)], limit=1)
            if matched_payment:
                if matched_payment.payment_type == "transfer":
                    inter_transfer_ids.append(move.id)
                else:
                    if matched_payment.journal_id.type == "bank":
                        bank_payment_ids.append(move.id)
                    else:
                        cash_payment_ids.append(move.id)
                if matched_payment.check_number:
                    checks[move.id] = {
                        "number": matched_payment.check_number,
                        "date": matched_payment.payment_date,
                    }
            else:
                journal_ids.append(move.id)

        return {
            "doc_ids": docids,
            "doc_model": "account.move",
            "docs": moves,
            "inter_transfer_ids": inter_transfer_ids,
            "bank_payment_ids": bank_payment_ids,
            "cash_payment_ids": cash_payment_ids,
            "journal_ids": journal_ids,
            "checks": checks,
        }