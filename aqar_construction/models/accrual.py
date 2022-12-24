from odoo import api, fields, models



class aqar_accrual(models.Model):
	_name='aqar.accrual'
	partner_id=fields.Many2one(string='Vendor',required=True,readonly=False,comodel_name='project.project')
	bill_id=fields.Many2one(string='Bill',copy=False,required=False,readonly=False,comodel_name='account.move')
	date=fields.Date(string='Date',required=False,readonly=False)
	lines=fields.One2many(string='Lines',required=False,readonly=False, comodel_name='aqar.accrual.line',inverse_name="accrual_id")
	state=fields.Selection(string='Status',selection=[('draft','Draft'),('approve','Approved'),('confirmed','Confirmed')],default='draft')
	construction_id=fields.Many2one(string='Construction',copy=False,required=False,readonly=False,comodel_name='aqar.construction')
	project_id = fields.Many2one(string='Project', required=True, readonly=True, comodel_name='project.project')
	project_code = fields.Char(string='Project Code', related='project_id.project_code', store=True)

	def action_approve(self):
		self.state='approve'

	def action_confirm(self):
		self.state='confirmed'

	def action_create_vendor_bill(self):
		self.bill_id = self.env['account.move'].create({
			'move_type': 'in_invoice',
			'project_id': self.project_id.id,
			'invoice_date':self.date,
			'invoice_date_due':self.date,
			'partner_id': self.partner_id.id,
			'invoice_line_ids': [(0, 0, {'quantity': line.qty,'product_id':line.item_id.id}) for line in self.lines]
		})



class aqar_accrual_lines(models.Model):
	_name='aqar.accrual.line'
	item_id=fields.Many2one(string='Item',required=True,comodel_name='product.product')
	qty=fields.Float(string='Quantity',required=False,readonly=False)
	price=fields.Float(string='Price',required=False,readonly=False)
	total=fields.Float(string='Total',compute='_calc_total',store=True)
	@api.depends('qty','price')
	def _calc_total(self):
		for rec in self:
			rec.total=rec.price*rec.qty


	accrual_id=fields.Many2one(string='accrual',required=False,readonly=False,comodel_name='aqar.accrual')

