# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    def check_invoice_tax_exempt(self):
        for invoice in self.filtered(lambda r: r.type == "out_invoice"):
            invoice_date = invoice.invoice_date or fields.Date.context_today(self)
            fiscalyear_last_month = int(invoice.company_id.fiscalyear_last_month)
            fiscalyear_last_day = invoice.company_id.fiscalyear_last_day
            fiscalyear_end = invoice_date + relativedelta(month=fiscalyear_last_month, day=fiscalyear_last_day)
            if invoice_date.month > fiscalyear_last_month:
                fiscalyear_end += relativedelta(years=1)
            fiscalyear_start = fiscalyear_end + relativedelta(years=-1, days=1)
            covered_invoices = self.env["account.move"].search([
                ("partner_id","=",invoice.partner_id.id),
                ("type","in",["out_invoice","out_refund"]),
                ("state","in",["draft","posted"]),
                ("invoice_date",">=",fiscalyear_start),
                ("invoice_date","<=",fiscalyear_end),
                ("id","!=",invoice.id)
            ])
            total_invoiced_amount = sum(covered_invoices.mapped("amount_untaxed_signed"))
            remaining_months = (fiscalyear_end.year - invoice_date.year) * 12 + (fiscalyear_end.month - invoice_date.month + 1)
            forecasted_amount = total_invoiced_amount + remaining_months * invoice.amount_untaxed
            if invoice.company_id.so_tax_exempt and forecasted_amount <= invoice.company_id.so_tax_exempt_amount:
                for line in invoice.invoice_line_ids:
                    line.tax_ids = [(5, 0 ,0)]
            else:
                for line in invoice.invoice_line_ids:
                    line.tax_ids = line._get_computed_taxes()
            invoice._recompute_dynamic_lines(recompute_all_taxes=True)
            invoice._compute_amount()
            # invoice_line_ids = []
            # if invoice.company_id.so_tax_exempt and forecasted_amount <= invoice.company_id.so_tax_exempt_amount:
            #     for line in invoice.invoice_line_ids:
            #         invoice_line_ids.append((1, line.id, {
            #             "tax_ids": [(5, 0 ,0)]
            #         }))
            # else:
            #     for line in invoice.invoice_line_ids:
            #         invoice_line_ids.append((1, line.id, {
            #             "tax_ids": line._get_computed_taxes()
            #         }))
            # invoice.write({"invoice_line_ids": invoice_line_ids})