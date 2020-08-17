#-*- coding:utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    merge_product_ids = fields.Many2many(string="Merge with Products",
        comodel_name="product.product")
    merge_categ_ids = fields.Many2many(string="Merge with Categories",
        comodel_name="product.category")
