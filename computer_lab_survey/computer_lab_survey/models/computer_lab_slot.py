# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ComputerLabSlot(models.Model):
    _name = 'computer.lab.slot'
    _description = 'Computer Lab Time Slot'
    _order = 'day_order, time_slot'

    survey_id = fields.Many2one('computer.lab.survey', string='Survey',
                                 required=True, ondelete='cascade')

    day = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
    ], string='Day', required=True)

    day_order = fields.Integer(compute='_compute_day_order', store=True)

    time_slot = fields.Selection([
        ('8:00 – 10:00 am', '8:00 – 10:00 am'),
        ('10:00 am – 12:00 pm', '10:00 am – 12:00 pm'),
        ('12:00 – 2:00 pm', '12:00 – 2:00 pm'),
        ('2:00 – 4:00 pm', '2:00 – 4:00 pm'),
        ('4:00 – 6:00 pm', '4:00 – 6:00 pm'),
    ], string='Time Slot', required=True)

    status = fields.Selection([
        ('free', 'Free / Available'),
        ('class', 'Scheduled Class'),
        ('exam', 'Exam / Practical'),
        ('workshop', 'Workshop / Event'),
        ('maintenance', 'Maintenance / Closed'),
    ], string='Status', default='free', required=True)

    # ─── Detail fields (for occupied slots) ─────────────────────────────────────
    course_subject = fields.Char(string='Course / Subject',
                                  placeholder='e.g. DBMS Lab, Python…')
    batch_class = fields.Char(string='Batch / Class',
                               placeholder='e.g. B.Tech 2nd yr A')
    student_count = fields.Integer(string='Student Count')

    # ─── Computed ────────────────────────────────────────────────────────────────
    is_occupied = fields.Boolean(compute='_compute_is_occupied', store=True)
    status_color = fields.Char(compute='_compute_status_color')

    @api.depends('day')
    def _compute_day_order(self):
        order_map = {'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5}
        for rec in self:
            rec.day_order = order_map.get(rec.day, 0)

    @api.depends('status')
    def _compute_is_occupied(self):
        for rec in self:
            rec.is_occupied = rec.status not in ('free', 'maintenance')

    def _compute_status_color(self):
        color_map = {
            'free': '#B4B2A9',
            'class': '#639922',
            'exam': '#185FA5',
            'workshop': '#854F0B',
            'maintenance': '#E24B4A',
        }
        for rec in self:
            rec.status_color = color_map.get(rec.status, '#B4B2A9')
