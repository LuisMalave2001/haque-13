# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    tax_collector_id = fields.Many2one(comodel_name="res.partner", 
        string="Tax Authority Institution")
    tax_journal_id = fields.Many2one(comodel_name="account.journal", 
        string="Tax Journal")