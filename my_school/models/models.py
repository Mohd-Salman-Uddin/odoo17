# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class SchoolStudent(models.Model):
    _name = "school.student"
    _description = "Students Of My_School"
    _rec_name = "student_name"

    student_name = fields.Char(string='Name')
    standard = fields.Selection([
        ('First', 'First'),
        ('Second', 'Second'),
        ('Third', 'Third'),
        ('Fourth', 'Fourth'),
        ('Fifth', 'Fifth'),
        ('Sixth', 'Sixth'),
        ('Seventh', 'Seventh'),
        ('Eighth', 'Eighth'),
        ('Ninth', 'Ninth'),
        ('Tenth', 'Tenth')
    ], string='Standard')
    teacher_id = fields.Many2one(comodel_name='school.teacher', string='Class Teacher')
    teacher_mob_num = fields.Char(string="Teacher No.")
    teachers = fields.Many2many("school.teacher", string="Teachers Appointed")
    date_of_birth = fields.Date(string='Date Of Birth')
    age = fields.Integer(string='Age', compute='_compute_age', store=True, readonly=True)
    address = fields.Char(string='Address')
    date_of_joining = fields.Date(string='Date Of Joining')
    guardian_name = fields.Char(string='Guardian Name')
    guardian_mobile = fields.Char(string='Guardian Mobile Number', size=15)

    fee_structure_ids = fields.One2many('school.fee.structure', 'student_id', string='Fee Structure')

    @api.depends('date_of_birth')
    def _compute_age(self):
        today = datetime.today()
        for rec in self:
            if rec.date_of_birth:
                dob = fields.Date.from_string(rec.date_of_birth)
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                rec.age = age
            else:
                rec.age = 0

    @api.onchange('teacher_id')
    def _onchange_teacher_id(self):
        if self.teacher_id:
            self.teacher_mob_num = self.teacher_id.mobile


class SchoolTeacher(models.Model):
    _name = "school.teacher"
    _description = "Teachers Of My_School"

    name = fields.Char(string='Name', required=True)
    date_of_joining = fields.Date(string='Date Of Joining')
    address = fields.Char(string='Address')
    mobile = fields.Char(string='Mobile Number', size=15)
    date_of_birth = fields.Date(string='Date Of Birth')
    is_class_teacher = fields.Boolean(string='Class Teacher')

    # One2many relationship to link to students
    student_ids = fields.One2many(comodel_name='school.student', inverse_name='teacher_id', string='Students')


class SchoolQuery(models.Model):
    _name = "school.query"
    _description = "Queries Of My_School"
    _rec_name = "student_name"

    student_name = fields.Char(string='Student Name')
    standard = fields.Selection([
        ('First', 'First'),
        ('Second', 'Second'),
        ('Third', 'Third'),
        ('Fourth', 'Fourth'),
        ('Fifth', 'Fifth'),
        ('Sixth', 'Sixth'),
        ('Seventh', 'Seventh'),
        ('Eighth', 'Eighth'),
        ('Ninth', 'Ninth'),
        ('Tenth', 'Tenth')
    ], string='Standard')
    guardian_name = fields.Char(string='Guardian Name')
    guardian_mobile = fields.Char(string='Guardian Number', size=15)
    query_date = fields.Date(string='Date', default=fields.Date.today)
    query_description = fields.Text(string='Description')

    def student_creation(self):
        student = self.env['school.student'].create({
            'student_name': self.student_name,
            'standard' : self.standard,
            'guardian_name' : self.guardian_name,
            'guardian_mobile' : self.guardian_mobile,
        })

class SchoolFeeStructure(models.Model):
    _name = "school.fee.structure"
    _description = "Fee Structure"
    _rec_name = 'student_id'


    student_id = fields.Many2one('school.student', string='Student')
    student_name = fields.Char(related='student_id.student_name', string='Student Name')
    fee_type = fields.Selection([
        ('tuition', 'Tuition Fee'),
        ('lab', 'Lab Fee'),
        ('sports', 'Sports Fee'),
        ('other', 'Other Fee')
    ], string='Fee Type', required=True)
    amount = fields.Float(string='Amount', required=True, default=0.0)
    date_due = fields.Date(string='Due Date', required=True)
    status = fields.Selection([
        ('not_paid', 'Unpaid'),
        ('paid', 'Paid')
    ], string='Status', default='not_paid')

    def action_set_paid(self):
        for record in self:
            if record.status == 'not_paid':
                record.status = 'paid'