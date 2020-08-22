#-*- coding:utf-8 -*-

from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    merge_product_id = fields.Many2one(string="Merge With",
        comodel_name="product.product")

    @api.onchange("product_id")
    def _compute_merge_product_id(self):
        for line in self:
            if line.product_id:
                matched = False
                order_lines = line.order_id.order_line.filtered(lambda l: l.product_id != line.product_id)
                if line.product_id.merge_product_ids:
                    for order_line in order_lines:
                        if order_line.product_id in line.product_id.merge_product_ids:
                            line.merge_product_id = order_line.product_id.id
                            matched = True
                            break
                if not matched and line.product_id.merge_categ_ids:
                    for order_line in order_lines:
                        if order_line.product_id.categ_id in line.product_id.merge_categ_ids:
                            line.merge_product_id = order_line.product_id.id
                            matched = True
                            break
                if not matched and len(line.product_id.merge_product_ids) == 1:
                    line.merge_product_id = line.product_id.merge_product_ids
    
    def _prepare_invoice_line(self):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        res["merge_product_id"] = self.merge_product_id.id
        return res