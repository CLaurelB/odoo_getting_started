from odoo import _, api, fields, models, exceptions, tools


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate properties"
    _order = "id desc"
    
    name = fields.Char(required = True,default="Unknown", string = "Title")
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy = False, default=lambda self: fields.Datetime.end_of(fields.Datetime.now(),'quarter'), string="Available From") #not copy when duplicating #default in 3 months
    expected_price = fields.Float(required = True)
    selling_price = fields.Float(readonly = True, copy = False) #read_only #not copy when duplicating
    bedrooms = fields.Integer(default = '2') #default number 2
    living_area = fields.Integer(string= "Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(string='Garden Orientation',
        selection=[('north','North'), ('south','South'), ('east','East'), ('west','West')],
        help="Orientation of the garden")
        
    active = fields.Boolean(default = True)
    state = fields.Selection(string='Status',
        selection=[('new','New'), ('offered','Offer received'),('accepted','Offer accepted'), ('sold','Sold'),('canceled','Canceled')],
        help="Estado",
        required=True,
        default = 'new',readonly = True)
        
    property_type_id = fields.Many2one("estate.property.type", string ="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer", readonly = True)
    seller_id = fields.Many2one("res.users", string="Salesman") 
    tag_ids = fields.Many2many("estate.property.tag")
    offer_ids = fields.One2many("estate.property.offer","property_id", string = "Offers",
                                states={"sold": [("readonly", True)]})
    
    total_area = fields.Integer(compute = "_compute_total_area" , string="Total Area (sqm)", store=True)
    
    @api.depends("living_area","garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
            
    best_price = fields.Float(compute="_compute_max_price", string = "Best Offer", store=True)
    
    @api.depends("offer_ids.price")
    def _compute_max_price(self):
        for record in self:
            if len(record.offer_ids)!=0:
                record.best_price = max(record.offer_ids.mapped("price"))
                record.state = 'offered'
            else:
                record.best_price = '0'
                #record.state = 'N'
                
    @api.onchange("garden")
    def onchange_garden(self):
        if self.garden == True:
            self.garden_area = '10'
            self.garden_orientation = 'north'           
            return {'warning': {
                'title': _("Warning"),
                'message': ('Garden area and Garden ortientation set to default values')}}
        else:
            self.garden_area = None
            self.garden_orientation = None          
            return {'warning': {
                'title': _("Warning"),
                'message': ('Garden area and Garden ortientation values reset')}}
    
    
    def sold(self):
        for record in self:
            if record.state == 'canceled':
                raise exceptions.UserError("Canceled properties cannot be sold.")
            elif record.state == 'new':
                raise exceptions.UserError("Can't sell without receiving and accepting an offer.")      
            elif record.state == 'offered':
                raise exceptions.UserError("Can't sell without accepting an offer.")                
            else:
                record.state = "sold"
        return True
        
    def cancel(self):
        for record in self:
            if record.state == 'sold':
                raise exceptions.UserError("Sold properties cannot be canceled.")
            else:
                record.state = "canceled"
        return True
        
    _sql_constraints = [
        ('positive_expected_price', 'CHECK(expected_price >= 0)',
         'The expected price must be positive.'),
         ('positive_selling_price', 'CHECK(selling_price >= 0)',
         'The selling price must be positive.')
    ]
    
    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            if tools.float_utils.float_compare(record.selling_price, 0.9*record.expected_price,2)<0 and not tools.float_utils.float_is_zero(record.selling_price,2):
                raise exceptions.ValidationError(r"The selling price cannot be lower than 90% of the expected price.")
    
    @api.ondelete(at_uninstall=False)
    def _delete_property(self):
        for record in self:
            if not (record.state == 'new' or record.state =='canceled'):
                raise exceptions.UserError("Only new and canceled properties can be deleted.")