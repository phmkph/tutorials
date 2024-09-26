from odoo import fields, models, api, _ #_ - это модуль для переводов строк на разные языки
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import random
import pdb #python debugger

class EstateProperty(models.Model):
	_name = "estate.property"
	_description = "descibes real estate objects"
	_order = "id desc"
	active = fields.Boolean (default = True)
	
	name = fields.Char('Property\'s name', required = True)
	description = fields.Text('Brief description of an object')
	state = fields.Selection(
		string='State of the contract on this property',
		selection=[('new', 'New'), ('offer_recieved', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold '), ('canceled', 'Canceled')],
		help="Indictes current state of the contract on this property",
		copy = False,
		required = True,
		default = 'new')
	postcode = fields.Char('Postal code', help = 'Postal code for a corresponding adress')
	date_availability = fields.Date(copy = False,default = fields.Datetime.today()+ relativedelta(months=3))
	expected_price = fields.Float(required = True)
	selling_price = fields.Float(readonly  = True, copy = False)
	bedrooms = fields.Integer('Number of bedrooms',default=2)
	living_area = fields.Integer()
	facades = fields.Integer()
	garage = fields.Boolean()
	garden = fields.Boolean()
	garden_area = fields.Integer(help = 'full m2')
	garden_orientation = fields.Selection(
		string='Garden orientation',
		selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
		help="How garden is oriented by cardinal directions")
	property_type_id = fields.Many2one("estate.property.type", string = "Property type")
	partner_id = fields.Many2one("res.partner", string="Buyer", copy = False)
	salesman_id = fields.Many2one("res.users", string="Salesperson", default = lambda self: self.env.user)
	tag_ids = fields.Many2many("estate.property.tag", string="Tags")
	offer_ids = fields.One2many("estate.property.offer", "property_id", string="Partner offers")
	total = fields.Float('Total area (m2)', compute="_compute_total", readonly = True, copy = False)
	best_price = fields.Float('Best Offer', compute="_compute_best_price_mapped", readonly = True, copy = False)
	
	_sql_constraints = [
		('check_expected_price', 'CHECK(expected_price > 0)',
		'A property expected price must be strictly positive.')
	]

	@api.ondelete(at_uninstall=False)
	def _check_status(self):
		# pdb.set_trace()  # Ставим точку останова
		if any(rec.state != 'new' and rec.state != 'canceled' for rec in self):
			raise UserError("Can't delete property if its state is not ‘New’ or ‘Canceled’!")
		
	#максимум вычисляется циклом, написана только для целей тестирования 
	@api.depends('offer_ids')
	def _compute_best_price(self):
		best_price = 0;
		for rec in self:
			for offer in rec.offer_ids:
				if offer.price > best_price:
					best_price = offer.price;
			if best_price > 0:
				rec.best_price = best_price

	@api.depends('offer_ids')
	def _compute_best_price_mapped(self):
		for rec in self:
			offer_prices = rec.offer_ids.mapped('price')#извлекаем список цен из офферов
			#Если список offer_prices пустой, то код if amount_totals else 0
			#предотвратит ошибку исполнения max() и установит max_price в 0
			max_price = max(offer_prices) if offer_prices else 0
			rec.best_price = max_price

	@api.depends('living_area','garden_area')
	def _compute_total(self):
		for record in self:
			record.total = record.living_area + record.garden_area
	
	@api.onchange('garden')
	def _onchange_garden(self):
		if not self.garden:
			self.update({'garden_area': None})  # Make it readonly by setting it conditionally
			self.update({'garden_orientation': None})
		else:
			self.garden_area = 10
			self.garden_orientation = 'north' 

	def action_sold(self):
		for record in self:
			if not (record.state == "canceled"):
				record.state = "sold"
			else:
				raise UserError(_('Property status is \'Canceled\' - this type of property can\'t be sold'))
		return True

	def action_canceled(self):
		for record in self:
			if (record.state != "canceled"):
				record.state = "canceled"
			else:
				raise UserError(_('Property status has already been set to \'Canceled\''))
		return True
	
	@api.constrains('selling_price','expected_price')
	def _check_best_price(self):
		for record in self:
			if not float_is_zero(record.selling_price, 6): 
				minimum_price = record.expected_price * 0.9
				pdb.set_trace()
				print(f"90% of expected price: {minimum_price}")
				print(f"Selling price: {record.selling_price}")
				result = float_compare(record.selling_price, minimum_price, 6)
				print(f"Comparison result: {result}")
				if result == -1:
					raise ValidationError("Selling price cannot be lower than 90% of the expected price")
		# all records passed the test, don't return anything

	def test_call(self):
		for rec in self:
			print("test_call FROM EstateProperty")
		return True

class EstatePropertyType(models.Model):
	_name = "estate.property.type"
	_description = "describes all real estate property types we will be using"
	_order = "name"
	
	name = fields.Char('Type of a property', required = True)
	property_ids = fields.One2many("estate.property","property_type_id", readonly = True)
	sequence = fields.Integer('Sequence', default=1, help="Used to order property types.")
	offer_ids = fields.One2many("estate.property.offer","property_type_id", readonly = True)
	offer_count = fields.Integer('Offer count', compute="_compute_total", readonly = True, copy = False)
	
	@api.depends('offer_ids')
	def _compute_total(self):
		for record in self:
			record.offer_count = len(record.offer_ids)

class EstatePropertyTag(models.Model):
	_name = "estate.property.tag"
	_description = "short string describing common properties of an object"
	_order = "name"
	
	def _get_default_color(self):
		return random.randint(1, 25)
	
	name = fields.Char('Tag name', required = True)
	color = fields.Integer(string='Color', default=_get_default_color)
	
	_sql_constraints = [
		('check_name', 'UNIQUE(name)',
		'A property tag name name must be unique')
	]

class EstatePropertyOffer(models.Model):
	_name = "estate.property.offer"
	_description = "property offer is an amount a potential buyer offers to the seller"
	_order = "price desc"
	
	price = fields.Float()
	status = fields.Selection(
		selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
		copy = False)
	partner_id = fields.Many2one("res.partner", string="Partner", required = True)
	property_id = fields.Many2one("estate.property", string="Property", required = True)
	validity = fields.Integer('Validity (days)', default = 7)
	date_deadline = fields.Date('Deadline', copy = False, compute="_compute_date_deadline", inverse = "_inverse_date_deadline")
	property_type_id = fields.Many2one(related="property_id.property_type_id", store = True)
	
	@api.model
	def create(self, vals):
		prop_recordset = self.env['estate.property'].browse(vals['property_id'])
		if prop_recordset.exists():
			offer_prices = prop_recordset.offer_ids.mapped('price')#извлекаем список цен из офферов
			min_price = min(offer_prices) if offer_prices else 0
			#pdb.set_trace()
			if (vals['price'] == 0 or vals['price'] < min_price): 
				raise UserError(_('Can\'t create an offer with a lower price than an already existing offer'))
			created_offer = super(EstatePropertyOffer, self).create(vals)
			if created_offer.property_id:
				created_offer.property_id.state = 'offer_recieved'
			return created_offer
			#return super(EstatePropertyOffer, self).create(vals)
			#print('Offer created')
	
	@api.depends('validity')
	def _compute_date_deadline(self):
		for record in self:
			if not isinstance(record.create_date, datetime):
				default = fields.Datetime.today()
				record.date_deadline = default + relativedelta(days=record.validity)
			else:
				record.date_deadline = record.create_date + relativedelta(days=record.validity)

	def _inverse_date_deadline(self):
		for record in self:
			if not isinstance(record.create_date, datetime):
				default = fields.Datetime.today().date()
			else:
				default = record.create_date.date()
			
			delta = record.date_deadline - default
			if delta.days > 0:  
				record.validity = delta.days
			else:
				record.validity = 0

	def me_decorator(func):
		def property_has_no_acc_offers(self):
			answ = False
			for offer in self.property_id.offer_ids:
				if (offer.status == "accepted"):
					answ = True
					break
			if not answ:
				func(self)
			else:
				raise UserError(_('This property already has \'Accepted\' offer!'))
				return True
		return property_has_no_acc_offers

	@me_decorator
	def action_accept(self):
		for record in self:
			record.status = "accepted"
			record.property_id.selling_price = record.price
			record.property_id.partner_id = record.partner_id
		return True

	def action_refuse(self):
		for record in self:
			record.status = "refused"
			record.property_id.partner_id = None
			record.property_id.selling_price = 0
		return True