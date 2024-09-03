from odoo import api, models, fields
class StudentSuggestion(models.TransientModel):
    _name="student.suggestion"
    _description="Complaints Registered By Students"

    student_name=fields.Many2one('school.student', string='Name')
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
    suggestion=fields.Text(string="Suggestion")

    def action_save(self):
        self.env['student.suggestions'].create({
            'student_name': self.student_name.id,
            'standard': self.standard,
            'suggestion': self.suggestion,
        })
        return {'type': 'ir.actions.act_window_close'}

