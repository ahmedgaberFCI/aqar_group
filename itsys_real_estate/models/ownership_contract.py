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
from datetime import datetime, timedelta
import time
import calendar
from odoo import api, fields, models
from odoo.tools.translate import _
from datetime import datetime, date,timedelta as td
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class ownership_contract(models.Model):
    _name = "ownership.contract"
    _description = "Ownership Contract"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _entry_count(self):
        move_obj = self.env['account.move']
        move_ids = move_obj.search([('ownership_id', 'in', self.ids)])
        self.entry_count = len(move_ids)

    def view_entries(self):
        entries=[]
        entry_obj = self.env['account.move']
        entry_ids = entry_obj.search([('ownership_id', 'in', self.ids)])
        for obj in entry_ids: entries.append(obj.id)

        return {
            'name': _('Journal Entries'),
            'domain': [('id', 'in', entries)],
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'account.move',
            'type':'ir.actions.act_window',
            'nodestroy':True,
            'view_id': False,
            'target':'current',
        }

    @api.depends('loan_line.amount','loan_line.amount_residual')
    def _check_amounts(self):
        total_paid = 0
        total_nonpaid = 0
        amount_total= 0
        amount_total2= 0
        for rec in self:
            for line in rec.loan_line:
                if line.add_amount:
                    amount_total2+= line.amount
                amount_total+= line.amount
                total_nonpaid+= line.amount_residual
                total_paid+= (line.amount-line.amount_residual)

        self.paid = total_paid
        self.balance = total_nonpaid
        self.amount_total=amount_total
        self.amount_total2=amount_total2


    def _voucher_count(self):
        voucher_obj = self.env['account.payment']
        voucher_ids = voucher_obj.search([('ownership_line_id.loan_id', 'in', self.ids)])
        self.voucher_count = len(voucher_ids)

    def _default_income_account(self):
        account_income= self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.income_account')
        return int(account_income)

    attach_line= fields.One2many("own.attachment.line", "own_contract_id_att", "Documents")
    entry_count= fields.Integer('Entry Count',compute='_entry_count')

    paid= fields.Float(compute='_check_amounts', string='Paid',)
    balance= fields.Float(compute='_check_amounts', string='Balance',)
    amount_total= fields.Float(compute='_check_amounts', string='Total',)
    amount_total2= fields.Float(compute='_check_amounts', string='Total',)
    #ownership_contract Info
    name= fields.Char    ('Name', size=64,readonly=True)
    reservation_id=  fields.Many2one('unit.reservation','Reservation')
    date= fields.Date    ('Date',required=True, default=fields.Date.context_today)
    date_payment= fields.Date    ('First Payment Date')
    #Building Info
    building= fields.Many2one('building','Building', copy=False)
    no_of_floors= fields.Integer ('# Floors')
    building_code= fields.Char    ('Code', size=16)
    #Building Unit Info
    building_unit= fields.Many2one('product.template','Building Unit', copy=False,domain=[('is_property', '=', True),('state', '=', 'free')],required=True)
    unit_code= fields.Char    ('Code', size=16)
    floor= fields.Char    ('Floor', size=16)
    address= fields.Char    ('Address')
    origin= fields.Char    ('Source Document')
    pricing= fields.Integer   ('Price', required=True, digits='Product Price')
    template_id= fields.Many2one('installment.template','Payment Template',)
    type= fields.Many2one('building.type','Building Unit Type')
    status= fields.Many2one('building.status','Building Unit Status')
    user_id= fields.Many2one('res.users','Responsible', default=lambda self: self.env.user,)
    partner_id= fields.Many2one('res.partner','Customer',required=True)
    building_area= fields.Integer ('Building Unit Area m²',)
    loan_line= fields.One2many('loan.line.rs.own', 'loan_id')
    loan_line2= fields.One2many('loan.line.rs.own', 'loan_id2')
    region= fields.Many2one('regions','Region')
    state= fields.Selection([('draft','Draft'),
                             ('confirmed','Confirmed'),
                             ('cancel','Canceled'),
                             ], 'State' , default='draft')
    voucher_count= fields.Integer('Voucher Count',compute='_voucher_count')
    account_income= fields.Many2one('account.account','Income Account', default=_default_income_account,required=False)
    account_analytic_id= fields.Many2one('account.analytic.account', 'Analytic Account')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    maintenance = fields.Float(string='وديعة صيانة', digits='Product Price')
    date_maintenance= fields.Date('تاريخ وديعة صيانة')
    maintenance_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')],)
    maintenance_installment = fields.Boolean(string=' Installment',)

    club = fields.Float(string='تصرفات عقارية', digits='Product Price')
    date_club= fields.Date('تاريخ تصرفات عقارية ')
    club_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')],)
    club_installment = fields.Boolean(string=' Installment',)

    garage = fields.Float(string='تشطبات', digits='Product Price')
    date_garage= fields.Date('تاريخ تشطبات')
    garage_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')],)
    garage_installment = fields.Boolean(string=' Installment',)

    elevator = fields.Float(string='تآمين آعمال', digits='Product Price')
    date_elevator= fields.Date(' تاريخ تآمين آعمال')
    elevator_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')],)
    elevator_installment = fields.Boolean(string=' Installment',)

    other = fields.Float(string='مرافق', digits='Product Price')
    date_other= fields.Date(' تاريخ مرافق')
    other_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')],)
    other_installment = fields.Boolean(string=' Installment',)

    deposit = fields.Float('Deposit', digits=(16, 2), )
    advance_payment_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')],
                                            'Advance Payment Type')

    advance_payment = fields.Float('Advance Payment Value', )
    advance_payment_date = fields.Date(' Advance Payment Date')
    advance_payment_journal_id = fields.Many2one('account.journal', string='Advance Payment Journal')
    advance_payment_payment_id = fields.Many2one('account.payment', string='Advance Payment ')
    commission_moves= fields.Integer(compute='_calc_commission_moves', string='Commission Moves')

    @api.constrains('loan_line','pricing')
    def check_loan_line(self):
        for rec in self:
            if rec.amount_total2>rec.pricing:
                raise ValidationError("الاقساط آكبر من سعر الوحدة")


    def _calc_commission_moves(self):
        moves = self.env['account.move'].search([('commission_reservation_id', '=', self.id)])
        self.commission_moves = len(moves)

    def open_commission_moves(self):
        action = self.env.ref('account.action_move_journal_line')
        result = action.read()[0]
        result['domain'] = [('commission_reservation_id', '=', self.id)]
        return result






    def action_receive_deposit(self):
        if not self.advance_payment_journal_id:
            raise UserError(_('Please set the Advance Payment Journal!'))
        if not self.advance_payment_date:
            raise UserError(_('Please set the Advance Payment Date!'))
        pricing = self.pricing
        custom_adv_payment = self.advance_payment if self.advance_payment_type == 'amount' else (
                    pricing * (self.advance_payment / 100))
        rec=self.env['account.payment'].create({
            'payment_type':'inbound',
            'partner_type':'customer',
            'amount':custom_adv_payment,
            'partner_id':self.partner_id.id,
            'date':self.advance_payment_date,
        })
        rec.action_post()
        self.advance_payment_payment_id=rec.id


    def unlink(self):
        if self.state !='draft':
            raise UserError(_('You can not delete a contract not in draft state'))
        super(ownership_contract, self).unlink()

    def view_vouchers(self):
        vouchers=[]
        voucher_obj = self.env['account.payment']
        voucher_ids = voucher_obj.search([('ownership_line_id.loan_id', 'in', self.ids)])
        for obj in voucher_ids: vouchers.append(obj.id)

        return {
            'name': _('Receipts'),
            'domain': [('id', 'in', vouchers)],
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'account.payment',
            'type':'ir.actions.act_window',
            'nodestroy':True,
            'view_id': False,
            'target':'current',
        }

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('ownership.contract')
        new_id = super(ownership_contract, self).create(vals)
        return new_id

    def unit_status(self):
        return self.building_unit.state

    def action_confirm(self):
        unit = self.building_unit
        unit.write({'state': 'sold'})
        self.write({'state':'confirmed'})
        for line in self.loan_line:
            line.make_invoice()
        # self.generate_entries()

    def action_cancel(self):
        unit = self.building_unit
        unit.write({'state':  'free'})
        self.write({'state':'cancel'})
        for line in self.loan_line:
            line.invoice_id.button_draft()
            line.invoice_id.button_cancel()
        # self.generate_cancel_entries()

    @api.onchange('region')
    def onchange_region(self):
        if self.region:
            building_ids = self.env['building'].search([('region_id', '=', self.region.id)])
            buildings=[]
            for u in building_ids: buildings.append(u.id)
            return {'domain': {'building': [('id', 'in', buildings)]}}

    @api.onchange('building')
    def onchange_building(self):
        if self.building:
            units = self.env['product.template'].search([('is_property', '=', True),('building_id', '=', self.building.id),('state','=','free')])
            unit_ids=[]
            for u in units: unit_ids.append(u.id)
            building_obj = self.env['building'].browse(self.building.id)
            code =  building_obj.code
            no_of_floors =  building_obj.no_of_floors
            region =  building_obj.region_id.id
            account_analytic_id= building_obj.account_analytic_id.id
            if building_obj:
                self.building_code= code
                self.region=region
                self.no_of_floors=no_of_floors
                self.account_analytic_id=account_analytic_id

                return {'domain': {'building_unit': [('id', 'in', unit_ids)]}}

    @api.onchange('template_id','date_payment','pricing','date_maintenance','date_club','date_garage',
                  'date_elevator','date_other',
                  'advance_payment','advance_payment_type')
    def onchange_tmpl(self):
        if self.template_id or 1==1:
            self.loan_line=[(5, 0, 0)]
            loan_lines=self._prepare_lines(self.date_payment)
            self.loan_line= loan_lines

    def add_months(self,sourcedate,months):
        month = sourcedate.month - 1 + months
        year = int(sourcedate.year + month / 12 )
        month = month % 12 + 1
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])
        return date(year,month,day)

    @api.onchange('building_unit')
    def onchange_unit(self):
        self.unit_code=self.building_unit.code
        self.floor=self.building_unit.floor
        self.pricing=self.building_unit.pricing
        self.type=self.building_unit.ptype
        self.address=self.building_unit.address
        self.status=self.building_unit.status
        self.building_area=self.building_unit.building_area
        self.building = self.building_unit.building_id.id
        self.region = self.building_unit.region_id.id

    @api.onchange('reservation_id')
    def onchange_reservation(self):
        self.building =  self.reservation_id.building.id
        self.region =  self.reservation_id.region.id
        self.building_code =  self.reservation_id.building_code
        self.partner_id =  self.reservation_id.partner_id.id
        self.building_unit =  self.reservation_id.building_unit.id
        self.unit_code =  self.reservation_id.unit_code
        self.address =  self.reservation_id.address
        self.floor =  self.reservation_id.floor
        self.building_unit =  self.reservation_id.building_unit.id
        self.pricing =  self.reservation_id.pricing
        self.date_payment =  self.reservation_id.date_payment
        self.template_id =  self.reservation_id.template_id.id
        self.type =  self.reservation_id.type
        self.status =  self.reservation_id.status
        self.building_area =  self.reservation_id.building_area
        if self.template_id or 1==1:
            self.loan_line = [(5, 0, 0)]
            loan_lines=self._prepare_lines(self.date_payment)
            self.loan_line= loan_lines

    def create_move(self,rec,debit,credit,move,account):
        move_line_obj = self.env['account.move.line']
        move_line_obj.create({
            'name': rec.name,
            'partner_id': rec.partner_id.id,
            'account_id': account,
            'debit': debit,
            'credit': credit,
            'move_id': move,
        })
    def generate_entries(self):
        journal_pool = self.env['account.journal']
        journal = journal_pool.search([('type', '=', 'sale')], limit=1)
        if not journal:
            raise UserError(_('Please set sales accounting journal!'))
        account_move_obj = self.env['account.move']
        total = 0
        for rec in self:
            if not rec.partner_id.property_account_receivable_id:
                raise UserError(_('Please set receivable account for partner!'))
            if not rec.account_income:
                raise UserError(_('Please set income account for this contract!'))

            for line in rec.loan_line:
                total+=line.amount
            account_move_obj.create({'ref' : rec.name, 'journal_id' : journal.id,'ownership_id':rec.id,
                                     'line_ids':[(0,0,{ 'name': rec.name,
                                                        'partner_id': rec.partner_id.id,
                                                        'account_id': rec.partner_id.property_account_receivable_id.id,'debit': total,
                                                        'credit': 0.0}),
                                                 (0,0,{'name': rec.name,
                                                       'partner_id': rec.partner_id.id,
                                                       'account_id': rec.account_income.id, 'debit': 0.0,
                                                       'credit': total})
                                                 ]})

    def generate_cancel_entries(self):
        journal_pool = self.env['account.journal']
        journal = journal_pool.search([('type', '=', 'sale')], limit=1)
        if not journal:
            raise UserError(_('Please set sales accounting journal!'))
        total = 0
        for rec in self:
            if not rec.partner_id.property_account_receivable_id:
                raise UserError(_('Please set receivable account for partner!'))
            if not rec.account_income:
                raise UserError(_('Please set income account for this contract!'))

            for line in rec.loan_line:
                total+=line.amount

        account_move_obj = self.env['account.move']
        move_id = account_move_obj.create({'ref': self.name,'ownership_id':rec.id,
                                           'journal_id': journal.id,
                                           'line_ids': [(0, 0, {'name': self.name,
                                                                'account_id': rec.partner_id.property_account_receivable_id.id,
                                                                'debit': 0.0,
                                                                'credit': total}),
                                                        (0, 0, {'name': self.name,
                                                                'account_id': rec.account_income.id,
                                                                'debit': total,
                                                                'credit': 0.0})
                                                        ]
                                           })
        return move_id

    def _prepare_lines(self,first_date):
        self.loan_line = [(5, 0, 0)]
        loan_lines=[]
        for line in self.loan_line2:
            loan_lines.append((0,0,
                               {'number': line.number,'add_amount':line.add_amount, 'manaul': True, 'journal_id': line.journal_id.id, 'amount': line.amount, 'date': line.date,
                                'name': line.name}
                               ))

        if self.template_id or 1==1:
            ind=len(self.loan_line) or 1
            pricing = self.pricing
            custom_adv_payment=self.advance_payment if self.advance_payment_type=='amount' else (pricing*(self.advance_payment/100))
            if custom_adv_payment>0:
                pricing -= custom_adv_payment
                loan_lines.append((0, 0, {'number': ind,'add_amount':True, 'journal_id': self.env['ir.config_parameter'].sudo().get_param(
                    'itsys_real_estate.income_journal'), 'amount': custom_adv_payment, 'date': first_date,
                                          'name': _('دفعة التعاقد')}))
                ind += 1

            mon = self.template_id.duration_month
            yr = self.template_id.duration_year
            repetition = self.template_id.repetition_rate
            advance_percent = self.template_id.adv_payment_rate
            deduct = self.template_id.deduct
            if not first_date:
                raise UserError(_('Please select first payment date!'))
            adv_payment=pricing*float(advance_percent)/100
            if self.template_id:
                if mon>12:
                    x = mon/12
                    mon=(x*12)+mon%12
                mons=mon+(yr*12)
                if adv_payment:
                    loan_lines.append((0,0,{'number':ind,'add_amount':True,'journal_id':int(self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.income_journal')),'amount':adv_payment,'date': first_date, 'name':_('Advance Payment')}))
                    ind+=1
                    if deduct:
                        pricing-=adv_payment
                loan_amount=(pricing/float(mons))*repetition
                m=0
                while m<mons:
                    loan_lines.append((0,0,{'number':ind,'add_amount':True,'journal_id':int(self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.income_journal')),
                                            'amount':loan_amount,'date': first_date,'name':_('Loan Installment')}))
                    ind+=1
                    first_date = self.add_months(first_date, repetition)
                    m+=repetition
            if self.club:
                if self.club_installment==False:
                    loan_lines.append((0,0,{'number':ind,'journal_id':int(self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.club_journal')),
                                            'amount':(self.club if self.club_type=='amount' else (self.pricing)*(self.club/100) / float(mons)) * repetition,'date': self.date_club,'name':_('تصرفات عقارية')}))
                    ind += 1
                else:
                    if self.template_id:
                        _m = 0
                        _first_date=self.date_club
                        _amount = ((self.club if self.club_type=='amount' else (self.pricing)*(self.club/100)) / float(mons)) * repetition
                        while _m < mons:
                            loan_lines.append((0, 0, {'number': ind, 'journal_id': int(
                                self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.club_journal')),
                                                      'amount':_amount, 'date':  _first_date, 'name':_('تصرفات عقارية')}))
                            ind += 1
                            _first_date = self.add_months(_first_date, repetition)
                            _m += repetition

            if self.maintenance:
                if self.maintenance_installment==False:
                    loan_lines.append((0,0,{'number':ind,'journal_id':int(self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.maintenance_journal')),'amount':self.maintenance if self.maintenance_type=='amount' else (self.pricing)*(self.maintenance/100),'date': self.date_maintenance,'name':_('وديعة صيانة')}))
                    ind += 1
                else:
                    if self.template_id:
                        _m = 0
                        _first_date = self.date_maintenance
                        _amount = ((self.maintenance if self.maintenance_type == 'amount' else (self.pricing) * (self.maintenance / 100)) / float(mons)) * repetition
                        while _m < mons:
                            loan_lines.append((0, 0, {'number': ind, 'journal_id': int(
                                self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.maintenance_journal')),
                                                      'amount':_amount ,
                                                      'date':_first_date, 'name': _('وديعة صيانة')}))

                            ind += 1
                            _first_date = self.add_months(_first_date, repetition)
                            _m += repetition

            if self.garage:
                if self.garage_installment==False:
                    loan_lines.append((0,0,{'number':ind,'journal_id':int(self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.garage_journal')),'amount':self.garage if self.garage_type=='amount' else (self.pricing)*(self.garage/100),'date': self.date_garage,'name':_('تشطبات')}))
                    ind += 1
                else:
                    if self.template_id:
                        _m = 0
                        _first_date = self.date_garage
                        _amount = ((self.garage if self.garage_type == 'amount' else (self.pricing) * (self.garage / 100)) / float(mons)) * repetition
                        while _m < mons:
                            loan_lines.append((0, 0, {'number': ind, 'journal_id': int(
                                self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.garage_journal')),
                                                      'amount': _amount,
                                                      'date': _first_date, 'name': _('تشطبات')}))

                            ind += 1
                            _first_date = self.add_months(_first_date, repetition)
                            _m += repetition

            if self.elevator:
                if self.elevator_installment==False:
                    loan_lines.append((0,0,{'number':ind,'journal_id':int(self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.elevator_journal')),'amount':self.elevator if self.elevator_type=='amount' else (self.pricing)*(self.elevator/100),'date': self.date_elevator,'name':_('تآمين آعمال')}))
                    ind += 1
                else:
                    if self.template_id:
                        _m = 0
                        _first_date = self.date_elevator
                        _amount = ((self.elevator if self.elevator_type == 'amount' else ( self.pricing) * (self.elevator / 100)) / float(mons)) * repetition
                        while _m < mons:
                            loan_lines.append((0, 0, {'number': ind, 'journal_id': int(
                                self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.elevator_journal')),
                                                      'amount': _amount,
                                                      'date': _first_date, 'name': _('تآمين آعمال')}))

                            ind += 1
                            _first_date = self.add_months(_first_date, repetition)
                            _m += repetition

            if self.other:
                if self.other_installment==False:
                    loan_lines.append((0,0,{'number':ind,'journal_id':int(self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.other_journal')),'amount':self.other if self.other_type=='amount' else (self.pricing)*(self.other/100),'date': self.date_other,'name':_('مرافق')}))
                    ind+=1
                else:
                    if self.template_id:
                        _m = 0
                        _first_date = self.date_other
                        _amount = (( self.other if self.other_type == 'amount' else ( self.pricing) * (self.other / 100)) / float(mons)) * repetition
                        while _m < mons:
                            loan_lines.append((0, 0, {'number': ind, 'journal_id': int(
                                self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.other_journal')),
                                                      'amount':_amount,
                                                      'date': _first_date, 'name': _('مرافق')}))

                            ind += 1
                            _first_date = self.add_months(_first_date, repetition)
                            _m += repetition

        return loan_lines



class loan_line_rs_own(models.Model):
    _name = 'loan.line.rs.own'
    _order = 'date, name'

    def view_payments(self):
        payments = self.env['account.payment'].sudo().search([('ownership_line_id','=',self.id)]).ids
        return {
            'name': _('Vouchers'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', payments)],
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
        }

    def _count_payment(self):
        for rec in self:
            payments = self.env['account.payment'].sudo().search([('ownership_line_id','=',rec.id)]).ids
            rec.payment_count= len(payments)

    @api.depends('amount','total_paid_amount')
    def _check_amounts(self):
        for rec in self:
            rec.total_remaining_amount = rec.amount - rec.total_paid_amount

    cancelled= fields.Boolean('Cancelled')
    number= fields.Char('Number')

    contract_user_id= fields.Many2one(string='User', related= 'loan_id.user_id', store=True)
    contract_partner_id= fields.Many2one(string='Partner', related= 'loan_id.partner_id', store=True)
    contract_building= fields.Many2one( string="Building", related='loan_id.building', store=True)
    contract_building_unit= fields.Many2one(related='loan_id.building_unit',string="Building Unit", store=True,domain=[('is_property', '=', True)])
    contract_region= fields.Many2one(related='loan_id.region',string="Region", store=True)
    date= fields.Date('Due Date')
    name= fields.Char('Name')
    amount= fields.Float('Payment', digits='Product Price')

    loan_id= fields.Many2one('ownership.contract', '',ondelete='cascade', readonly=True)
    loan_id2= fields.Many2one('ownership.contract', '',ondelete='cascade', readonly=True)
    status= fields.Char('Status')
    company_id= fields.Many2one('res.company', readonly=True,  default=lambda self: self.env.user.company_id.id)

    payment_count= fields.Integer(compute='_count_payment', string='# Counts')

    invoice_id = fields.Many2one('account.move', string='Invoice', )
    journal_id = fields.Many2one('account.journal', string='Journal', )
    payment_state = fields.Selection(related='invoice_id.payment_state', readonly=True,)
    invoice_state = fields.Selection(related='invoice_id.state', readonly=True,)
    amount_residual = fields.Monetary(related='invoice_id.amount_residual', readonly=True,)
    currency_id = fields.Many2one(related='invoice_id.currency_id', readonly=True)
    manaul = fields.Boolean(string='Manaul')
    add_amount = fields.Boolean()

    def send_multiple_installments(self):
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('itsys_real_estate',
                                                         'email_template_installment_notification')[1]
        template_res = self.env['mail.template']
        template = template_res.browse(template_id)
        template.send_mail(self.id, force_send=True)

    def make_invoice(self):
        for rec in self:
            if not rec.loan_id.partner_id.property_account_receivable_id:
                raise UserError(_('Please set receivable account for partner!'))
            # if not rec.loan_id.account_income:
            #     raise UserError(_('Please set income account for this contract!'))
            account_move_obj = self.env['account.move']
            journal_pool = self.env['account.journal']
            journal = rec.journal_id or journal_pool.search([('type', '=', 'sale')], limit=1)

            invoice= account_move_obj.create({'ref': rec.name, 'journal_id': journal.id,
                                     'partner_id': rec.contract_partner_id.id,
                                     'move_type': 'out_invoice', 'ownership_line_id': rec.id,
                                     'invoice_date_due': rec.date,
                                     'ref':(rec.loan_id.name + ' - ' + rec.name),
                                     'invoice_line_ids': [(0, None, {
                                         'name': (rec.loan_id.name + ' - ' + rec.name),
                                         'quantity': 1,
                                         # 'analytic_account_id':rec.loan_id.account_analytic_id.id,
                                         'price_unit': rec.amount, })]
                                     })
            invoice.action_post()
            self.invoice_id= invoice.id

    def view_invoice(self):
        move = self.env['account.move'].sudo().search([('ownership_line_id','=',self.id)])
        return {
            'name': _('Invoice'),
            'view_type': 'form',
            'res_id':move.id,
            'view_mode': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
        }

class accountMove(models.Model):
    _inherit = 'account.move'
    ownership_id= fields.Many2one('ownership.contract', '',ondelete='cascade', readonly=True)

class own_attachment_line(models.Model):
    _name = 'own.attachment.line'

    name= fields.Char    ('Name', required=True)
    file= fields.Binary    ('File',)
    own_contract_id_att= fields.Many2one('ownership.contract', '',ondelete='cascade', readonly=True)