from odoo import api, fields, models,_
from datetime import datetime
class aqar_construction(models.Model):
	_name='aqar.construction'

	project_id=fields.Many2one(string='Project',required=True,readonly=False,comodel_name='project.project')
	project_code=fields.Char(string='Project Code',related='project_id.project_code',store=True)
	lines=fields.One2many(string='Lines',required=False,readonly=False, comodel_name='aqar.construction.line',inverse_name="construction_id")
	state=fields.Selection(string='Status',selection=[('draft','Draft'),('approve','Approved'),('confirmed','Confirmed')],default='draft')

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
		return {
			'name': _('Create Accrual'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'wiz.create.accrual',
			'view_id': self.env.ref('aqar_construction.create_accrual_form').id,
			'type': 'ir.actions.act_window',
			'context': {
				'default_construction_id': self.id,
				'default_lines': lines,
			},
			'target': 'new'
		}
	def action_extra_lines(self):
		lines=[]
		for line in self.lines:
			if line.item_select:
				lines.append((0,0,{
					'item_id':line.item_id.id,
				}))
		return {
			'name': _('Create Accrual'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'wiz.create.extra',
			'view_id': self.env.ref('aqar_construction.create_extra_lines_form').id,
			'type': 'ir.actions.act_window',
			'context': {
				'default_construction_id': self.id,
			},
			'target': 'new'
		}



class aqar_construction_line(models.Model):
	_name='aqar.construction.line'
	item_select=fields.Boolean(string='Select',required=False,readonly=False)
	is_extra=fields.Boolean(string='Is Extra',required=False,readonly=True)
	item_id=fields.Many2one(string='Item',required=True,comodel_name='product.product')
	planned_qty=fields.Float(string='Planned  Quantity',required=False,readonly=False)
	planned_price=fields.Float(string='Planned Price',required=False,readonly=False)
	actual_qty=fields.Float(string='Actual Quantity',compute='_calc_actual_qty',store=False,readonly=True)
	actual_price=fields.Float(string='Actual Price',compute='_calc_actual_qty',store=False,readonly=True)
	prec_in_qty=fields.Float(string='Percentage  In Quantity',compute='_calc_prec_in_qty',store=True)
	prec_in_price=fields.Float(string='Percentage  In Price',compute='_calc_prec_in_qty',store=True)
	construction_id=fields.Many2one(string='Construction',comodel_name='aqar.construction')
	state=fields.Selection(string='Status',related='construction_id.state',store=True)

	def _calc_actual_qty(self):
		for rec in self:
			accrual_lines=self.env['aqar.accrual.line'].search([('accrual_id.construction_id','=',rec.construction_id.id)])
			actual_qty=actual_price=0
			for line in accrual_lines:
				if line.item_id==rec.item_id:
					actual_qty+=line.qty
					actual_price+=line.price
			rec.actual_qty=actual_qty
			rec.actual_price=actual_price


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