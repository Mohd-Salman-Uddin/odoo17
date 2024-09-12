from odoo import api, fields, models

class InvoicingOrder(models.Model):
    _inherit = "account.move"

    guardian_name=fields.Char(string="Guardian Name") #adding a text field into sale.order from here
    guardian_mobile=fields.Char(string="Guardian Number")


class ProductOrder(models.Model):
    _inherit = "account.move.line"

    fee_structure_id = fields.Many2one('school.fee.structure', string='Fee Structure')