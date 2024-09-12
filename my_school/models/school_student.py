import base64
from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta




class SchoolStudent(models.Model):
    _name = "school.student"
    _description = "Students Of My_School"
    _rec_name = "student_name"
    _inherit = [
        'mail.thread'
    ]

    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    student_id=fields.Many2one('school.student',string="Student ID")
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
    guardian_email = fields.Char(string="Guardian's Email", tracking=True)
    select_status = fields.Selection([('not_selected', "Not Selected"),
                                      ('selected', "Selected")],
                                     default='not_selected', tracking=True,string = "Student Status")
    fee_structure_ids = fields.Many2many('school.fee.structure', string='Fee Structure')
    total_amount = fields.Float(string="Total Amount", compute='_compute_total_amount', store=True ,readonly=True)
    untaxed_amount = fields.Float(string="Untaxed Amount", store=True,readonly=True)
    taxed_amount = fields.Float(string="Total tax Amount", store=True, readonly=True)
    status = fields.Selection([
        ('not_paid', 'Unpaid'),
        ('paid', 'Paid')
    ], string='Fee Payment',compute='_compute_payment_status', default='not_paid', tracking=True,readonly=True)

    @api.depends('invoice_id.payment_state')
    def _compute_payment_status(self):
        for rec in self:
            if rec.invoice_id and rec.invoice_id.payment_state == 'paid':
                rec.status = 'paid'
            else:
                rec.status = 'not_paid'

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

    def action_proceed_payment(self):
        print(self, "Button clicked")
        self.ensure_one()
        existing_invoice = self.env['account.move'].search([
            ('partner_id', '=', self.user_id.partner_id.id),
            ('move_type', '=', 'out_invoice'),
            ('state', 'in', ['draft', 'posted']),
            ('payment_state', '!=', 'paid')
        ], limit=1)

        if existing_invoice:
            raise UserError(_("An unpaid or draft invoice already exists for this student."))

        partner = self.env['res.partner'].search([('name', '=', self.student_name)], limit=1)
        # Prepare the invoice line items
        invoice_lines = []
        for fee_structure in self.fee_structure_ids:
            invoice_lines.append((0, 0, {
                'product_id':fee_structure.product_id.id,
            }))
        current_date = datetime.today().date()
        date_3_months_later = current_date + relativedelta(months=3)
        # Create the invoice
        invoice = self.env['account.move'].create({
            'partner_id': partner.id,
            'guardian_name': self.guardian_name,
            'guardian_mobile':self.guardian_mobile,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_date_due': date_3_months_later,
            'invoice_line_ids': invoice_lines,  # Add all invoice lines
        })
        # Link the invoice to the student
        self.invoice_id = invoice.id

        # Mark the fee as paid
        # self.status = 'paid'

        # Optionally, open the created invoice
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoice'),
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }

  # I Was Working On The Cron Job - Due Date Reminder
  #   @api.model
  #   def _cron_fee_due_reminder(self):
  #       current_date = datetime.today().date()
  #       date_3_months_later = current_date + relativedelta(months=3)
  #
  #       self.search([
  #           ('fee_structure_ids.date_due', '=', 'today'),
  #           ('fee_structure_ids.status', '=', 'not_paid')
  #        ])

    # Sample - Basic Cronjob Testing Message
    #
    #
    #     for student in students_due:
    #         message=f"Fees For The Student {student.id} Is Pending"
    #         student.message_post(body=message)
    #         print(student)
    #     print(students_due,' : abc')

        # template = self.env.ref('my_school.fee_due_reminder_email_template')
        #
        # for student in students_due:
        #     if student:
        #         # Prepare the email for the guardian
        #         template.send_mail(student.id, force_send=True)




