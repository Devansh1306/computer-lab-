# -*- coding: utf-8 -*-
from odoo import models, fields


class DepartmentMaster(models.Model):
    _name = 'department.master'
    _description = 'Department Master'
    _order = 'institute_id, name'

    institute_id = fields.Many2one(
        'institute.master',
        string='Institute',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    
    name = fields.Char(string='Department Name', required=True, tracking=True)

    _sql_constraints = [
        ('institute_dept_unique', 'UNIQUE(institute_id, name)', 'Department name must be unique per institute!'),
    ]

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.name))
        return result
