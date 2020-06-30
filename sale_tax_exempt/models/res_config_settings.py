# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    so_tax_exempt = fields.Boolean(string="SO Tax Exemption",
        related="company_id.so_tax_exempt",
        readonly=False)
    so_tax_exempt_amount = fields.Monetary(string="SO Tax Exemption Amount",
        related="company_id.so_tax_exempt_amount",
        currency_field="company_currency_id",
        readonly=False)
    company_currency_id = fields.Many2one(string="Company Currency",
        comodel_name="res.currency",
        related="company_id.currency_id",
        readonly=True,
        help="Utility field to express amount currency")