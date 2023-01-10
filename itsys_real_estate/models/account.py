# -*- coding: utf-8 -*-
from odoo import api, fields, models

class account_voucher(models.Model):
    _inherit = "account.payment"

    reservation_id=  fields.Many2one('unit.reservation','Reservation')
    real_estate_ref= fields.Char('Real Estate Ref.')
    ownership_line_id= fields.Many2one('loan.line.rs.own','Ownership Installment')
    rental_line_id= fields.Many2one('loan.line.rs.rent','Rental Contract Installment')

class account_move(models.Model):
    _inherit = "account.move"

    real_estate_ref = fields.Char('Real Estate Ref.')
    ownership_line_id = fields.Many2one('loan.line.rs.own', 'Ownership Installment')
    rental_line_id = fields.Many2one('loan.line.rs.rent', 'Rental Contract Installment')
    property_owner_id = fields.Many2one('res.partner', string="Owner")
    commission_reservation_id=  fields.Many2one('ownership.contract','Commission Ownership Contract')

    @api.depends('company_id', 'invoice_filter_type_domain')
    def _compute_suitable_journal_ids(self):
        for m in self:
            if m.move_type == 'entry':
                m.suitable_journal_ids = self.env['account.journal'].search([])
            else:
                journal_type = m.invoice_filter_type_domain or 'general'
                company_id = m.company_id.id or self.env.company.id
                domain = [('company_id', '=', company_id), ('type', '=', journal_type)]
                m.suitable_journal_ids = self.env['account.journal'].search(domain)


class account_move_line(models.Model):
    _inherit = "account.move.line"
    commissioned= fields.Boolean('Commissioned')

class account_journal(models.Model):
    _inherit = "account.journal"
    is_commission= fields.Boolean('Commission')