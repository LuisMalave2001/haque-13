# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_tax_id(self):
        super(SaleOrderLine, self)._compute_tax_id()
        for line in self:
            if line.order_id.partner_id.sale_status_wht_id == "filler":
                line.tax_id = [(5, 0, 0)]