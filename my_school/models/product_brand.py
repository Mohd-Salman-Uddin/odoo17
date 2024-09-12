from odoo import fields, models

class ProductBrand(models.Model):
    _name='product.brand'
    _rec_name = 'brand_name'
    brand_name=fields.Char(string='Brand Name')


class ProductBrandInTemplate(models.Model):
    _inherit='product.template'
    brand_ids=fields.Many2one('product.brand',string='Brand Name')
#
# class ProductBrandInProduct(models.Model):
#     _inherit='product.product'
#     brand_ids=fields.Many2one('product.brand',string='Brand Name')