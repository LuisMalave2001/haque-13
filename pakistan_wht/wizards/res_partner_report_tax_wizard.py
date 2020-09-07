# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartnerReportTaxWizard(models.TransientModel):
    _name = "res.partner.report.tax.wizard"
    _description = "Vendor Tax Report Wizard"

    start_date = fields.Date(string="Start Date",
        required=True,
        default=fields.Date.today())
    end_date = fields.Date(string="End Date",
        required=True,
        default=fields.Date.today())

    def action_confirm(self):
        datas = {
            "form": self.read()[0]
        }

        return self.env.ref("pakistan_wht.action_res_partner_report_tax").report_action([], data=datas)