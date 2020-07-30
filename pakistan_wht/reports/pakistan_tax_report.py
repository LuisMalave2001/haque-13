# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from datetime import timedelta
from dateutil import tz


class PakistanTaxReport(models.AbstractModel):
    _name = "report.pakistan_wht.pakistan_tax_report"
    _inherit = 'report.report_xlsx.abstract'

    def _get_invoices(self, from_date, to_date):
        self.env.cr.execute("""
                SELECT id FROM account_move 
                WHERE state = 'posted' AND type = 'out_invoice' AND invoice_payment_state = 'paid' 
                AND invoice_date BETWEEN '%(from_date)s' AND '%(to_date)s'
            """ % {"from_date": from_date, "to_date": to_date})
        res = [x[0] for x in self.env.cr.fetchall()]
        return res

    def _get_payment_lines(self, invoice):
        self.env.cr.execute("""
                SELECT id FROM account_payment 
                WHERE state NOT IN ('draft', 'cancel') AND partner_type = 'customer' 
                AND communication =  '%(invoice)s' 
                ORDER BY payment_date ASC
            """ % {"invoice": invoice})
        res = [x[0] for x in self.env.cr.fetchall()]
        return res

    def generate_xlsx_report(self, workbook, data, lines):
        start_date = data["form"]["start_date"]
        end_date = data["form"]["end_date"]
        payment = self.env["account.payment"]
        invoice = self.env["account.move"]
        header_format = workbook.add_format({"font_size":14, "align": "vcenter", "bold": True})
        data_format = workbook.add_format({"font_size":12, "align": "vcenter", "bold": False})
        number_format = workbook.add_format({'num_format': '#,##0.00'})
        sheet = workbook.add_worksheet("Tax Report")
        invoices_ids = self._get_invoices(start_date, end_date)
        invoices = invoice.browse(invoices_ids)

        # sheet.write(0, 0, "No.", header_format)
        sheet.write(0, 0, "Customer Tax ID", header_format)
        sheet.write(0, 1, "Customer Name", header_format)
        sheet.write(0, 2, "Date Paid", header_format)
        sheet.write(0, 3, "Untaxed Amount", header_format)
        sheet.write(0, 4, "Tax Amount", header_format)
        sheet.write(0, 5, "Total Paid", header_format)
        # sheet.write(0, 7, "Status", header_format)

        # row = 1
        # for invoice in invoices:
        #     sheet.write(row, 0, row, data_format)
        #     row += 1
        
        row = 1
        for invoice in invoices:
            sheet.write(row, 0, invoice.partner_id.vat, data_format)
            row += 1

        row = 1
        for invoice in invoices:
            sheet.write(row, 1, invoice.partner_id.name, data_format)
            row += 1

        row = 1  
        for invoice in invoices:
            payment_ids = self._get_payment_lines(invoice.name)
            if payment_ids:
                last_payment = payment_ids[-1]
                last_payment_id = payment.browse(last_payment)
                sheet.write(row, 2, last_payment_id.payment_date.strftime("%m/%d/%Y"), data_format)
            row += 1

        row = 1
        for invoice in invoices:
            sheet.write(row, 3, invoice.amount_untaxed, number_format)
            row += 1
        
        row = 1
        for invoice in invoices:
            sheet.write(row, 4, invoice.amount_tax_signed, number_format)
            row += 1
        
        row = 1
        for invoice in invoices:
            payment_ids = self._get_payment_lines(invoice.name)
            payments = payment.browse(payment_ids)
            total = 0
            for payment in payments:
                total += float(payment.amount)
            sheet.write(row, 5, total, number_format)
            row += 1
