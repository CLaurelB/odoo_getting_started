from odoo import api, fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate properties types"
    _order = "sequence,name desc"

    name = fields.Char(required = True)
    
    _sql_constraints = [
        ('unique_type', 'UNIQUE(name)',
         'The type must be unique.'),
    ]    
    
    property_ids = fields.One2many("estate.property","property_type_id", string = "Properties")
    
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")

    offer_ids = fields.One2many("estate.property.offer","property_type_id", string = "Offers")

    offer_count = fields.Integer(compute = "_count_offers")

    @api.depends("offer_ids")
    def _count_offers(self):
        for record in self:
            if len(record.offer_ids)!=0:
                record.offer_count = len(record.offer_ids)
            else:
                record.offer_count = 0
