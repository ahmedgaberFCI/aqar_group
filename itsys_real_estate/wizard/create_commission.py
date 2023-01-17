# -*- coding: utf-8 -*-
from odoo import api, fields, models



class create_commission(models.TransientModel):
    _name = 'wiz.create.commission'
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        required=False)

    brokers = fields.Float( string=' وسطاء', )
    brokers_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')],)

    relations = fields.Float(string=' علاقات', )
    relations_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')],)
    comp = fields.Float( string=' شركة', )
    comp_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')],)

    credit_account_id = fields.Many2one(comodel_name='account.account',string=' Credit Account',)


    def create_move(self):
        contract = self.env['ownership.contract'].browse(self._context.get('active_ids'))
        brokers=self.brokers if self.brokers_type == 'amount' else (contract.pricing) * (self.brokers / 100)
        relations=self.relations if self.relations_type == 'amount' else (contract.pricing) * (self.relations / 100)
        comp=self.comp if self.comp_type == 'amount' else (contract.pricing) * (self.comp / 100)
        lines=[]
        lines.append((0, 0,
                      {
                          'account_id': int(self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.brokers_account_id')),
                          'name': "Commission-"+contract.name,
                          'credit': 0,
                          'debit': brokers,
                      }
                      ))
        lines.append((0, 0,
                      {
                          'account_id': int(
                              self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.relations_account_id')),
                          'name': "Commission-"+contract.name,
                          'credit': 0,
                          'debit': relations,


                      }
                      ))
        lines.append((0, 0,
                      {
                          'account_id': int(
                              self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.comp_account_id')),
                          'name': "Commission-"+contract.name,
                          'credit': 0,
                          'debit': comp,

                      }
                      ))
        lines.append((0, 0,
                      {
                          'account_id':self.credit_account_id.id,
                          'name': "Commission-"+contract.name,
                          'credit': brokers+relations+comp,
                          'debit': 0,
                      }
                      ))

        new_move = self.env['account.move'].create({
            'journal_id': self.journal_id.id,
            'ref':   contract.name,
            'line_ids': lines,
            'commission_reservation_id': contract.id,
        })

