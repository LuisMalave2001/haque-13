# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class Invoice(models.Model):
    _inherit = "account.move"

    invoice_date_invalid = fields.Date(string="Invalid Date",
        compute="_compute_invoice_date_invalid",
        store=True,
        readonly=False)
    late_fee_amount = fields.Monetary(string="Late Fee Amount", store=True, compute="_compute_late_fee_amount")
    late_fee_was_applied = fields.Boolean(default=False)
    paypro_id = fields.Char(string="PayPro/Connect Pay ID",
        compute="_compute_paypro_id")
    fee_month = fields.Char(string="Fee Month",
        compute="_compute_fee_month")
    grade_level_id = fields.Many2one(string="Class",
        comodel_name="school_base.grade_level",
        related="student_id.grade_level_id")
    amount_before_due = fields.Monetary(string="Amount Before Due Date",
        compute="_compute_due_amounts")
    amount_after_due = fields.Monetary(string="Amount After Due Date",
        compute="_compute_due_amounts")
    student_facts_id = fields.Char(string="Student Fact ID",
        related="student_id.facts_id")
    voucher_number = fields.Char(string="Voucher #",
        readonly=True)
    fiscal_year = fields.Char(string="Fiscal Year",
        readonly=True)

    @api.depends('invoice_date', 'type')
    def _compute_late_fee_amount(self):
        for move_id in self:
            late_fee_amount = 0
            if move_id.type == 'out_invoice' and move_id.invoice_date:
                late_fee_amount_range_ids = move_id.journal_id.late_fee_amount_range_ids.filtered(lambda range_id: range_id.date_from <= move_id.invoice_date)
                if late_fee_amount_range_ids:
                    late_fee_amount = late_fee_amount_range_ids.sorted(key="date_from", reverse=True)[0].amount
                else:
                    late_fee_amount = move_id.journal_id.late_fee_amount_default or \
                                           move_id.company_id.late_fee_amount_default or 0.0

            move_id.late_fee_amount = late_fee_amount
    
    def _compute_paypro_id(self):
        for move in self:
            move.paypro_id = "%s%s" % (move.journal_id.paypro_prefix or "",
                                       move.student_facts_id or "")
    
    def _compute_fee_month(self):
        for move in self:
            move.fee_month = move.invoice_date and move.invoice_date.strftime("%b-%y") or False
    
    def _compute_due_amounts(self):
        late_fee_product = self.env.ref("haque_invoices.late_fee_product", raise_if_not_found=True)
        for move in self:
            matched = move.invoice_line_ids.filtered(lambda l: l.product_id.id == late_fee_product.product_variant_id.id)
            if matched:
                move.amount_before_due = move.amount_total - matched[0].price_total
                move.amount_after_due = move.amount_total
            else:
                move.amount_before_due = move.amount_total
                move.amount_after_due = move.amount_total + move.late_fee_amount

    @api.depends("invoice_date_due")
    def _compute_invoice_date_invalid(self):
        for invoice in self:
            result = False
            if invoice.invoice_date_due:
                result = invoice.invoice_date_due + relativedelta(weeks=1)
            invoice.invoice_date_invalid = result

    def cron_include_late_fees(self):
        now_date = datetime.now().date()
        overdue_invoices = self.sudo().search(
            [("invoice_date_due", "<", now_date),
             ("type", "=", "out_invoice"),
             ("invoice_payment_state", "!=", "paid"),
             ("late_fee_was_applied", "=", False)])

        late_fee_product_id = self.env.ref("haque_invoices.late_fee_product")

        late_fee_account_monthly_dict = {
            7: "211122",
            8: "211124",
            9: "211126",
            10: "211128",
            11: "211130",
            12: "211132",
            1: "211134",
            2: "211136",
            3: "211138",
            4: "211140",
            5: "211142",
            6: "211144",
        }

        account_code = late_fee_account_monthly_dict.get(now_date.month, False)
        late_fee_monthly_account_id = self.sudo().env["account.account"].search([("code", "=", account_code)])

        for invoice in overdue_invoices:
            invoice = invoice.sudo()

            if invoice.state == "posted":
                invoice.sudo().mapped('line_ids').remove_move_reconcile()
                invoice.sudo().write({'state': 'draft'})
            
            invoice.sudo().write({
                "invoice_line_ids": [(0, 0, {
                    "product_id": late_fee_product_id. get_single_product_variant().get("product_id", False),
                    "price_unit": invoice.late_fee_amount,
                    "account_id": late_fee_monthly_account_id.id,
                    "quantity": 1,
                    "tax_ids": late_fee_product_id.taxes_id.ids,
                })],
                "late_fee_was_applied": True
            })

            if invoice.state == "posted":
                invoice.sudo().post()
        _logger.info("Hola: ", self)

    def post(self):
        res = super(Invoice, self).post()
        self.assign_voucher_number()
        return res
    
    def assign_voucher_number(self):
        sequence_obj = self.env["ir.sequence"]
        for move in self.filtered(lambda m: not m.voucher_number and m.state == "posted"):
            fiscalyear_last_month = int(move.company_id.fiscalyear_last_month)
            move_month = move.date.month
            fiscalyear_year = move.company_id.compute_fiscalyear_dates(move.date)["date_to"].year
            fiscalyear_month = move_month - fiscalyear_last_month
            if fiscalyear_month < 0:
                fiscalyear_month = move_month + fiscalyear_last_month
            year_str = str(fiscalyear_year)
            month_str = str(fiscalyear_month).zfill(2)
            sequence_code = "account.move.voucher.{}.{}".format(year_str, month_str)
            code = sequence_obj.with_context(force_company=move.company_id.id).next_by_code(sequence_code)
            if not code:
                sequence = sequence_obj.sudo().create({
                    "name": "Voucher " + year_str + "-" + month_str,
                    "code": sequence_code,
                    "company_id": move.company_id.id,
                    "prefix": month_str + "-",
                    "padding": 3,
                    "number_increment": 1,
                    "number_next_actual": 1,
                })
                code = sequence.next_by_id()
            move.voucher_number = code
            move.fiscal_year = year_str