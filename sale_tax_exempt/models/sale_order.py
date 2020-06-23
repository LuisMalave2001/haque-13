# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.constrains("amount_untaxed")
    def check_so_tax_exempt(self):
        for sale in self:
            today = fields.Date.context_today(self)
            fiscalyear_end = today + relativedelta(month=int(sale.company_id.fiscalyear_last_month), day=sale.company_id.fiscalyear_last_day)
            fiscalyear_start = fiscalyear_end + relativedelta(years=-1, days=1)
            covered_invoices = self.env["account.move"].search([
                ("partner_id","=",sale.partner_id.id),
                ("type","=","out_invoice"),
                ("state","in",["draft","posted"]),
                ("invoice_date",">=",fiscalyear_start),
                ("invoice_date","<=",fiscalyear_end),
            ])
            total_invoiced_amount = sum(covered_invoices.mapped("amount_untaxed_signed"))
            remaining_months = (fiscalyear_end.year - today.year) * 12 + (fiscalyear_end.month - today.month + 1)
            forecasted_amount = total_invoiced_amount + remaining_months * sale.amount_untaxed
            if sale.company_id.so_tax_exempt and forecasted_amount <= sale.company_id.so_tax_exempt_amount:
                for line in sale.order_line:
                    line.tax_id = [(5, 0 ,0)]
                sale._amount_all()