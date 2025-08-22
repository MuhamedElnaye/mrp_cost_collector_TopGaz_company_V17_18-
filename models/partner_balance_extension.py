from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    balance = fields.Monetary(string='Balance', compute='_compute_balance', currency_field='currency_id')

    def _compute_balance(self):
        # نجيب حسابات المقبوضات والمدفوعات
        account_ids = self.env['account.account'].search([
            ('account_type', 'in', ['asset_receivable', 'liability_payable'])
        ]).ids

        for partner in self:
            lines = self.env['account.move.line'].search([
                ('partner_id', '=', partner.id),
                ('account_id', 'in', account_ids),
                ('move_id.state', '=', 'posted'),
            ])
            partner.balance = sum(lines.mapped('amount_residual'))

    balance_display = fields.Char(string='Balance', compute='_compute_balance_display')

    @api.depends('balance')
    def _compute_balance_display(self):
        for rec in self:
            rec.balance_display = f"{rec.balance:.2f} EGP"