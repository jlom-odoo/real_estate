from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Property"

    _sql_constraints = [
        ("expected_price_check", "CHECK(expected_price > 0)", "The expected price must always be greater than 0"),
        ("selling_price_check", "CHECK(selling_price >= 0)", "The selling price can not be less than 0"),
    ]

    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ("new", "New"),
        ("offer_received", "Offer Received"),
        ("offer_accepted", "Offer Accepted"),
        ("sold", "Sold"),
        ("canceled", "Canceled"),
    ], string="Status", copy=False, required=True, default="new")
    property_type_id = fields.Many2one(comodel_name="estate.property.type")
    tag_ids = fields.Many2many(string="Property Tags", comodel_name="estate.property.tag")
    postcode = fields.Char()
    date_availability = fields.Date(
        copy=False, default=lambda self: fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(required=True)
    best_offer = fields.Float(compute="_compute_best_offer")
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([
        ("north", "North"),
        ("south", "South"),
        ("east", "East"),
        ("west", "West"),
    ])
    total_area = fields.Integer(compute="_compute_total_area")
    offer_ids = fields.One2many(comodel_name="estate.property.offer", inverse_name="property_id")
    buyer_id = fields.Many2one(comodel_name="res.partner", ondelete="restrict")
    salesperson_id = fields.Many2one(comodel_name="res.users", ondelete="restrict", default=lambda self: self.env.user)

    @api.constrains("expected_price", "selling_price")
    def _check_selling_price(self):
        for property in self:
            if float_is_zero(property.selling_price, precision_digits=2):
                continue
            if float_compare(property.selling_price, property.expected_price * 0.9, precision_digits=2) < 0:
                raise ValidationError("The selling price of a property can not be less than 90% of its expected price")
    
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for property in self:
            property.total_area = property.living_area + property.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_offer(self):
        for property in self:
            property.best_offer = max(property.offer_ids.mapped("price"), default=0)

    @api.onchange("garden")
    def _onchange_garden(self):
        self.garden_area = self.garden and 10
        self.garden_orientation = self.garden and "north"

    def action_sell_property(self):
        for record in self:
            if record.state == "canceled":
                raise UserError("Canceled properties can not be sold")
            record.state = "sold"

    def action_cancel_property(self):
        for record in self:
            if record.state == "sold":
                raise UserError("Sold properties can not be canceled")
            record.state = "canceled"
