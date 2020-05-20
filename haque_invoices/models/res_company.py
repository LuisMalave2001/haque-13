# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = "res.company"

    main_account    = fields.Char(string='Main Account')
    deposit_account = fields.Char(string='Deposit Account')

    late_fee_amount_default = fields.Monetary(string='Late Fee amount', default=0)