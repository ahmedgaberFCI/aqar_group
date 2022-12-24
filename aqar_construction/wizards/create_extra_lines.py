# -*- coding: utf-8 -*-
from odoo import api, fields, models



class create_extra(models.TransientModel):
    _name = 'wiz.create.extra'
    construction_id = fields.Many2one(string='Construction', copy=False, required=False, readonly=False,
                                      comodel_name='aqar.construction')
    lines = fields.One2many(
        comodel_name='wiz.create.extra.lines',
        inverse_name='wiz_id',
        string='Lines',
        required=False)

    def create_line(self):
        for line in self.lines:
            self.env['aqar.construction.line'].create({
                    'is_extra':True,
                    'item_select':line.item_select,
                    'item_id':line.item_id.id,
                    'planned_qty':line.planned_qty,
                    'planned_price':line.planned_price,
                    'construction_id':self.construction_id.id,
                })



class create_extra_lines(models.TransientModel):
    _name = 'wiz.create.extra.lines'
    wiz_id=fields.Many2one(string='Item',required=True,comodel_name='wiz.create.extra')
    item_select = fields.Boolean(string='Select', required=False, readonly=False)
    item_id=fields.Many2one(string='Item',required=True,comodel_name='product.product')
    planned_qty = fields.Float(string='Planned  Quantity', required=False, readonly=False)
    planned_price = fields.Float(string='Planned Price', required=False, readonly=False)
