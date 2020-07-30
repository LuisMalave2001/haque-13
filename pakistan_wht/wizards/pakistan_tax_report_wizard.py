# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PakistanTaxReportWizard(models.TransientModel):
    _name = "pakistan.tax.report.wizard"

    start_date = fields.Date(string="Start Date",
        required=True)
    end_date = fields.Date(string="End Date",
        required=True)
    

    def action_confirm(self):
        datas = {
            "form": self.read()[0]
        }

        return self.env.ref("pakistan_wht.action_pakistan_tax_report").report_action([], data=datas)