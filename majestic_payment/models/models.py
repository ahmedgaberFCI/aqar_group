# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools.misc import formatLang, format_date, get_lang
from num2words import num2words


class InheritPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'Inherit Payment'

    is_expense = fields.Boolean(string="Send To", )
    account_expense = fields.Many2one("account.account", string="Account", required=False, domain="[('account_type', 'in', ('asset_receivable', 'liability_payable'))]")
    national_id = fields.Char(string="National Id", required=False, )
    anly_world = fields.Char(string="فقط لا غير", required=False, )
    label = fields.Char(string="Label", required=False, )
    is_other = fields.Boolean(string="Receive From", )
    other_account = fields.Many2one(comodel_name="account.account", string="Account Credit", required=False, domain="[('account_type', 'in', ('asset_receivable', 'liability_payable'))]")
    is_check = fields.Boolean(string="Is Check", )
    check_number = fields.Char(string="Check Number", required=False, )
    due_date = fields.Date(string="Due Date", required=False, )



    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer', 'is_expense', 'account_expense',
                 'is_other', 'other_account')
    def _compute_destination_account_id(self):
        self.destination_account_id = False
        for pay in self:
            if pay.is_expense:
                pay.destination_account_id = pay.account_expense
            elif pay.is_other:
                pay.destination_account_id = pay.other_account

            else:
                if pay.is_internal_transfer:
                    # pay.destination_account_id = pay.journal_id.company_id.transfer_account_id
                    pay.destination_account_id = pay.destination_journal_id.company_id.transfer_account_id

                elif pay.partner_type == 'customer':

                    if pay.partner_id:
                        pay.destination_account_id = pay.partner_id.with_company(
                            pay.company_id).property_account_receivable_id
                    else:
                        pay.destination_account_id = self.env['account.account'].search([
                            ('company_id', '=', pay.company_id.id),
                            ('account_type', '=', 'asset_receivable'),
                            ('deprecated', '=', False),
                        ], limit=1)
                    # Receive money from invoice or send money to refund it.

                    # if pay.partner_id:
                    #     pay.destination_account_id = pay.partner_id.with_company(
                    #         pay.company_id).property_account_receivable_id
                    # else:
                    #     pay.destination_account_id = self.env['account.account'].search([
                    #         ('company_id', '=', pay.company_id.id),
                    #         ('internal_type', '=', 'asset_receivable'),
                    #         ('deprecated', '=', False),
                    #     ], limit=1)


                elif pay.partner_type == 'supplier':
                    if pay.partner_id:
                        pay.destination_account_id = pay.partner_id.with_company(
                            pay.company_id).property_account_payable_id
                    else:
                        pay.destination_account_id = self.env['account.account'].search([
                            ('company_id', '=', pay.company_id.id),
                            ('account_type', '=', 'liability_payable'),
                            ('deprecated', '=', False),
                        ], limit=1)
                    # Send money to pay a bill or receive money to refund it.

                    # if pay.partner_id:
                    #     pay.destination_account_id = pay.partner_id.with_company(
                    #         pay.company_id).property_account_payable_id
                    # else:
                    #     pay.destination_account_id = self.env['account.account'].search([
                    #         ('company_id', '=', pay.company_id.id),
                    #         ('internal_type', '=', 'liability_payable'),
                    #         ('deprecated', '=', False),
                    #     ], limit=1)

    def amount_to_text(self):
        convert_amount_in_words = num2words(abs(self.amount), lang='ar')
        return convert_amount_in_words

    def _seek_for_lines(self):
        ''' Helper used to dispatch the journal items between:
        - The lines using the temporary liquidity account.
        - The lines using the counterpart account.
        - The lines being the write-off lines.
        :return: (liquidity_lines, counterpart_lines, writeoff_lines)
        '''
        self.ensure_one()

        liquidity_lines = self.env['account.move.line']
        counterpart_lines = self.env['account.move.line']
        writeoff_lines = self.env['account.move.line']

        for line in self.move_id.line_ids:
            print("S>>>>>>>>>>...", line.account_id.account_type)

            if line.account_id in self._get_valid_liquidity_accounts():
                liquidity_lines += line
            elif line.account_id.account_type in (
                    'asset_receivable', 'liability_payable', 'income_other') or line.partner_id == line.company_id.partner_id:
                counterpart_lines += line
            else:
                writeoff_lines += line

        return liquidity_lines, counterpart_lines, writeoff_lines

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        if not self.outstanding_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set either on the company or the %s payment method in the %s journal.",
                self.payment_method_line_id.name, self.journal_id.display_name))

        # Compute amounts.
        write_off_amount_currency = write_off_line_vals.get('amount', 0.0)

        if self.payment_type == 'inbound':
            # Receive money.
            liquidity_amount_currency = self.amount
        elif self.payment_type == 'outbound':
            # Send money.
            liquidity_amount_currency = -self.amount
            write_off_amount_currency *= -1
        else:
            liquidity_amount_currency = write_off_amount_currency = 0.0

        write_off_balance = self.currency_id._convert(
            write_off_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        liquidity_balance = self.currency_id._convert(
            liquidity_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
        counterpart_balance = -liquidity_balance - write_off_balance
        currency_id = self.currency_id.id

        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.journal_id.name)
            else:  # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        else:
            liquidity_line_name = self.payment_reference

        # Compute a default label to set on the journal items.

        payment_display_name = {
            'outbound-customer': _("Customer Reimbursement"),
            'inbound-customer': _("Customer Payment"),
            'outbound-supplier': _("Vendor Payment"),
            'inbound-supplier': _("Vendor Reimbursement"),
        }

        default_line_name = self.env['account.move.line']._get_default_line_name(
            _("Internal Transfer") if self.is_internal_transfer else payment_display_name[
                '%s-%s' % (self.payment_type, self.partner_type)],
            self.amount,
            self.currency_id,
            self.date,
            partner=self.partner_id,
        )

        if self.is_expense:
            line_vals_list = [
                # Liquidity line.
                {
                    'name': self.label,
                    'date_maturity': self.date,
                    'currency_id': currency_id,
                    'credit': abs(counterpart_balance),
                    'debit': 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.outstanding_account_id.id,
                },
                # Receivable / Payable.
                {
                    'name': self.label,
                    'date_maturity': self.date,
                    'currency_id': currency_id,
                    'debit': abs(liquidity_balance),
                    'credit': 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.account_expense.id,
                },
            ]
        elif self.is_other:
            line_vals_list = [
                # Liquidity line.
                {
                    'name': self.label,
                    'date_maturity': self.date,
                    'currency_id': currency_id,
                    'debit': abs(counterpart_balance),
                    'credit': 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.outstanding_account_id.id,
                },
                # Receivable / Payable.
                {
                    'name': self.label,
                    'date_maturity': self.date,
                    'currency_id': currency_id,
                    'credit': abs(liquidity_balance),
                    'debit': 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.other_account.id,
                },
            ]
        else:
            line_vals_list = [
                # Liquidity line.
                {
                    'name': liquidity_line_name or default_line_name,
                    'date_maturity': self.date,
                    'amount_currency': liquidity_amount_currency,
                    'currency_id': currency_id,
                    'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                    'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.outstanding_account_id.id,
                },
                # Receivable / Payable.
                {
                    'name': self.payment_reference or default_line_name,
                    'date_maturity': self.date,
                    'amount_currency': counterpart_amount_currency,
                    'currency_id': currency_id,
                    'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                    'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.destination_account_id.id,
                },
            ]
        if not self.currency_id.is_zero(write_off_amount_currency):
            # Write-off line.
            line_vals_list.append({
                'name': write_off_line_vals.get('name') or default_line_name,
                'amount_currency': write_off_amount_currency,
                'currency_id': currency_id,
                'debit': write_off_balance if write_off_balance > 0.0 else 0.0,
                'credit': -write_off_balance if write_off_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': write_off_line_vals.get('account_id'),
            })
        print("D>", line_vals_list)
        return line_vals_list

    def print_payment_receipt(self):
        return self.env.ref('majestic_payment.action_payment_receipt_report').report_action(self, data={}, config=False)



class AccountMoveLine(models.Model):
    _inherit='account.move.line'

    @api.model
    def _get_default_line_name(self, document, amount, currency, date, partner=None):
        ''' Helper to construct a default label to set on journal items.

        E.g. Vendor Reimbursement $ 1,555.00 - Azure Interior - 05/14/2020.

        :param document:    A string representing the type of the document.
        :param amount:      The document's amount.
        :param currency:    The document's currency.
        :param date:        The document's date.
        :param partner:     The optional partner.
        :return:            A string.
        '''
        values = ['%s %s' % (document, formatLang(self.env, amount, currency_obj=currency))]
        if partner:
            values.append(partner.display_name)
        values.append(format_date(self.env, fields.Date.to_string(date)))
        return ' - '.join(values)

class AccountMove(models.Model):
    _inherit='account.move'
    check_number = fields.Char(string="Check Number",compute='_calc_check_number',store=True )
    due_date = fields.Date(string="Due Date", required=False,compute='_calc_check_number',store=True )

    @api.depends('payment_id')
    def _calc_check_number(self):
        for rec in self:
            if rec.check_number:
                rec.check_number = rec.payment_id.check_number
            if rec.due_date:
                rec.due_date = rec.payment_id.due_date

