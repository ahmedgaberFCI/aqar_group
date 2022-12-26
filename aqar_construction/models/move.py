from odoo import api, fields, models
class Move(models.Model):
    _inherit='account.move'
    building_id = fields.Many2one(string='Project', required=False, readonly=False, comodel_name='building')
    building_code = fields.Char(string='Project Code', related='building_id.code', store=True)
