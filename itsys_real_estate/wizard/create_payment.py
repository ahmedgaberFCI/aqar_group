# -*- coding: utf-8 -*-
from odoo import api, fields, models
import calendar
from odoo import api, fields, models
from datetime import datetime, date,timedelta as td

duration=[
    ('type1','سنوي'),
    ('type2','ربع سنوي'),
    ('type3','نصف سنوي'),
    ('type4','شهري'),
]

types=[
    ('inst', 'قسط'),
    ('maintenance','وديعة صيانة'),
    ('club','تصرفات عقارية'),
    ('garage','تشطبات'),
    ('elevator','تآمين آعمال'),
    ('other','مرافق')
]

class CreateManualPayment(models.TransientModel):
    _name = 'wiz.create.manual.payments'

    name = fields.Char('Installment Name', size=64, required=False)

    date = fields.Date(string='Date',required=True)
    duration_month = fields.Integer('Month')
    duration_year = fields.Integer('Year')
    duration = fields.Selection(string="Duration", selection=duration, required=False)
    type = fields.Selection(string="Type", selection=types, required=True)
    amount_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')],)
    amount = fields.Float(string='amount', digits='Product Price')


    def add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = int(sourcedate.year + month / 12)
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def create_pay_lines(self):
        contract = self.env['ownership.contract'].browse(self._context.get('active_ids'))
        loan_lines=self.get_lines(contract)
        # contract.loan_line2=[(5, 0, 0)]
        contract.loan_line2=loan_lines
        contract.onchange_tmpl()



    def get_lines(self,contract):
        ind = 1
        if self.type=='inst':
            pricing = contract.pricing
            pricing -= contract.advance_payment
        else:
            if self.amount_type=='percentage':
                pricing= ( contract.pricing) * (self.amount / 100)
            else:
                pricing = self.amount
        mon = self.duration_month
        yr = self.duration_year
        first_date = self.date
        loan_lines = []
        repetition=1
        if self.duration=='type1':
            repetition = 12
        if self.duration=='type2':
            repetition = 3
        if self.duration=='type3':
            repetition = 6
        if self.duration=='type4':
            repetition = 1


        if mon > 12:
            x = mon / 12
            mon = (x * 12) + mon % 12
        mons = mon + (yr * 12)
        loan_amount = (pricing / float(mons)) * repetition
        m = 0
        while m < mons:

            if self.type=='inst':
                loan_lines.append((0, 0, {'number': ind,'add_amount':True, 'manaul':True,
                                          'journal_id': int(self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.income_journal')),
                                          'amount': loan_amount, 'date': first_date, 'name': self.name or ''}))
            if self.type == 'maintenance':
                loan_lines.append((0, 0, {'number': ind, 'add_amount': True, 'manaul': True, 'journal_id': int(
                    self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.maintenance_journal')),
                                          'amount': loan_amount, 'date': first_date, 'name': self.name or 'وديعة صيانة'}))
            if self.type == 'club':
                loan_lines.append((0, 0, {'number': ind, 'add_amount': True, 'manaul': True, 'journal_id': int(
                    self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.club_journal')),
                                          'amount': loan_amount, 'date': first_date, 'name': self.name or 'تصرفات عقارية'}))
            if self.type == 'garage':
                loan_lines.append((0, 0, {'number': ind, 'add_amount': True, 'manaul': True, 'journal_id': int(
                    self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.garage_journal')),
                                          'amount': loan_amount, 'date': first_date, 'name': self.name or 'تشطبات'}))
            if self.type == 'elevator':
                loan_lines.append((0, 0, {'number': ind, 'add_amount': True, 'manaul': True, 'journal_id': int(
                    self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.elevator_journal')),
                                          'amount': loan_amount, 'date': first_date, 'name': self.name or 'تآمين آعمال'}))
            if self.type == 'other':
                loan_lines.append((0, 0, {'number': ind, 'add_amount': True, 'manaul': True, 'journal_id': int(
                    self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.other_journal')),
                                          'amount': loan_amount, 'date': first_date, 'name': self.name or 'مرافق'}))

            ind += 1
            first_date = self.add_months(first_date, repetition)
            m += repetition
        print("D>D>D",loan_lines)
        return loan_lines

