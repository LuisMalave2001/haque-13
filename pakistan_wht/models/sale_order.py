# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.constrains("partner_id")
    def check_partner_tax_exempt(self):
        for sale in self:
            if sale.partner_id.sale_status_wht_id == "filler":
                for line in sale.order_line:
                    line.tax_id = [(5, 0, 0)]
                sale._amount_all()