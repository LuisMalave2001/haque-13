# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartnerReportTax(models.AbstractModel):
    _name = "report.pakistan_wht.res_partner_report_tax"
    _description = "Vendor Tax Report"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        start_date = data["form"]["start_date"]
        end_date = data["form"]["end_date"]
        styles = {
            "base_style": workbook.add_format({"text_wrap": True}),
            "header_bold_style": workbook.add_format({"text_wrap": True, "bold": True, "bg_color": "#e9ecef"}),
            "number_style": workbook.add_format({"num_format": "#,##"}),
        }
        sheet = workbook.add_worksheet("Tax Report")

        sheet.write(0, 0, "Payment Section", styles["header_bold_style"])
        sheet.write(0, 1, "TaxPayer_NTN", styles["header_bold_style"])
        sheet.write(0, 2, "TaxPayer_CNIC", styles["header_bold_style"])
        sheet.write(0, 3, "TaxPayer_Name", styles["header_bold_style"])
        sheet.write(0, 4, "TaxPayer_Business_Name", styles["header_bold_style"])
        sheet.write(0, 5, "Taxable_Amount", styles["header_bold_style"])
        sheet.write(0, 6, "Tax_Amount", styles["header_bold_style"])
        sheet.set_column(0, 0, 25)
        sheet.set_column(0, 1, 25)
        sheet.set_column(0, 2, 25)
        sheet.set_column(0, 3, 25)
        sheet.set_column(0, 4, 25)
        sheet.set_column(0, 5, 25)
        sheet.set_column(0, 6, 25)

        offset = 1
        partners = self.env["res.partner"].browse(self._context.get("active_ids"))
        for partner in partners:
            for rate in partner.tax_category_id.tax_rate_ids:
                sheet.write(offset, 0, rate.section_code)
                sheet.write(offset, 2, partner.vat)
                sheet.write(offset, 3, partner.name)
                sheet.write(offset, 4, partner.name)
                bills = self.env["account.move"].search([
                    ("type","in",["in_invoice","in_receipt"]),
                    ("state","in",["posted"]),
                    ("partner_id","=",partner.id),
                    ("invoice_date",">=",start_date),
                    ("invoice_date","<=",end_date)
                ])
                total_taxable = abs(sum(bills.mapped("amount_total_signed")))
                total_tax = abs(sum(bills.mapped("amount_tax_signed")))
                sheet.write(offset, 5, total_taxable, styles["number_style"])
                sheet.write(offset, 6, total_tax, styles["number_style"])
                offset += 1