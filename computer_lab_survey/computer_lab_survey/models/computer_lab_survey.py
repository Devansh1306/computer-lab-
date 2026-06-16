# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ComputerLabSurvey(models.Model):
    _name = 'computer.lab.survey'
    _description = 'Computer Lab Utilization Survey'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'lab_name'
    _order = 'week_start_date desc, id desc'

    # ─── Lab & Department Details ───────────────────────────────────────────────
    college = fields.Selection([
        ('eng_tech', 'College of Engineering & Technology'),
        ('cs_it', 'College of Computer Science & IT'),
        ('management', 'College of Management Studies'),
        ('pharmacy', 'College of Pharmacy'),
        ('science', 'College of Science'),
        ('architecture', 'College of Architecture & Design'),
        ('law', 'College of Law'),
        ('education', 'College of Education'),
        ('other', 'Other / Central University'),
    ], string='College / Institution', required=True, tracking=True)

    department = fields.Char(string='Department', required=True, tracking=True,
                              placeholder='e.g. Computer Science, MBA, BCA…')
    lab_name = fields.Char(string='Lab Name / Number', required=True, tracking=True,
                            placeholder='e.g. Lab 101, Programming Lab A…')
    num_desktops = fields.Integer(string='Number of Desktops', default=30,
                                   tracking=True)
    incharge_name = fields.Char(string='Lab In-charge Name', required=True, tracking=True)
    contact_info = fields.Char(string='Contact Email / Phone', required=True,
                                placeholder='email or mobile number')

    week_start_date = fields.Date(string='Week Start Date', required=True, tracking=True)
    week_end_date = fields.Date(string='Week End Date', required=True, tracking=True)
    academic_year = fields.Selection([
        ('2024_25', '2024–25'),
        ('2025_26', '2025–26'),
        ('2026_27', '2026–27'),
    ], string='Academic Year', default='2025_26', required=True)

    # ─── Slot Lines ──────────────────────────────────────────────────────────────
    slot_ids = fields.One2many('computer.lab.slot', 'survey_id', string='Weekly Slots')

    # ─── Availability & Notes ────────────────────────────────────────────────────
    sharable = fields.Selection([
        ('yes_all', 'Yes — all free slots available'),
        ('yes_some', 'Yes — some slots only (specify below)'),
        ('no', 'No — reserved for department use'),
        ('coordinator', 'To be decided by coordinator'),
    ], string='Free Slots Shareable?', tracking=True)

    booking_notice = fields.Selection([
        ('same_day', 'Same day'),
        ('1_day', '1 day prior'),
        ('2_3_days', '2–3 days prior'),
        ('1_week', '1 week prior'),
    ], string='Advance Booking Notice')

    special_conditions = fields.Text(string='Special Conditions / Restrictions',
                                      placeholder='e.g. Only after 4pm, no internet required, prior HOD approval needed…')
    infra_issues = fields.Text(string='Infrastructure Issues / Upgrade Requirements',
                                placeholder='e.g. 5 desktops non-functional, projector needs repair…')

    # ─── State ───────────────────────────────────────────────────────────────────
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
    ], string='Status', default='draft', tracking=True)

    # ─── Computed Stats ───────────────────────────────────────────────────────────
    total_slots = fields.Integer(string='Total Slots', compute='_compute_stats', store=True)
    filled_slots = fields.Integer(string='Filled Slots', compute='_compute_stats', store=True)
    free_slots = fields.Integer(string='Free Slots', compute='_compute_stats', store=True)
    utilization_pct = fields.Float(string='Utilization %', compute='_compute_stats', store=True)

    @api.depends('slot_ids', 'slot_ids.status')
    def _compute_stats(self):
        for rec in self:
            total = len(rec.slot_ids)
            filled = len(rec.slot_ids.filtered(lambda s: s.status not in ('free', 'maintenance')))
            free = len(rec.slot_ids.filtered(lambda s: s.status == 'free'))
            rec.total_slots = total
            rec.filled_slots = filled
            rec.free_slots = free
            rec.utilization_pct = round((filled / total * 100), 1) if total else 0.0

    # ─── Actions ─────────────────────────────────────────────────────────────────
    def action_submit(self):
        for rec in self:
            if not rec.slot_ids:
                raise ValidationError('Please add at least one slot before submitting.')
            rec.state = 'submitted'

    def action_review(self):
        self.write({'state': 'reviewed'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_generate_slots(self):
        """Auto-generate 25 slots (5 days × 5 time slots) for the survey."""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        slots = [
            '8:00 – 10:00 am',
            '10:00 am – 12:00 pm',
            '12:00 – 2:00 pm',
            '2:00 – 4:00 pm',
            '4:00 – 6:00 pm',
        ]
        for rec in self:
            if rec.slot_ids:
                rec.slot_ids.unlink()
            vals_list = []
            for day in days:
                for slot in slots:
                    vals_list.append({
                        'survey_id': rec.id,
                        'day': day,
                        'time_slot': slot,
                        'status': 'free',
                    })
            self.env['computer.lab.slot'].create(vals_list)

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record.action_generate_slots()
        return record
