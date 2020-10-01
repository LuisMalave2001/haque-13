# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    school_leaving_template = fields.Html(string="School Leaving Report Template")