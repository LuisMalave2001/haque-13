# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    so_tax_exempt = fields.Boolean(string="SO Tax Exemption",
        default=False,
        help="Check to enable removing of taxes for an SO if forecasted year total is less than or equal a specified yearly amount")
    so_tax_exempt_amount = fields.Monetary(string="SO Tax Exemption Amount",
        default=200000,
        help="Taxes are removed for an SO if the forecasted year total is less or equal than this amount")