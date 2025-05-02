from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag"
    _order = "name"

    _sql_constraints = [("name_uniq", "UNIQUE(name)", "A tag with this name already exists!")]

    name = fields.Char(required=True)
