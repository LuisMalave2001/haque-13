# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class AccountPaymentImport(models.Model):
    _name = "account.payment.import"
    _description = "Payment Import"

    transaction_date = fields.Date(string="Transaction Date",
        required=True)
    facts_id = fields.Char(string="Facts ID",
        required=True)
    student_name = fields.Char(string="Student Name")
    invoice_number = fields.Char(string="Invoice No",
        required=True)
    paypro_id = fields.Char(string="PayPro/Connect ID",
        required=True)
    amount = fields.Float(string="Amount")
    invoice_id = fields.Many2one(string="Invoice",
        comodel_name="account.move")
    payment_id = fields.Many2one(string="Payment",
        comodel_name="account.payment")
    error_msg = fields.Char(string="Error Msg")
    
    def create_payment(self, journal):
        move_obj = self.env["account.move"]
        payment_obj = self.env["account.payment"]

        for line in self.filtered(lambda l: not l.payment_id):
            matched_invoice = move_obj.search([
                ("name","like",line.invoice_number),
                ("type","=","out_invoice"),
                ("state","=","posted"),
                ("amount_residual",">",0.0)
            ])
            if not matched_invoice:
                line.error_msg = "No unpaid posted invoice found"
                continue
            elif len(matched_invoice) > 1:
                # filter by matching paypro id
                matched_invoice = matched_invoice.filtered(lambda i: i.student_id.paypro_id)
                if not matched_invoice:
                    line.error_msg = "No unpaid posted invoice found with matching student PayPro ID"
                    continue
                elif len(matched_invoice) > 1:
                    line.error_msg = "Multiple invoices matched"
                    continue
            line.error_msg = False
            defaults = payment_obj.with_context(active_ids=[matched_invoice.id], active_model="account.move").default_get([])
            defaults.update({
                "amount": line.amount,
                "journal_id": journal.id,
                "payment_date": line.transaction_date,
                "payment_method_id": journal.inbound_payment_method_ids[0].id,
            })
            payment = payment_obj.create(defaults)
            payment.post()
            line.invoice_id = matched_invoice.id
            line.payment_id = payment.id



