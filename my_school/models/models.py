# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command
from datetime import datetime
from odoo.exceptions import ValidationError


class SchoolStudent(models.Model):
    _name = "school.student"
    _description = "Students Of My_School"
    _rec_name = "student_name"
    _inherit = [
        'mail.thread'
    ]
    user_id = fields.Many2one('res.users',string="Username")
    student_email = fields.Char(string="Student's Email", required=True, tracking=True)
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
    ], string='Standard', tracking=True)
    teacher_id = fields.Many2one(comodel_name='school.teacher', string='Class Teacher')
    teacher_mob_num = fields.Char(string="Teacher No.")
    teachers_ids = fields.Many2many("school.teacher", string="Teachers Appointed")
    date_of_birth = fields.Date(string='Date Of Birth', tracking=True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True, readonly=True)
    address = fields.Char(string='Address', tracking=True)
    date_of_joining = fields.Date(string='Date Of Joining', tracking=True)
    guardian_name = fields.Char(string='Guardian Name', tracking=True)
    guardian_mobile = fields.Char(string='Guardian Mobile Number', size=15, tracking=True)
    select_status = fields.Selection([('not_selected', "Not Selected"),
                                      ('selected', "Selected")],
                                     default='not_selected', tracking=True,string = "Student Status")

    fee_structure_ids = fields.One2many('school.fee.structure', 'student_id', string='Fee Structure', tracking=True)
    total_amount = fields.Float(string="Total Amount", compute='_compute_total_amount', store=True ,readonly=True)
    untaxed_amount = fields.Float(string="Untaxed Amount", store=True,readonly=True)
    taxed_amount = fields.Float(string="Total tax Amount", store=True, readonly=True)

    @api.depends('fee_structure_ids.total_amount','fee_structure_ids.amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(i.total_amount for i in rec.fee_structure_ids)
            rec.untaxed_amount = sum(j.amount for j in rec.fee_structure_ids)
            rec.taxed_amount =  rec.total_amount - rec.untaxed_amount

    def action_select(self):
        self.select_status = "selected"

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

    def action_suggest(self):
        return {
            'name': _('Suggestion Panel'),
            'view_mode': 'form',
            'res_model': 'student.suggestion',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context' : {
            'student_name': self.student_name,
            'standard':self.standard
        }
        }

    def action_create_student_user(self):

        template = self.env.ref('my_school.student_email_template'
        print("template :", template)
        for rec in self:
            template.send_mail(rec.id,force_send=True)
            rec.message_post(body="An email has been sent to the student: %s" % rec.student_name)
        user_vals = {
            'name': self.student_name,
            'login': self.student_email,
            'email': self.student_email,
            'password': self.student_name,
            'groups_id': [Command.set([self.env.ref('my_school.group_school_students').id])]
        }
        self.env['res.users'].create(user_vals)

    suggestion_count = fields.Integer(string="Suggestion Count", compute='compute_suggestion')
    def compute_suggestion(self):
        for rec in self:
            suggestion_count = self.env['student.suggestions'].search_count([('student_name', "=", rec.student_name)])
            rec.suggestion_count = suggestion_count

    def action_open_suggestions(self):
        print("Test in smart button")
        return {
            'name': 'Suggestions',
            'view_mode': 'tree,form',
            'res_model': 'student.suggestions',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain':[('student_name','=',self.student_name)]
        }


class SchoolTeacher(models.Model):
    _name = "school.teacher"
    _description = "Teachers Of My_School"
    _inherit = [
        'mail.thread'
    ]

    user_id = fields.Many2one('res.users', string="Username")
    name = fields.Char(string='Name', required=True, tracking=True)
    teacher_email=fields.Char(string="Teacher's Email", required=True, tracking=True)
    date_of_joining = fields.Date(string='Date Of Joining', tracking=True)
    address = fields.Char(string='Address', tracking=True)
    mobile = fields.Char(string='Mobile Number', size=15, tracking=True)
    date_of_birth = fields.Date(string='Date Of Birth', tracking=True)
    is_class_teacher = fields.Boolean(string='Class Teacher', tracking=True)
    teacher_selection_status = fields.Selection([('temporary', "Temporary"),
                                      ('permanent', "Permanent")],
                                     default='temporary')

    # One2many relationship to link to students
    student_ids = fields.One2many(comodel_name='school.student', inverse_name='teacher_id', string='Students',
                                  tracking=True)
    def action_teacher_selection(self):
        self.teacher_selection_status = "permanent"

    def action_create_teacher_user(self):

        template = self.env.ref('my_school.teacher_email_template')
        for rec in self:
            template.send_mail(rec.id,force_send=True)
            rec.message_post(body="An email has been sent to the student: %s" % rec.name)
        user_vals = {
            'name': self.name,
            'login': self.teacher_email,
            'email': self.teacher_email,
            'password': self.name,
            'groups_id': [Command.set([self.env.ref('my_school.group_school_students').id])]
        }
        self.env['res.users'].create(user_vals)


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


class SchoolFeeStructure(models.Model):
    _name = "school.fee.structure"
    _description = "Fee Structure"
    _rec_name = 'tax'
    _inherit = [
        'mail.thread'
    ]

    tax_amount=fields.Float(string='Tax Amount',compute='_compute_tax_amount', default=0.0, store=True)
    tax=fields.Many2many('account.tax',string="Tax")
    student_id = fields.Many2one('school.student', string='Student', tracking=True)
    student_name = fields.Char(related='student_id.student_name', string='Student Name', tracking=True)
    fee_type = fields.Selection([
        ('tuition', 'Tuition Fee'),
        ('lab', 'Lab Fee'),
        ('sports', 'Sports Fee'),
        ('other', 'Other Fee')
    ], string='Fee Type', required=True, tracking=True)
    amount = fields.Float(string='Untaxed Amount', required=True, default=0.0, tracking=True)
    date_due = fields.Date(string='Due Date', required=True, tracking=True)
    status = fields.Selection([
        ('not_paid', 'Unpaid'),
        ('paid', 'Paid')
    ], string='Status', default='not_paid', tracking=True)
    total_amount=fields.Float(string='Total',compute='_compute_total_amount', store=True)

    @api.depends('amount','tax_amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount= rec.amount + rec.tax_amount

    @api.depends('amount','tax')
    def _compute_tax_amount(self):
        for rec in self:
            total_tax_amount=0.0
            if rec.tax:
                for tax in rec.tax:
                    total_tax_amount+= (rec.amount*tax.amount/100)
                rec.tax_amount=total_tax_amount
            else:
                rec.tax_amount = 0

    def action_set_paid(self):
        for record in self:
            if record.status == 'not_paid':
                record.status = 'paid'


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    guardian_name = fields.Char(string='Guardian Name')
    guardian_mobile = fields.Char(string='Guardian Number', size=15)


class InvoiceOrder(models.Model):
    _inherit = 'account.move'

    guardian_name = fields.Char(string='Guardian Name')
    guardian_mobile = fields.Char(string='Guardian Number', size=15)


class InvoiceOrderFee(models.Model):
    _inherit = 'account.move.line'
    fee_structure_id = fields.Many2one('school.fee.structure', string='Fee Structure')


class StudentSuggestions(models.Model):
    _name = 'student.suggestions'
    _description = 'Suggestions/Complaints Received From Students'
    _rec_name = 'student_name'

    student_name = fields.Char(string='Name')
    standard = fields.Char(string='Standard')
    suggestion = fields.Text(string="Suggestion/Complaint")
    user_id = fields.Many2one('res.users', string='Submitted By', default=lambda self: self.env.user)
