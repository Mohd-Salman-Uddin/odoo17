from odoo import api, models, fields
class StudentSuggestion(models.TransientModel):
    _name="student.suggestion"
    _description="Complaints Registered By Students"

    student_name=fields.Char(string='Name',readonly=True)
    standard = fields.Char(string='Standard',readonly=True)
    suggestion=fields.Text(string="Suggestion")

    @api.model
    def default_get(self,fields_list):
        res = super(StudentSuggestion,self).default_get(fields_list)
        context=self.env.context
        student_name=context.get('student_name')
        standard=context.get('standard')
        if student_name:
            res.update({
                'student_name':student_name,
                'standard': standard
            })
        return res

    def action_save(self):
        self.env['student.suggestions'].create({
            'student_name': self.student_name,
            'standard': self.standard,
            'suggestion': self.suggestion,
        })
        return {'type': 'ir.actions.act_window_close'}

