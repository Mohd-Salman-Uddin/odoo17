from odoo import models, fields, api, _, Command
from datetime import datetime

class SchoolStudent(models.Model):
    _name = "school.student"
    _description = "Students Of My_School"
    _rec_name = "student_name"
    _inherit = [
        'mail.thread'
    ]

    student_id=fields.Many2one('school.student',string="Student ID")
    user_id = fields.Many2one('res.users',string="Username")
    student_name = fields.Char(string='Name')
    gender = fields.Selection([('Male','Male'),('Female','Female')],string='Gender')
    student_email = fields.Char(string="Student's Email", required=True, tracking=True)
    date_of_birth = fields.Date(string='Date Of Birth', tracking=True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True, readonly=True)
    address = fields.Char(string='Address', tracking=True)
    date_of_joining = fields.Date(string='Date Of Joining', tracking=True)
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
    guardian_name = fields.Char(string='Guardian Name', tracking=True)
    guardian_mobile = fields.Char(string='Guardian Mobile Number', size=15, tracking=True)
    guardian_email = fields.Char(string="Guardian's Email", tracking=True)
    select_status = fields.Selection([('not_selected', "Not Selected"),
                                      ('selected', "Selected")],
                                     default='not_selected', tracking=True,string = "Student Status")
    fee_structure_ids = fields.One2many('school.fee.structure','student_id', string='Fee Structure')
    total_amount = fields.Float(string="Total Amount", compute='_compute_total_amount', store=True ,readonly=True)
    untaxed_amount = fields.Float(string="Untaxed Amount", store=True,readonly=True)
    taxed_amount = fields.Float(string="Total tax Amount", store=True, readonly=True)
    invoice_count=fields.Integer(string='Invoice Count', compute='_compute_invoices_count')

    @api.depends('fee_structure_ids.total_amount','fee_structure_ids.amount')
    def _compute_total_amount(self):

        for rec in self:
            rec.total_amount = sum(i.total_amount for i in rec.fee_structure_ids)
            rec.untaxed_amount = sum(j.amount for j in rec.fee_structure_ids)
            rec.taxed_amount =  rec.total_amount - rec.untaxed_amount

    def action_select(self):
        self.select_status = "selected"
        template = self.env.ref('my_school.student_email_template')
        print("template :", template)
        for rec in self:
            template.send_mail(rec.id,force_send=True)
        user_vals = {
            'name': self.student_name,
            'login': self.student_email,
            'email': self.student_email,
            'password': self.student_name,
            'groups_id': [Command.set([self.env.ref('my_school.group_school_students').id])]
        }
        self.env['res.users'].create(user_vals)


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
    def _compute_invoices_count(self):
        self.invoice_count=self.env['account.move'].search_count(domain=[('partner_id','=',self.student_name),('move_type','=','out_invoice')])
    def action_open_invoices(self):
        print("Test in smart button")
        return {
            'name': 'Invoices',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain':[('partner_id','=',self.user_id.partner_id.id),('move_type','=','out_invoice')]
        }

    @api.model
    def _cron_fee_due_reminder(self):
        today = datetime.today().date()
        due_students = self.search([('fee_structure_ids.due_date', '=', today),'fee_structure_ids.status', '=', 'Unpaid'])
        for student in due_students:
            message = f"Fees For The Student {student.id} Is Pending.!"
            student.message_post(body=message)
            template = self.env.ref('my_school.fee_due_reminder_email_template')
            template.send_mail(student.id, force_send=True)
