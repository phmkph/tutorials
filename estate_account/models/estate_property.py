from odoo import models, fields, api
from odoo import Command

class EstatePropertyAccounting(models.Model):
	_inherit = "estate.property"
	abacus = fields.Char('This field is inherited from EstateProperty - Accounting')

	def action_sold(self):
		res = super(EstateProperty, self).action_sold()
		print("action_sold from EstatePropertyAccounting")
		return res

	def test_call(self):
		res = super().test_call()
		self.env["account.move"].create(
			{
				"partner_id":self.partner_id.id,
				"move_type":'out_invoice',
				"invoice_line_ids": [
					Command.create({
						"name": "Selling bonus",
						"quantity": 1,
						"price_unit": (self.selling_price * 6) / 100,
					}),
					Command.create({
						"name": "Administrative fees",
						"quantity": 1,
						"price_unit": 100,
					}),
				],
			}
		)
		print("test_call FROM Accounting Estate Property")
		return res

class EA_TestingClass(models.Model):
	_name = 'estate.property.accounting.testclass'
	_description = 'Added to test class visibility in a two model scenario'
	
	name = fields.Char('Test class name', required = True)