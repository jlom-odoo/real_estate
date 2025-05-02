from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"

    _sql_constraints = [("name_uniq", "UNIQUE(name)", "A type with this name already exists!")]

    name = fields.Char(required=True)
    property_ids = fields.One2many(comodel_name="estate.property", inverse_name="property_type_id")
