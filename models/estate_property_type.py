from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"
    _order = "sequence"

    _sql_constraints = [("name_uniq", "UNIQUE(name)", "A type with this name already exists!")]

    sequence = fields.Integer(default=1, help="Order of property types. Lower appears first.")
    name = fields.Char(required=True)
    property_ids = fields.One2many(comodel_name="estate.property", inverse_name="property_type_id")
