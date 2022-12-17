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


class CreateManualPayment(models.TransientModel):
    _name = 'wiz.create.manual.payments'

    name = fields.Char('Installment Name', size=64, required=False)
    date = fields.Date(string='Date',required=True)
    duration_month = fields.Integer('Month')
    duration_year = fields.Integer('Year')
    duration = fields.Selection(string="Duration", selection=duration, required=False)

    def add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = int(sourcedate.year + month / 12)
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def create_pay_lines(self):
        contract = self.env['ownership.contract'].browse(self._context.get('active_ids'))
        loan_lines=self.get_lines(contract)
        contract.write({'loan_line':loan_lines})



    def get_lines(self,contract):
        ind = 1
        pricing = contract.pricing
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
            loan_lines.append((0, 0, {'number': ind, 'journal_id': int(self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.income_journal')),'amount': loan_amount, 'date': first_date, 'name': self.name or ''}))
            ind += 1
            first_date = self.add_months(first_date, repetition)
            m += repetition
        return loan_lines

