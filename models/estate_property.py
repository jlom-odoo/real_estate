from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Property"
    _order = "id desc"

    _sql_constraints = [
        ("check_expected_price", "CHECK(expected_price > 0)", "The expected price must be greater than 0!"),
        ("check_selling_price", "CHECK(selling_price >= 0)", "The selling price can't be less than 0!"),
    ]

    name = fields.Char(required=True)
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
    tag_ids = fields.Many2many(comodel_name="estate.property.tag", string="Property Tags")
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
    salesperson_id = fields.Many2one(comodel_name="res.users", ondelete="restrict", 
                                     default=lambda self: self.env.user)
    
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

    def action_sold(self):
        if self.filtered(lambda p: p.state == "canceled"):
            raise UserError(_("A canceled property can not be sold!"))
        self.filtered(lambda p: p.state != "sold").write({"state": "sold"})
        return True
    
    def action_cancel(self):
        if self.filtered(lambda p: p.state == "sold"):
            raise UserError(_("A sold property can not be canceled!"))
        self.filtered(lambda p: p.state != "canceled").write({"state": "canceled"})
        return True
    
    @api.constrains("selling_price", "expected_price", "state")
    def _check_selling_price(self):
        for property in self.filtered(lambda p: p.state == "offer_accepted"):
            if float_compare(
                    property.selling_price, property.expected_price * 0.9, precision_digits=2) == -1:
                raise ValidationError(_("The selling price can't be lower than 90% of the expected price!"))
            
    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        if any(p.state not in ["new", "canceled"] for p in self):
            raise UserError(_("Properties can only be deleted when status is 'New' or 'Canceled'"))
