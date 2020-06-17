# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.constrains("amount_untaxed")
    def check_so_tax_exempt(self):
        for sale in self:
            if sale.company_id.so_tax_exempt and sale.amount_untaxed <= sale.company_id.so_tax_exempt_amount:
                for line in sale.order_line:
                    line.tax_id = [(5, 0 ,0)]
                sale._amount_all()