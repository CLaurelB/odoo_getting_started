from odoo import models, exceptions, Command,fields

class EstateProperty(models.Model):
    _inherit = "estate.property"
    property_type_id = fields.Many2one(string ="Property Types", required=True)
        
    def sold(self):
        print("////////////Hola///////////////")
        #raise exceptions.UserError("Modulo sobreescrito.")
        import pdb; pdb.set_trace()
        result = super().sold()
        
        self.env["account.move"].create(
            {'partner_id':super().buyer_id.id,
             'move_type':'out_invoice',
             'invoice_line_ids':[
                 Command.create({
                     'name':super().name,
                     'quantity':1,
                     'price_unit':super().selling_price
                      }),
                 Command.create({
                     'name':'6%',
                      'quantity':1,
                      'price_unit':super().selling_price*0.06
                      }),
                 Command.create({     
                     'name':'administrative fees',
                     'quantity':1,
                     'price_unit':100.00
                     })
             ]
             })

        return result