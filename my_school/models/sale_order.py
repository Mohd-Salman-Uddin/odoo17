from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    guardian_name = fields.Char(string='Guardian Name')
    guardian_mobile = fields.Char(string='Guardian Number', size=15)
    bank_name=fields.Char(string="Bank Name")
    account_number=fields.Float(string="Account Number")
    ifsc_code=fields.Char(string="IFSC Code")
    branch=fields.Char(string="Branch")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    brand_ids=fields.Many2one('product.brand',string='Brand Name')
