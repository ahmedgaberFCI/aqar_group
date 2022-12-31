# -*- coding: utf-8 -*-
from odoo import api, fields, models



class create_accrual(models.TransientModel):
    _name = 'wiz.create.accrual'
    partner_id = fields.Many2one(string='Vendor', required=True, readonly=False, comodel_name='project.project')
    date = fields.Date(string='Date', required=True, readonly=False)
    construction_id = fields.Many2one(string='Construction', copy=False, required=False, readonly=False,
                                      comodel_name='aqar.construction')
    lines = fields.One2many(
        comodel_name='wiz.create.accrual.lines',
        inverse_name='wiz_id',
        string='Lines',
        required=False)

    def create_accrual(self):
        lines = []
        for line in self.lines:
            if line:
                lines.append((0,0,{
                    'item_id':line.item_id.id,
                    'qty':line.qty,
                    'price':line.price,
                }))
                line.construction_line_id.write({'item_select':False})
        self.env['aqar.accrual'].create({'date':self.date,'lines':lines,'construction_id':self.construction_id.id,
                                         'partner_id':self.partner_id.id,
                                         'building_id':self.construction_id.building_id.id
                                         })




class create_accrual_lines(models.TransientModel):
    _name = 'wiz.create.accrual.lines'
    wiz_id=fields.Many2one(string='Item',required=True,comodel_name='wiz.create.accrual')
    construction_line_id=fields.Many2one(comodel_name='aqar.construction.line')
    item_id=fields.Many2one(string='Item',required=True,comodel_name='product.product')
    qty=fields.Float(string='Quantity',required=False,readonly=False)
    price=fields.Float(string='Price',required=False,readonly=False)