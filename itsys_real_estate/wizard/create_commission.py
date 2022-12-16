# -*- coding: utf-8 -*-
from odoo import api, fields, models



class create_commission(models.TransientModel):
    _name = 'wiz.create.commission'
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        required=False)

    brokers = fields.Float( string=' وسطاء', )
    relations = fields.Float(string=' علاقات', )
    comp = fields.Float( string=' شركة', )
    credit_account_id = fields.Many2one(comodel_name='account.account',string=' Credit Account',)


    def create_move(self):
        contract = self.env['ownership.contract'].browse(self._context.get('active_ids'))
        lines=[]
        lines.append((0, 0,
                      {
                          'account_id': int(self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.brokers_account_id')),
                          'name': "Commission-"+contract.name,
                          'credit': 0,
                          'debit': self.brokers,
                      }
                      ))
        lines.append((0, 0,
                      {
                          'account_id': int(
                              self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.relations_account_id')),
                          'name': "Commission-"+contract.name,
                          'credit': 0,
                          'debit': self.relations,
                      }
                      ))
        lines.append((0, 0,
                      {
                          'account_id': int(
                              self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.comp_account_id')),
                          'name': "Commission-"+contract.name,
                          'credit': 0,
                          'debit': self.comp,
                      }
                      ))
        lines.append((0, 0,
                      {
                          'account_id':self.credit_account_id.id,
                          'name': "Commission-"+contract.name,
                          'credit': self.brokers+self.relations+self.comp,
                          'debit': 0,
                      }
                      ))

        new_move = self.env['account.move'].create({
            'journal_id': self.journal_id.id,
            'ref':   contract.name,
            'line_ids': lines,
            'commission_reservation_id': contract.id,
        })

