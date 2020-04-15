# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    journal_id = fields.Many2one("account.journal", string="Journal")
