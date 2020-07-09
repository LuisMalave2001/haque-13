# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    main_account = fields.Char(string='Main Account', default=lambda self: self.company_id.main_account)
    deposit_account = fields.Char(string='Deposit Account', default=lambda self: self.company_id.deposit_account)

    late_fee_amount_default = fields.Monetary(string='Late Fee amount')
    paypro_prefix = fields.Char(string="PayPro Prefix")