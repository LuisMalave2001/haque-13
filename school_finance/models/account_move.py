# -*- coding: utf-8 -*-

from odoo import fields, models

class Invoice(models.Model):
    _inherit = "account.move"

    partner_family_ids = fields.Many2many(related="partner_id.family_ids")
    family_members_ids = fields.Many2many(related="partner_family_ids.member_ids")

    student_id = fields.Many2one("res.partner", string="Student", domain=[('person_type', '=', 'student')])
    family_id = fields.Many2one("res.partner", string="Family")