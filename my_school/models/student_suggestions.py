from odoo import models, fields

class StudentSuggestions(models.Model):
    _name = 'student.suggestions'
    _description = 'Suggestions/Complaints Received From Students'
    _rec_name = 'student_name'

    student_name = fields.Char(string='Name')
    standard = fields.Char(string='Standard')
    suggestion = fields.Text(string="Suggestion/Complaint")
    user_id = fields.Many2one('res.users', string='Submitted By', default=lambda self: self.env.user)
