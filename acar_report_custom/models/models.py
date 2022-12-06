# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'ResPartner'

    notional_id = fields.Char(string="National_id", required=False, )
    work_address = fields.Char(string="Work Address", required=False, )


