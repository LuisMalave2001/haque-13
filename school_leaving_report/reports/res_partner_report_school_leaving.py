# -*- coding: utf-8 -*-

from datetime import date, datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError, MissingError
from odoo.tools.misc import formatLang, format_date, format_datetime

class ResPartnerReportSchoolLeaving(models.AbstractModel):
    _name = "report.school_leaving_report.res_partner_report_school_leaving"

    @api.model
    def _get_report_values(self, docids, data=None):
        partner_obj = self.env["res.partner"]
        student_ids = self.env.context.get("active_ids", [])
        students = partner_obj.browse(student_ids or docids)

        template = self.env.company.school_leaving_template
        if not template:
            raise MissingError("School Leaving Report Template is empty.")

        contents = {}
        for student in students:
            vals = {
                "date_today": fields.Date.context_today(self),
            }
            student_vals = student.read()[0]
            for key, value in student_vals.items():
                vals["student_" + key] = value
            parent = student.family_ids.member_ids.filtered(lambda m: m.person_type == "parent")
            if parent:
                parent_vals = parent[0].read()[0]
                for key, value in parent_vals.items():
                    vals["parent_" + key] = value
            if student.grade_level_id:
                grade_level_vals = student.grade_level_id.read()[0]
                for key, value in grade_level_vals.items():
                    vals["grade_level_" + key] = value
            for key, value in vals.items():
                new_value = str(value)
                if isinstance(value, date):
                    new_value = format_date(self.env, value)
                elif isinstance(value, datetime):
                    new_value = format_datetime(self.env, value)
                vals[key] = new_value
            try:
                contents[student.id] = template % vals
            except:
                raise ValidationError("An error has occurred while formatting the school leaving report template.")

        return {
            "doc_ids": student_ids,
            "doc_model": "res.partner",
            "docs": students,
            "contents": contents,
        }