# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class JournalLateFeeRange(models.Model):

    _name = "haque_invoices.journal_late_fee_range"

    journal_id = fields.Many2one("account.journal")
    currency_id = fields.Many2one("res.currency", related="journal_id.currency_id")

    date_from = fields.Date("Date")
    amount = fields.Monetary("Amount")
