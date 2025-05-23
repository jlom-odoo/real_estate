from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"
    _order = "price desc"

    _sql_constraints = [
        ("check_price", "CHECK(price > 0)", "The offer price must be greater than 0!"),
    ]

    price = fields.Float()
    state = fields.Selection([
        ("accepted", "Accepted"),
        ("refused", "Refused"),
    ], string="Status", copy=False)
    validity = fields.Integer(string="Validity (days)", default=7)
    deadline_date = fields.Date(compute="_compute_deadline_date", inverse="_inverse_deadline_date")
    partner_id = fields.Many2one(comodel_name="res.partner", required=True)
    property_id = fields.Many2one(comodel_name="estate.property", required=True)
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)

    @api.depends("validity")
    def _compute_deadline_date(self):
        for offer in self:
            offer.deadline_date = fields.Date.add(offer.create_date or fields.Date.today(), days=offer.validity)

    def _inverse_deadline_date(self):
        for offer in self:
            create_date = fields.Date.to_date(offer.create_date)
            offer.validity = (offer.deadline_date - create_date).days

    def action_accept(self):
        for offer in self:
            offer_property = offer.property_id
            if offer_property.offer_ids.filtered(lambda o: o.state == "accepted"):
                raise UserError(_("Property '%s' already has an accepted offer!", offer_property.name))
            offer.state = "accepted"
            offer_property.selling_price = offer.price
            offer_property.buyer_id = offer.partner_id
            offer_property.state = "offer_accepted"
        return True
    
    def action_refuse(self):
        for offer in self:
            offer.state = "refused"
        return True
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property_id = self.env["estate.property"].browse(vals["property_id"])
            offer_ids = property_id.offer_ids
            if offer_ids and vals["price"] < max(offer_ids.mapped("price"), default=0):
                raise UserError("A new offer can't have a lower price than the highest current offer")
            elif not offer_ids:
                property_id.write({"state": "offer_received"})
        return super().create(vals_list)
