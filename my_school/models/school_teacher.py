from odoo import models, fields, Command

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
            rec.message_post(body="An email has been sent to the student: %s" % rec.student_name)
        user_vals = {
            'name': self.name,
            'login': self.teacher_email,
            'email': self.teacher_email,
            'password': self.name,
            'groups_id': [Command.set([self.env.ref('my_school.group_school_students').id])]
        }
        self.env['res.users'].create(user_vals)

