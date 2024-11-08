from odoo import api, fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"

    price = fields.Float()
    state = fields.Selection([
        ("accepted", "Accepted"),
        ("refused", "Refused"),
    ], string="Status", copy=False)
    partner_id = fields.Many2one(comodel_name="res.partner", required=True)
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    property_id = fields.Many2one(comodel_name="estate.property", required=True)

    @api.depends("validity")
    def _compute_date_deadline(self):
        for offer in self:
            offer.date_deadline = fields.Date.add(offer.create_date or fields.Date.today(), days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            create_date = fields.Date.to_date(offer.create_date)
            offer.validity = (offer.date_deadline - create_date).days

    def action_accept_offer(self):
        self.ensure_one()
        if self.property_id.offer_ids.filtered(lambda o: o.state == "accepted" and o.id != self.id):
            raise UserError("A property can only have one accepted offer")
        
        self.state = "accepted"
        self.property_id.selling_price = self.price
        self.property_id.buyer_id = self.partner_id
    
    def action_refuse_offer(self):
        for record in self:
            record.state = "refused"
