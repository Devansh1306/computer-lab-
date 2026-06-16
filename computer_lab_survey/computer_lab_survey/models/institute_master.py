# -*- coding: utf-8 -*-
from odoo import models, fields, api


class InstituteMaster(models.Model):
    _name = 'institute.master'
    _description = 'Institute Master'
    _order = 'code'

    code = fields.Char(string='Institute Code', required=True, unique=True, tracking=True)
    name = fields.Char(string='Institute Name', required=True, tracking=True)
    
    department_ids = fields.One2many(
        'department.master',
        'institute_id',
        string='Departments'
    )

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Institute Code must be unique!'),
    ]

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, f"{rec.code} - {rec.name}"))
        return result
