# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    so_tax_exempt = fields.Boolean(string="SO Tax Exemption",
        default=False,
        help="Check to enable removing of taxes if SO untaxed amount is less than or equal a specific amount")
    so_tax_exempt_amount = fields.Monetary(string="SO Tax Exemption Amount",
        default=10000,
        help="Taxes are removed if SO untaxed amount is less than or equal this amount")