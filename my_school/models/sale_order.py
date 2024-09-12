from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    guardian_name = fields.Char(string='Guardian Name')
    guardian_mobile = fields.Char(string='Guardian Number', size=15)
