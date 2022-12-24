from odoo import api, fields, models
class Move(models.Model):
    _inherit='account.move'
    project_id = fields.Many2one(string='Project', required=True, readonly=True, comodel_name='project.project')
    project_code = fields.Char(string='Project Code', related='project_id.project_code', store=True)