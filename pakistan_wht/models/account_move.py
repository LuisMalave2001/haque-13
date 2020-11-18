# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = "account.move"

    def create_wht_bil(self):
        if self.state =='posted' and not self.reversed_entry_id:
            move_data = {}
            cash_tax_journal_id = self.env.company.tax_cash_basis_journal_id
            tax_journal_id = self.env.company.tax_journal_id
            vendor_id = self.env.company.tax_collector_id
            product_id = self.env["product.product"].search([("name","ilike","WHT Payment")], limit=1)
            if not product_id:
                raise ValidationError(""" 
                    There's no Product defined as 'WHT Payment' in your product list. 
                    Please create one to automate the WHT bill. """)
            if not product_id.property_account_expense_id:
                raise ValidationError(" Please define an Expense account in your 'WHT Payment' product. ")

            tax_amount = 0
            origin_bill = ""
            
            # setting default account to be search
            transition_account_name = "Tax Payable"
            
            # getting the set transition account in account.tax
            for line in self.line_ids:
                transition_account = self.env["account.tax"].search([("name","=",line.name)])
                if transition_account:
                    transition_account_name = transition_account.cash_basis_transition_account_id.name
                    break

            for line in self.line_ids.filtered(lambda x: x.account_id.name == transition_account_name):
                tax_amount += line.debit
                origin_bill = line.name
                vendor_name = line.partner_id.name
            # will not create wht bill if the tax amount is zero
            if tax_amount > 0:
                bill_id = self.env["account.move"].sudo().create({
                        "type": "in_invoice",
                        "partner_id": vendor_id.id,
                        "journal_id": tax_journal_id.id,
                        "ref": "Tax Bill for "+ origin_bill +" (Journal Ref: "+ self.name +")",
                    })
                move_data.setdefault(bill_id.id, {})
                bill_line = self.env["account.move.line"].sudo().create({
                        "move_id":bill_id.id,
                        "product_id":product_id.id,
                        "account_id":product_id.property_account_expense_id.id,
                        "quantity": 1,
                    })
                bill_line._onchange_product_id()
                move_data[bill_id.id][bill_line.id] = {
                        "name": bill_line.name + " Bill Partner: "+ vendor_name+ "\n" + " (for " + origin_bill + ")",
                        "price_unit": tax_amount,
                    }
                for move_id, created_lines in move_data.items():
                    move = self.env["account.move"].browse(move_id)
                    invoice_line_ids = []
                    for line in move.invoice_line_ids:
                        if line.id in created_lines:
                            invoice_line_ids.append((1, line.id, created_lines[line.id]))
                        else:
                            invoice_line_ids.append((1, line.id, {
                                "name": line.name,
                                "account_id": line.account_id.id,
                            }))
                    move.sudo().write({"invoice_line_ids": invoice_line_ids})


    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)

        # Sends Notification to Accountants if their is new Bill in defined Tax Journal in Company settings 
        tax_journal_id = self.env.company.tax_journal_id
        if not tax_journal_id:
                raise ValidationError("No set Tax Journal in Company settings. Please define the journal for Automated WHT bill")
        if res.journal_id == tax_journal_id:
            activity_obj = self.env["mail.activity"]
            groups = self.env["res.groups"].search([("id","=",self.env.ref("account.group_account_invoice").id)])
            for user in groups.users:
                if user.id != self.env.ref("base.user_admin").id:
                    activity_obj.sudo().create({
                        "res_id": res.id,
                        "res_model_id": self.env['ir.model']._get('account.move').id,
                        "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                        "summary": "To Settle ",
                        "user_id": user.id,
                        "note": "Please confirm / post the created draft WHT Bill then settle the payment as soon as possible."
                    })
        return res