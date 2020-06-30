# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

class SaleOrderForStudents(models.Model):
    _inherit = "sale.order"

    invoice_date_due = fields.Date()
    invoice_date_invalid = fields.Date(string="Invoice Date Invalid"
        compute="_compute_invoice_date_invalid",
        store=True,
        readonly=False)
    late_fee_amount = fields.Monetary(string="Late Fee Amount",
        compute="_compute_late_fee_amount")
    journal_id = fields.Many2one("account.journal", string="Journal", domain="[('type', '=', 'sale')]")

    def _create_invoices(self, grouped=False, final=False):
        all_moves = super()._create_invoices(grouped, final)
        for order in self:
            order.invoice_ids.write({
                "invoice_date_invalid": order.invoice_date_invalid,
                "invoice_date_due": order.invoice_date_due,
            })
        return all_moves
    
    def _compute_late_fee_amount(self):
        for order in self:
            order.late_fee_amount = order.journal_id.late_fee_amount_default or \
                                    order.company_id.late_fee_amount_default or 0.0
    
    @api.depends("invoice_date_due")
    def _compute_invoice_date_invalid(self):
        for order in self:
            result = False
            if order.invoice_date_due:
                result = order.invoice_date_due + relativedelta(weeks=1)
            order.invoice_date_invalid = result
