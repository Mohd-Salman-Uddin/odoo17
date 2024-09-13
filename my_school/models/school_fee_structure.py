from odoo import api, fields, models, _


class FeesStructure(models.Model):
    _name = "school.fee.structure"
    _description = "Fee Structure"
    _rec_name = "fee_type"
    _inherit = ['mail.thread']

    student_id = fields.Many2one(comodel_name="school.student", string="Student")
    product_id = fields.Many2one('product.template', string="Product")
    fee_type = fields.Selection(
        [('Tuition Fee', 'Tuition Fee'), ('Lab Fee', 'Lab Fee'), ('Exam Fee', 'Exam Fee'), ('Sport Fee', 'Sport Fee'),
         ('Transport Fee', 'Transport Fee'), ('Other Fee', 'Other Fee')], string="Fee Type")
    due_date = fields.Date(string='Due Date')
    amount = fields.Float(string='Untaxed Fee')
    status = fields.Selection([("Unpaid", "Unpaid"), ("Paid", "Paid")], default="Unpaid", compute='_compute_status_based_on_invoice')
    tax = fields.Many2many('account.tax', string="Tax")
    tax_amount = fields.Float(string='Tax Amount', compute='_compute_tax_amount', default=0.0, store=True)
    total_amount = fields.Float(string='Total', compute='_compute_total_amount', store=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)

    @api.onchange('product_id')
    def _fetch_values(self):
        print('Initiated')
        for rec in self:
            if rec.product_id:
                rec.fee_type = rec.product_id.name
                if rec.fee_type == 'Tuition Fee':
                    rec.amount = 35000
                elif rec.fee_type == 'Lab Fee':
                    rec.amount = 1200
                elif rec.fee_type == 'Exam Fee':
                    rec.amount = 1000
                elif rec.fee_type == 'Sport Fee':
                    rec.amount = 1000
                elif rec.fee_type == 'Transport Fee':
                    rec.amount = 5000
                elif rec.fee_type == 'Other Fee':
                    rec.amount = 0

    @api.depends('amount', 'tax')
    def _compute_tax_amount(self):
        for rec in self:
            total_tax_amount = 0.0
            if rec.tax:
                for tax in rec.tax:
                    total_tax_amount += (rec.amount * tax.amount / 100)
                rec.tax_amount = total_tax_amount
            else:
                rec.tax_amount = 0

    @api.depends('amount', 'tax_amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = rec.amount + rec.tax_amount

    def action_proceed_payment(self):
        self.ensure_one()

        # Check if an invoice already exists
        if self.invoice_id:
            # Redirect to the existing invoice
            return {
                'type': 'ir.actions.act_window',
                'name': _('Invoice'),
                'res_model': 'account.move',
                'res_id': self.invoice_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            # If no invoice exists, create a new one
            partner = self.env['res.partner'].search([('name', '=', self.student_id.student_name)], limit=1)
            invoice = self.env['account.move'].create({
                'partner_id': partner.id,
                'guardian_name': self.student_id.guardian_name,
                'guardian_mobile': self.student_id.guardian_mobile,
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, {
                    'product_id': self.product_id.id,
                    'fee_structure_id': self.id,
                    'name': 'Fee for %s' % self.fee_type,
                    'quantity': 1,
                    'price_unit': self.total_amount,
                    'tax_ids': [(6, 0, self.tax.ids)],
                })],
            })

            # Link the invoice to the fee structure
            self.invoice_id = invoice.id

            # Redirect to the newly created invoice
            return {
                'type': 'ir.actions.act_window',
                'name': _('Invoice'),
                'res_model': 'account.move',
                'res_id': invoice.id,
                'view_mode': 'form',
                'target': 'current',
            }

    def _compute_status_based_on_invoice(self):
        """ Compute the fee status based on invoice payment state """
        for rec in self:
            if rec.invoice_id:
                payment_state = rec.invoice_id.payment_state
                print(f"Invoice ID: {rec.invoice_id.id} - Payment State: {payment_state}")

                if payment_state == 'paid':
                    rec.status = 'Paid'
                else:
                    rec.status = 'Unpaid'
            else:
                rec.status = 'Unpaid'  # If no invoice yet
                print(f"No Invoice for record {rec.id}, setting status to Unpaid.")


