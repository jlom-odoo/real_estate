from odoo import api, fields, models, _


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"
    _order = "sequence"

    _sql_constraints = [("name_uniq", "UNIQUE(name)", "A type with this name already exists!")]

    sequence = fields.Integer(default=1, help="Order of property types. Lower appears first.")
    name = fields.Char(required=True)
    property_ids = fields.One2many(comodel_name="estate.property", inverse_name="property_type_id")
    offer_ids = fields.One2many(comodel_name="estate.property.offer", inverse_name="property_type_id")
    offer_count = fields.Integer(compute="_compute_offer_count")

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for offer in self:
            offer.offer_count = len(offer.offer_ids)

    def action_open_offer_ids(self):
        self.ensure_one()
        return {
            "name": _("Offers"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "estate.property.offer",
            # "target": "current",
            "domain": [("property_type_id", "=", self.id)],
            "context": {"default_property_type_id": self.id},
        }
