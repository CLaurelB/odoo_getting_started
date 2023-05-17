from odoo import api, fields, models, exceptions
import datetime

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate properties offers"
    _order = "price desc"
    
    price = fields.Float(string = "Price")
    status = fields.Selection(copy = False,selection=[('accepted','Accepted'), ('refused','Refused')], readonly = True)
    partner_id = fields.Many2one("res.partner", string="Partner", required = True) 
    property_id = fields.Many2one("estate.property", string="Property", required = True) 
    
    validity = fields.Integer(default="7",string = "Validity (days)")
    date_deadline = fields.Date(compute="_compute_deadline", inverse = "_inverse_deadline", string = "Deadline", store=True)
    
    create_date = fields.Date(default=lambda self: fields.Datetime.now())
    
    property_state = fields.Selection(related = 'property_id.state', store = True)
    
    @api.depends("create_date","validity")
    def _compute_deadline(self):
        for record in self:
            record.date_deadline = record.create_date + datetime.timedelta(days=record.validity)
    
    def _inverse_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - record.create_date).days
    
    
    def action_accept(self):
        if self.property_id.state =='sold':
            raise exceptions.UserError("Property sold.")
        if "accepted" in self.property_id.mapped('offer_ids.status'):
            raise exceptions.UserError("There must be only one accepted proposal")
        self.write({'status':'accepted'})
        self.property_id.buyer_id = self.partner_id
        self.property_id.selling_price = self.price
        self.property_id.state = 'accepted'
        return True
        
        
    def action_refuse(self):
        if self.property_id.state =='sold':
            raise exceptions.UserError("Property sold.")
        self.write({'status':'refused'})
        if  "accepted" not in self.property_id.mapped('offer_ids.status'):
            self.property_id.selling_price = '0'
            self.property_id.state = 'offered'
        return True
        
    _sql_constraints = [
        ('positive_offer_price', 'CHECK(price >= 0)',
         'The offer price must be positive.')
    ]    

    property_type_id = fields.Many2one(related = "property_id.property_type_id", store=True)

    @api.model
    def create(self, vals):
        property = self.env['estate.property'].browse(vals['property_id'])
        if vals['price'] <= property.best_price :
            raise exceptions.UserError("The offer must be higher than "+ str(property.best_price))
        else:
            return super(EstatePropertyOffer, self).create(vals)