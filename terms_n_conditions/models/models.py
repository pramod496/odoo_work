from odoo import fields, models, api, _


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    terms_condition = fields.Many2one('terms.condition',string='Terms and Conditions')
    descr_terms_condition = fields.Text(string='Description')

    @api.onchange('terms_condition')
    def _onchange_terms_condition(self):
        values = {
            "descr_terms_condition": self.terms_condition.description_terms
        }
        self.update(values)


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    terms_condition = fields.Many2one('terms.condition', string='Terms and Conditions')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        values = {
            'note': self.partner_id.terms_condition.description_terms,
            'terms_condition': self.partner_id.terms_condition
        }
        self.update(values)

    @api.model
    def create(self, vals):
        if vals.get('origin'):
            if vals.get('origin').startswith('SQ'):
                sq = self.env['sale.order'].search([('name','=',vals.get('origin'))])
                vals['terms_condition'] = sq.terms_condition.id
        return super(SaleOrderInherit, self).create(vals)


class AccountInvoiceInherit(models.Model):
    _inherit = 'account.move'

    terms_condition = fields.Many2one('terms.condition',string='Terms and Conditions')

    @api.onchange('partner_id')
    def _onchange_partner_id_account(self):
        values = {
            "comment_proforma": self.partner_id.terms_condition.description_terms,
            "terms_condition": self.partner_id.terms_condition
        }
        self.update(values)


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    terms_condition = fields.Many2one('terms.condition',string='Terms and Conditions')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        values = {
            "notes": self.partner_id.terms_condition.description_terms,
            "terms_condition": self.partner_id.terms_condition
        }
        self.update(values)


class TermsAndCondition(models.Model):
    _name = 'terms.condition'

    name = fields.Char(string='Name')
    description_terms = fields.Text(string='Description')