from odoo import api, fields, models
from datetime import datetime
class aqar_construction(models.Model):
	_name='aqar.construction'

	project_id=fields.Many2one(string='Project',required=True,readonly=False,comodel_name='project.project')
	project_code=fields.Char(string='Project Code',related='project_id.project_code',store=True)
	lines=fields.One2many(string='Lines',required=False,readonly=False, comodel_name='aqar.construction.line',inverse_name="construction_id")
	state=fields.Selection(string='Status',selection=[('draft','Draft'),('approve','Approved'),('confirmed','Confirmed')],default='draft')
	accrual_id=fields.Many2one(string='Accrual',copy=False,required=False,readonly=False,comodel_name='aqar.accrual')

	def action_approve(self):
		self.state='approve'

	def action_confirm(self):
		self.state='confirmed'

	def action_create_accrual(self):
		lines=[]
		for line in self.lines:
			if line.item_select:
				lines.append((0,0,{
					'item_id':line.item_id.id,
				}))
		self.accrual_id=self.env['aqar.accrual'].create({'date':datetime.now().date(),'lines':lines})


class aqar_construction_line(models.Model):
	_name='aqar.construction.line'
	item_select=fields.Boolean(string='Select',required=False,readonly=False)
	item_id=fields.Many2one(string='Item',required=True,comodel_name='product.product')
	planned_qty=fields.Float(string='Planned  Quantity',required=False,readonly=False)
	planned_price=fields.Float(string='Planned Price',required=False,readonly=False)
	actual_qty=fields.Float(string='Actual Quantity',compute='_calc_actual_qty',store=True)
	actual_price=fields.Float(string='Actual Price',compute='_calc_actual_qty',store=True)
	prec_in_qty=fields.Float(string='Percentage  In Quantity',compute='_calc_prec_in_qty',store=True)
	prec_in_price=fields.Float(string='Percentage  In Price',compute='_calc_prec_in_qty',store=True)
	construction_id=fields.Many2one(string='Construction',comodel_name='aqar.construction')
	accrual_id=fields.Many2one(string='Accrual',related='construction_id.accrual_id',comodel_name='aqar.accrual')


	@api.depends('accrual_id.lines')
	def _calc_actual_qty(self):
		for rec in self:
			rec.actual_qty=sum(rec.accrual_id.lines.filtered(lambda ll:ll.item_id==rec.item_id).mapped('qty'))
			rec.actual_price=sum(rec.accrual_id.lines.filtered(lambda ll:ll.item_id==rec.item_id).mapped('price'))


	@api.depends('planned_qty', 'planned_price','actual_qty','actual_price')
	def _calc_prec_in_qty(self):
		for rec in self:
			rec.prec_in_qty = rec.actual_qty / (rec.planned_qty or 1)
			rec.prec_in_price = rec.actual_price / (rec.planned_price or 1)

	notes=fields.Text(string='Notes',required=False,readonly=False)





class Project(models.Model):
	_inherit='project.project'
	project_code = fields.Char(
	    string='Project Code',
	    required=False)