#-*- coding:utf-8 -*-

from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    merge_product_id = fields.Many2one(string="Merge With",
        comodel_name="product.product")

    @api.onchange("product_id")
    def _compute_merge_product_id(self):
        for line in self:
            if line.product_id:
                matched = False
                invoice_lines = line.move_id.invoice_line_ids.filtered(lambda l: l.product_id != line.product_id)
                if line.product_id.merge_product_ids:
                    for invoice_line in invoice_lines:
                        if invoice_line.product_id in line.product_id.merge_product_ids:
                            line.merge_product_id = invoice_line.product_id.id
                            matched = True
                            break
                if not matched and line.product_id.merge_categ_ids:
                    for invoice_line in invoice_lines:
                        if invoice_line.product_id.categ_id in line.product_id.merge_categ_ids:
                            line.merge_product_id = invoice_line.product_id.id
                            matched = True
                            break
                if not matched and len(line.product_id.merge_product_ids) == 1:
                    line.merge_product_id = line.product_id.merge_product_ids