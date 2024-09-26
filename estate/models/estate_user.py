from odoo import fields, models, api

class estateUser(models.Model):
	_inherit = "res.users"

	est_memo = fields.Char('Random text')
	property_ids = fields.One2many("estate.property","salesman_id", domain=[('active', '=', 'True')] )