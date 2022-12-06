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
from odoo.exceptions import ValidationError
from odoo import api, fields, models, tools, _

class building(models.Model):
    _name = "building"
    _description = "Building"
    _inherit = ['mail.thread']

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('building')
        new_id = super(building, self).create(vals)
        return new_id

    attach_line= fields.One2many("building.attachment.line", "building_attach_id", "Documents")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    region_id= fields.Many2one('regions','Region', )
    account_income= fields.Many2one('account.account','Income Account', )
    account_analytic_id= fields.Many2one('account.analytic.account', 'Analytic Account')
    active= fields.Boolean ('Active', help="If the active field is set to False, it will allow you to hide the top without removing it.",default=True)
    alarm= fields.Boolean ('Alarm')
    old_building= fields.Boolean ('Old Property')
    constructed= fields.Date ('Construction Date')
    no_of_floors= fields.Integer ('# Floors')
    props_per_floors= fields.Integer ('# Unit per Floor')
    category= fields.Char    ('Category', size=16)
    description= fields.Text    ('Description')
    floor= fields.Char    ('Floor', size=16)
    pricing= fields.Integer   ('Net Price',compute='_calc_price',store=True)
    balcony= fields.Integer   ('Balconies m²',)
    building_area= fields.Float   ('Property Area m²',)
    land_area= fields.Float   ('Land Area m²',)
    price_per_m= fields.Float   ('Price Per m²',)
    price_before_discount= fields.Float   ('Price',compute='_calc_price',store=True)
    discount_type= fields.Selection([('percentage','Percentage'),('amount','Amount')])
    discount= fields.Float('Dsicount')
    garden= fields.Integer   ('Garden m²',)
    terrace= fields.Integer   ('Terraces m²',)
    garage= fields.Integer ('Garage included')
    carport= fields.Integer ('Carport included')
    parking_place_rentable= fields.Boolean ('Parking rentable', help="Parking rentable in the location if available")
    handicap= fields.Boolean ('Handicap Accessible')
    heating= fields.Selection([('unknown','unknown'),
                                           ('none','none'),
                                           ('tiled_stove', 'tiled stove'),
                                           ('stove', 'stove'),
                                           ('central','central heating'),
                                           ('self_contained_central','self-contained central heating')], 'Heating')
    heating_source= fields.Selection([('unknown','unknown'),
                                           ('electricity','Electricity'),
                                           ('wood','Wood'),
                                           ('pellets','Pellets'),
                                           ('oil','Oil'),
                                           ('gas','Gas'),
                                           ('district','District Heating')], 'Heating Source')
    internet= fields.Boolean ('Internet')
    lease_target= fields.Integer   ('Target Lease', )
    lift= fields.Integer ('# Passenger Elevators')
    lift_f= fields.Integer ('# Freight Elevators')
    name= fields.Char    ('Name', size=64, required=True)
    code= fields.Char    ('Code', size=16)
    note= fields.Html    ('Notes')
    note_sales= fields.Text    ('Note Sales Folder')
    partner_id= fields.Many2one('res.partner','Owner', )
    type= fields.Many2one('building.type','Property Type', )
    floor_type= fields.Many2one('floor.type','Floor Type', )
    status= fields.Many2one('building.status','Property Status', )
    purchase_date= fields.Date    ('Purchase Date')
    launch_date= fields.Date    ('Launching Date')
    rooms= fields.Char    ('Rooms', size=32 )
    solar_electric= fields.Boolean ('Solar Electric System')
    solar_heating= fields.Boolean ('Solar Heating System')
    staircase= fields.Char    ('Staircase', size=8)
    surface= fields.Integer   ('Surface')
    telephon= fields.Boolean ('Telephon')
    tv_cable= fields.Boolean ('Cable TV')
    tv_sat= fields.Boolean ('SAT TV')
    usage= fields.Selection([('unlimited','unlimited'),
                                          ('office','Office'),
                                           ('shop','Shop'),
                                           ('flat','Flat'),
                                            ('rural','Rural Property'),
                                           ('parking','Parking')], 'Usage')
    sort= fields.Integer ('Sort')
    sequence= fields.Integer ('Sequ.')
    air_condition= fields.Selection([('unknown','Unknown'),
                                           ('central','Central'),
                                           ('partial','Partial'),
                                           ('none', 'None'),
                                           ], 'Air Condition' )
    address= fields.Char    ('Address')
    license_code= fields.Char    ('License Code', size=16)
    license_date= fields.Date    ('License Date')
    date_added= fields.Date    ('Date Added to Notarization')
    license_location= fields.Char    ('License Notarization')
    electricity_meter= fields.Char    ('Electricity meter', size=16)
    water_meter= fields.Char    ('Water meter', size=16)
    north= fields.Char    ('Northen border by:')
    south= fields.Char    ('Southern border by:')
    east= fields.Char    ('Eastern border  by: ')
    west= fields.Char    ('Western border by: ')
    unit_ids= fields.Many2many('product.template', string='Properties')
    property_floor_plan_image_ids = fields.One2many('floor.plans', 'building_id', string="Floor Plans", copy=True)
    building_image_ids = fields.One2many('building.images', 'building_id', string="Building Images", copy=True)
    street = fields.Char(related='region_id.street',store=True)
    street2 = fields.Char(related='region_id.street2',store=True)
    zip = fields.Char(related='region_id.zip',store=True)
    city = fields.Char(related='region_id.city',store=True)
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               related='region_id.state_id',store=True)
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',related='region_id.country_id',store=True)
    country_code = fields.Char(related='country_id.code', string="Country Code",store=True)


    @api.depends('price_per_m','discount_type','discount','building_area')
    def _calc_price(self):
        for rec in self:
            rec.price_before_discount=rec.price_per_m*rec.building_area
            if rec.discount_type=='amount':
                rec.pricing=rec.price_before_discount-rec.discount
            elif rec.discount_type=='percentage':
                rec.pricing = rec.price_before_discount - ((rec.discount/100)*rec.price_before_discount)
            else:
                rec.pricing=rec.price_before_discount

    def action_create_units(self):
        property_pool = self.env['product.template']
        props=[]
        if self.no_of_floors and self.props_per_floors:
            i=1
            no=1
            while i<=self.no_of_floors:
                j=1
                while j<=self.props_per_floors:
                    print("D>>D",self.code+'-'+str(i)+'-'+str(no))
                    vals={
                        'name':self.code+'-'+str(i)+'-'+str(no),
                        'code':self.code+'-'+str(i)+'-'+str(no),
                        'building_id':self.id,
                        'floor':str(i),
                        'is_property': True,
                        'pricing': self.pricing,
                    }
                    prop_id= property_pool.create(vals)
                    props.append(prop_id.id)
                    j+=1
                    no+=1
                i+=1

            self.unit_ids=[(6, 0, props)]
        else:
            raise ValidationError(
                _("Please set valid number for number of floors and units per floor"))

    _sql_constraints = [
        ('unique_building_code', 'UNIQUE (code,region_id)', 'Building code must be unique!'),
    ]


class building_attachment_line(models.Model):
    _name = 'building.attachment.line'

    name= fields.Char    ('Name', required=True)
    file= fields.Binary    ('File',)
    building_attach_id= fields.Many2one('building', '',ondelete='cascade', readonly=True)
