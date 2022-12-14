# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models 

class building_type(models.Model):
    _name = "building.type"
    _description = "Building Type"
    
    name= fields.Char ('Type')
    land_ratio= fields.Float   ('Load Ratio',)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
class Floor_type(models.Model):
    _name = "floor.type"
    _description = "Building Type"

    name= fields.Char ('Floor Type')
