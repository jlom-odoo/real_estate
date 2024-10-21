from odoo import fields, models


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Property"

    name = fields.Char()
    garden_orientation = fields.Selection([
        ("north", "North"),
        ("south", "South"),
        ("east", "East"),
        ("west", "West"),
    ])
