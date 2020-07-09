# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False):
        res = self.env["account.move"]
        for order in self:
            order.check_so_tax_exempt()
            res |= super(SaleOrder, order)._create_invoices(grouped, final)
        return res

    @api.constrains("amount_untaxed", "invoice_date")
    def check_so_tax_exempt(self):
        for sale in self:
            invoice_date = sale.invoice_date and sale.invoice_date.date() or fields.Date.context_today(self)
            fiscalyear_last_month = int(sale.company_id.fiscalyear_last_month)
            fiscalyear_last_day = sale.company_id.fiscalyear_last_day
            fiscalyear_end = invoice_date + relativedelta(month=fiscalyear_last_month, day=fiscalyear_last_day)
            if invoice_date.month > fiscalyear_last_month:
                fiscalyear_end += relativedelta(years=1)
            fiscalyear_start = fiscalyear_end + relativedelta(years=-1, days=1)
            covered_invoices = self.env["account.move"].search([
                ("partner_id","=",sale.partner_id.id),
                ("type","in",["out_invoice","out_refund"]),
                ("state","in",["draft","posted"]),
                ("invoice_date",">=",fiscalyear_start),
                ("invoice_date","<=",fiscalyear_end),
            ])
            total_invoiced_amount = sum(covered_invoices.mapped("amount_untaxed_signed"))
            remaining_months = (fiscalyear_end.year - invoice_date.year) * 12 + (fiscalyear_end.month - invoice_date.month + 1)
            forecasted_amount = total_invoiced_amount + remaining_months * sale.amount_untaxed
            if sale.company_id.so_tax_exempt and forecasted_amount <= sale.company_id.so_tax_exempt_amount:
                for line in sale.order_line:
                    line.tax_id = [(5, 0 ,0)]
            else:
                sale._compute_tax_id()
            amount_untaxed = amount_tax = 0.0
            for line in sale.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            sale.amount_tax = amount_tax
            sale.amount_total = amount_untaxed + amount_tax
