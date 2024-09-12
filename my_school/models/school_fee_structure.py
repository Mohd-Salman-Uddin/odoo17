from odoo import models, fields, api

class SchoolFeeStructure(models.Model):
    _name = "school.fee.structure"
    _description = "Fee Structure"
    _rec_name = 'tax'
    _inherit = ['mail.thread']

    fee_type = fields.Char(string="Fee Type", required=True)
    amount = fields.Float(string='Untaxed Amount', required=True, default=0.0, tracking=True)
    tax = fields.Many2many('account.tax', string="Tax")
    tax_amount = fields.Float(string='Tax Amount', compute='_compute_tax_amount', default=0.0, store=True)
    total_amount = fields.Float(string='Total', compute='_compute_total_amount', store=True)
    product_id=fields.Many2one('product.template',string="Product")

    @api.depends('amount', 'tax_amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = rec.amount + rec.tax_amount

    @api.depends('amount', 'tax')
    def _compute_tax_amount(self):
        for rec in self:
            total_tax_amount = 0.0
            if rec.tax:
                for tax in rec.tax:
                    total_tax_amount += (rec.amount * tax.amount / 100)
            rec.tax_amount = total_tax_amount

    @api.model
    def create(self, vals):
        # Call the super method to create the record first
        fee_structure = super(SchoolFeeStructure, self).create(vals)
        # Trigger the creation of the related product
        fee_structure.create_product()
        return fee_structure

    def create_product(self):
        self.env['product.template'].create({
            'name': self.fee_type,
            'detailed_type': 'service',
            'list_price' : self.amount,
            'taxes_id' : self.tax,
        })
        print('Product created')