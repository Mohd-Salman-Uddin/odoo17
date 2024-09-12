from odoo import models, fields
from datetime import datetime
from odoo.exceptions import ValidationError

class SchoolQuery(models.Model):
    _name = "school.query"
    _description = "Queries Of My_School"
    _rec_name = "student_name"
    _inherit = [
        'mail.thread'
    ]

    student_email = fields.Char(string="Student's Email", required=True, tracking=True)
    student_name = fields.Char(string='Student Name', tracking=True)
    date_of_birth = fields.Date(string='Date Of Birth', tracking=True)
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
    ], string='Standard', tracking=True)
    status = fields.Selection([('Draft', 'Draft'), ('Admitted', 'Admitted'), ('Closed', 'Closed')], default='Draft')
    guardian_name = fields.Char(string='Guardian Name', tracking=True)
    guardian_mobile = fields.Char(string='Guardian Number', size=15, tracking=True)
    query_date = fields.Date(string='Date Of Query', default=fields.Date.today, tracking=True)
    query_description = fields.Text(string='Description', tracking=True)

    def status_closed(self):
        for rec in self:
            if rec.status != 'Closed':
                rec.status = 'Closed'

    def student_creation(self):
        student = self.env['school.student'].search(
            [('student_name', '=', self.student_name), ('guardian_name', '=', self.guardian_name),
             ('guardian_mobile', '=', self.guardian_mobile)])
        if student:
            raise ValidationError("The Student Data Already Exists.!")
        for rec in self:
            if rec.status == 'Draft':
                rec.status = 'Admitted'
        date_of_joining = datetime.today()
        student = self.env['school.student'].create({
            'student_name': self.student_name,
            'standard': self.standard,
            'student_email': self.student_email,
            'date_of_birth': self.date_of_birth,
            'guardian_name': self.guardian_name,
            'guardian_mobile': self.guardian_mobile,
            'date_of_joining': date_of_joining,
        })
