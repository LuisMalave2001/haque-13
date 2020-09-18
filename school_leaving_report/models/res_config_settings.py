# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    school_leaving_template = fields.Html(string="School Leaving Report Template",
        related="company_id.school_leaving_template",
        readonly=False)