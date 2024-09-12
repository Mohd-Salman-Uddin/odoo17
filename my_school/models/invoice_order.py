from odoo import models, fields

class InvoiceOrder(models.Model):
    _inherit = 'account.move'

    guardian_name = fields.Char(string='Guardian Name')
    guardian_mobile = fields.Char(string='Guardian Number', size=15)

class InvoiceOrderFee(models.Model):
    _inherit = 'account.move.line'
    fee_structure_id = fields.Many2one('school.fee.structure', string='Fee Structure')