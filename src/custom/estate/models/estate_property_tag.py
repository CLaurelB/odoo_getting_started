from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate properties types"
    _order = "name desc"

    name = fields.Char("Name", required = True)
    
    _sql_constraints = [
        ('unique_tag', 'UNIQUE(name)',
         'The tag must be unique.'),
    ]    

    color = fields.Integer()